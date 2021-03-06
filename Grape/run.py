#!/usr/bin/python
#coding:utf8
from flask import Flask, render_template, url_for, request, redirect, make_response, session, abort
import MySQLdb
from flask import jsonify
from config import *
from function import *
import plotly.plotly as py  #easy_install plotly
from xml.sax.saxutils import quoteattr  # transfer ' to \' to escape error in mysql
from plotly.graph_objs import *
import string

from init import initdb

app = Flask(__name__)

py.sign_in('NoListen','ueixigh6gr') # API KEY

app.secret_key = '\xbc\x98B\x95\x0f\x1e\xcdr\xf8\xb0\xc1\x1a\xd3H\xdd\x86T\xff\xfdg\x80\x8b\x95\xf7'

conn = MySQLdb.connect(user=db_config["db_user"],passwd=db_config["db_passwd"],host=db_config["db_host"],db=db_config["db_name"],charset="utf8")

cursor = conn.cursor()

open_event_scheduler ="SET GLOBAL event_scheduler = 1;"
cursor.execute(open_event_scheduler)
conn.commit()
#open the event_scheduler to set time expiration event

@app.route('/init')
def init():
    initdb()
    return "success"

@app.route('/', methods=['GET', 'POST'])
def index():
    islogin = session.get('islogin')
    user_id = session.get('user_id')
    message1 = session.get('message1')
    attendedGroupsList = []
    ownGroupsList = []
    messages = []
    html = 'index.html'
    members = None
    leader = None

    if islogin == '1':
        html = 'index-log.html'
        #get groups
        User1 = User(user_id=user_id)
        username = User1.username
        role = User1.role
        if(role == 1):
            return redirect('/admin')
        attendedGroups, ownGroups = User1.get_groups()
        for i in ownGroups:
            ownGroupsList += [Group(i).get_data()]
        for i in attendedGroups:
            if i not in ownGroups:
                attendedGroupsList += [Group(i).get_data()]
        messages = User1.get_messages()
        if request.method == 'GET':
            #Find group by group_id
            group_id=request.args.get('group_id')
            #print "id from front=", group_id
            if group_id and group_id.isdigit():
            #    Group1=User1.search_group(group_id)
            #    if Group1:
            #        members=Group1.get_members()
            #        leader=Group1.leader_id
            #        print leader, members, 233
                return redirect(url_for('groupDetail', group_id=group_id))

        if request.method == 'POST':
            #del group
            delname=request.form.get('delname')
            if delname:
                User1.delete_group(delname)
            #quit group
            quitname=request.form.get('quitname')
            if quitname:
                User1.quit_group(quitname)
            return make_response(redirect('/'))
    else:
        username = u'请先登录'

    return render_template(html, user_id=user_id, username=username, islogin=islogin,\
                            message1=message1, messages=messages,\
                            attend=attendedGroupsList, own=ownGroupsList, \
                            members=members, leader=leader)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        session.clear()
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        response = make_response(redirect('/'))
        session['islogin'] = '0'
        if(username == '' or password == '' or email == ''):
            session['message1'] = 'fuck!'
            return response
        if password2 == password:
            user = User(name=username, email=email)
            if user.check_e() == 1 or user.check_u() == 1:
                session['message1'] = "User already existed!"
                return response
            result = user.register(password)
            #session['username'] = result['username']
            session['islogin'] = '1'
            session['user_id'] = result['user_id']
            #session['email'] = result['email']
            return response
        else:
            session['message1'] = "Password not the same!"
            return response
    else:
        return render_template('index.html')


@app.route('/_login/', methods=['GET', 'POST'])
def login():
    session.clear()
    email = str(request.args.get('email', 0, type=str))
    password = str(request.args.get('pw', 0, type=str))
    session['islogin'] = '0'
    # print "Come here!"
    if(email == '' or password == ''):
        status = 'Please enter email and password!'
        return jsonify(status=status)
    user = User(email=email)
    state = user.login(password)
    if state == 1:
        data = user.get_data_by_email()
        session['user_id'] = data['user_id']
        session['islogin'] = '1'
        status = 'success'
        return jsonify(status=status)
    if state == 0:
        status = "Wrong password!"
        return jsonify(status=status)
    if state == -1:
        status = "Email not used!"
        return jsonify(status=status)


@app.route('/logout')
def logout():
    session.clear()
    response = make_response(redirect('/'))
    return response


@app.route('/_check_users')
def check_users():
    username = request.args.get('username', 0, type=str)
    user = User(name=username)
    return jsonify(exist=user.check_u())


@app.route('/_check_email')
def check_email():
    email = request.args.get('email', 0, type=str)
    user = User(email=email)
    return jsonify(exist=user.check_e())

#create new group
@app.route('/_new_group')
def new_group():
    user_id = session.get('user_id')
    user = User(user_id=user_id)
    name=request.args.get('name')
    topic=request.args.get('topic')
    confirmMessage=request.args.get('confirm')
    desc=request.args.get('desc', '', type=str)
    if name and topic and confirmMessage:
        if not desc:
            desc="this is my group"
        status=user.create_group(name, topic, desc, confirmMessage)
    elif name == '':
        status = 'name'
    elif topic == '':
        status = 'topic'
    elif confirmMessage == '':
        status = 'confirm message'
    return jsonify(status=status)


@app.route('/_join_group')
def join_group():
    user_id = session.get('user_id')
    group_id = str(request.args.get('group_id', 0, type=int))
    confirm = str(request.args.get('confirm', 0, type=str))
    # group = Group(group_id=group_id)
    user = User(user_id=user_id)
    status=user.join_group(group_id=group_id, confirm=confirm)
    return jsonify(status=status)


@app.route('/_quit_group')
def quit_group():
    user_id = session.get('user_id')
    group_id = str(request.args.get('group_id', 0, type=str))
    # group = Group(group_id=group_id)
    user = User(user_id=user_id)
    status=user.quit_group(group_id=group_id)
    return jsonify(status=status)


@app.route('/_delete_group')
def deleteGroup():
    user_id = session.get('user_id')
    group_id = str(request.args.get('group_id', 0, type=int))
    print "user_id:", session
    user = User(user_id=user_id)
    return jsonify(success=user.delete_group(group_id))


@app.route('/_delete_user')
def delete_user():
    user_id = session.get('user_id')
    user_id_to_be_deleted = str(request.args.get('user_id', 0, type=int))
    admin = Admin(user_id=user_id)
    return jsonify(success=admin.delete_user(user_id_to_be_deleted))


@app.route('/_delete_group_admin')
def delete_group_admin():
    user_id = session.get('user_id')
    group_id = str(request.args.get('group_id', 0, type=int))
    admin = Admin(user_id=user_id)
    return jsonify(success=admin.delete_group(group_id))

@app.route('/_delete_vote')
def delete_vote():
    user_id = session.get('user_id')
    vote_id = str(request.args.get('vote_id', 0, type=int))
    print vote_id,234234
    user = User(user_id=user_id)
    return jsonify(success=user.delete_vote(vote_id))


@app.route('/_end_vote')
def end_vote():
    user_id = session.get('user_id')
    vote_id = str(request.args.get('vote_id', 0, type=int))
    print vote_id,234234
    user = User(user_id=user_id)
    return jsonify(success=user.end_vote(vote_id))

@app.route('/group/')
def myGroups():
    return make_response(redirect('/'))



@app.route('/discussion/dis<int:discuss_id>')
def show_discuss(discuss_id):
    is_login = session.get('islogin')
    if(is_login != '1'):                       #please login first!
        return make_response(redirect('/'))
    user_id = session.get('user_id')
    user = User(user_id=user_id)
    if(user.check_id() == 0):                #user not exist?
        session.clear()
        return make_response(redirect('/'))
    discuss = Discussion(discuss_id=discuss_id)
    group_id = discuss.group_id
    group = Group(group_id=group_id)
    user_dic = {}
    user_dic['member_id'] = user_id
    if(user_dic not in group.get_members()):
        return make_response(redirect('/'))

    user_data = user.get_data_by_id()
    if discuss.exist():
        discuss_data = discuss.get_data()
        reply = discuss.get_reply()
        if group.exist_group():
            creator = User(user_id=discuss.user_id).username
            discuss.increase_read_num()
            group_name = group.name
            members = group.get_members()
            role = '0'
            if({'member_id': user_id} in members):
                role = '1'          # member
            if(str(user_id) == str(group.leader_id)):
                role = '2'          # leader
            return render_template('discussion.html', group_id=group_id,\
                                    discuss=discuss_data,reply=reply,group_name=group_name,\
                                    username=user_data['username'], role=role,\
                                    user_id=user_id, creator=creator)

    abort(404)

@app.route('/_create_discussion/<int:group_id>')
def create_discussion(group_id):
    title = request.args.get('title')
    content = request.args.get('content')
    user_id = session.get('user_id')
    # print "content: ", content
    group = Group(group_id)
    return jsonify(status=group.create_discussion(user_id, title, content))


@app.route('/_delete_discussion')
def deleteDiscussion():
    user_id = session.get('user_id')
    user = User(user_id=user_id)
    discuss_id = str(request.args.get('discuss_id', 0, type=int))
    return jsonify(success=user.delete_discussion(discuss_id))


@app.route('/_reply_discussion/<discuss_id>')
def reply_discussion(discuss_id):
    # discuss_id = request.form.get('discuss_id')
    reply_content = request.args.get('content')
    if(reply_content == ''):
        return jsonify(status='fail')
    user_id = session.get('user_id')
    try:
        # user = User(user_id=user_id)
        # username = user.username
        discuss = Discussion(discuss_id)
        discuss.add_reply(user_id,reply_content.encode('utf8'))
        # html = '/discussion/dis%s' % discuss_id
        return jsonify(status='success')
    except Exception, e:
        print 'reply error:', e
        return jsonify(status='fail')

@app.route('/_delete_reply')
def deleteReply():
    user_id = session.get('user_id')
    user = User(user_id=user_id)
    reply_id = str(request.args.get('reply_id', 0, type=int))
    return jsonify(success=user.delete_reply(reply_id))

@app.route('/_message_confirm', methods=['GET'])
def news_confirm():
    user_id = str(request.args.get('user_id', 0, type=int))
    message_id = str(request.args.get('message_id', 0, type=int))
    user = User(user_id = user_id)
    return jsonify(success=user.message_confirm(message_id))

@app.errorhandler(404)
def page_not_found(error):
    user_id = session.get('user_id')
    islogin = session.get('islogin')
    if islogin == '1':
        user = User(user_id=user_id)
        username = user.username
    else:
        username = u'请先登录'
    return render_template('page_not_found.html', user_id=user_id, islogin=islogin, username=username), 404


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    is_login = session.get('islogin')
    if(is_login == '0'):                       #please login first!
        return make_response(redirect('/'))
    user_id = session.get('user_id')
    user = User(user_id=user_id)
    if(user.check_id() == 0):                #user not exist?
        session.clear()
        return make_response(redirect('/'))

    if(user.role!=1):
        abort(404)

    admin1=Admin(user_id=user_id)
    groups=admin1.show_all_groups()
    users=admin1.show_all_users()

    # admin1.delete_user(2)
    # admin1.delete_group(2)


    return render_template('admin.html', username=user.username,\
                           groups=groups,users=users)


@app.route('/group/gp<int:group_id>')
def groupDetail(group_id):
    is_login = session.get('islogin')
    if(is_login == '0'):                       #please login first!
        return make_response(redirect('/'))
    user_id = session.get('user_id')
    user = User(user_id=user_id)
    if(user.check_id() == 0):                #user not exist?
        session.clear()
        return make_response(redirect('/'))
    user_data = user.get_data_by_id()
    #code above checks user data
    group = Group(group_id)
    if(group.exist_group()):
        group_data = group.get_data()
        group_data['leader_name'] = User(user_id=group.leader_id).username

        discussions = group.get_discussions()
        votes_list_voting = group.get_votes_voting()
        votes_list_end = group.get_votes_expired()
        bulletin = group.get_bulletin()
        members = group.get_members()
        news = group.get_news(user_id)

        memberNames=[]
        role = '0'
        for member in members:
            if str(member['member_id']) != str(group.leader_id):
                user=User(user_id=member['member_id'])
                memberNames+=[user.username]

        if {'member_id': user_id} in members :
            role = '1'              #member
        if str(user_id) == str(group.leader_id):
            role = '2'              #leader

        return render_template('group-id.html', group_id=group_id, bulletin=bulletin,\
                                group_data=group_data, discussions=discussions,\
                                votes_list_voting=votes_list_voting, newsList=news,\
                                votes_list_end=votes_list_end,username=user_data['username'],\
                                memberNames=memberNames,memberNum=len(memberNames),user_id=user_id, role=role)
    abort(404)
                           #non-exist

@app.route('/_create_vote/<int:group_id>',methods=['GET','POST'])
def raise_a_vote_result(group_id):  
    user_id = session.get('user_id')
    if request.method == "GET":
        vote_contents_set = []
        options_set = []
        vote_options_set = []
        
        time2end = request.args.get('endtime')
        endtime_selection = request.args.get('endtime-selection')
        print endtime_selection
        if endtime_selection == '0': # date
            title = quoteattr(request.args.get('vote-content'))
            vote_contents_set.append(title)

            vote_options = []
            options = string.atoi(request.args.get('vote-options-num'))

            options_set.append(options)

            for i in range(1,options+1):
                vote_options.append(quoteattr(request.args.get('vote-option-content-%s'% str(i))).encode('utf-8'))

            vote_options_set.append(vote_options)
            time_split = time2end.split(":")
            endtime = "current_timestamp + interval %s hour + interval %s minute + interval %s second" % (time_split[0],time_split[1],time_split[2])

        else:
            title = quoteattr(request.args.get('title'))
            endtime = "'%s'" % time2end
            vote_contents_num = string.atoi(request.args.get('votes-num'))
            print "vote_contents_num:", vote_contents_num
            for i in range(1,vote_contents_num+1):
                vote_contents_set.append(quoteattr(request.args.get('vote-content-%d' % i)))
                options = string.atoi(request.args.get('vote-options-num-%d' % i))
                options_set.append(options)
                vote_options = []

                for j in range(1,options+1):
                    vote_options.append(quoteattr(request.args.get('vote%d-option-content-%s'% (i,str(j))).encode('utf-8')))
                
                vote_options_set.append(vote_options)

        #options = string.atoi(request.args.get('vote-options-num'))
        
        group = Group(group_id)
        group.create_vote(user_id,title,vote_contents_set,endtime_selection,options_set,vote_options_set,endtime)
    return redirect(url_for('groupDetail',group_id=group_id))


@app.route('/vote/voting<vote_id>') #查看正在进行的投票
def vote_operation(vote_id): # use groupid to verify the vote
    user_id = session.get('user_id')
    vote = Vote(vote_id,user_id)
    group = Group(vote.group_id)
    members = group.get_members()
    if {'member_id': user_id} not in members :
        return redirect(url_for('groupDetail', group_id=vote.group_id))
    # ensure the vote has not voted before 
    # if the user change the status to submit it
    # try:
    user = User(user_id=user_id)
    username = user.username
    group_id = vote.group_id
    vote_options_list = vote.vote_options # a list [[]]
    #vote_contents = vote.vote_contents # a list []
    #is_voted = vote.is_voted
   # options_voted = vote.options_voted
    # the option the user has voted for
    #0 means not yet
    return render_template('view_vote-id.html',vote_options_list=vote_options_list,\
                           vote=vote,group=Group(group_id=group_id),\
                           username=username,creator=User(user_id=vote.user_id),\
                           current_path=request.path)
    # except Exception, e:
    #     print e
        # abort(404)

@app.route('/_vote_op/voting<int:vote_id>',methods=['GET','POST']) #进行投票
def vote_operation_result(vote_id):
    if request.method == 'GET':
        # try:
        user_id = session.get('user_id')
        print user_id
        vote_option = request.args.get('vote-option')
        #vote_id = request.args.get('vote-id')
        vote = Vote(vote_id,user_id)
        if vote.is_voted != 0:
            return "You have voted"
        vote_contents_num = vote.contents_num
        vote_options = []
        for i in range(1,vote_contents_num+1):
            vote_options.append(request.args.get('vote%d-option' % i))

        group_id = vote.group_id
        vote.vote_op(user_id,vote_options)
        return redirect(url_for('vote_operation', vote_id=vote_id))
        # except Exception, e:
        #     print e
        #     abort(404)
    return redirect(url_for('vote_operation', vote_id=vote_id))


@app.route('/vote/rs<int:vote_id>',methods=['GET','POST']) #查看已完成的投票
def view_votes_result(vote_id):

    user_id = session.get('user_id')
    user = User(user_id = user_id)
    vote = Vote(vote_id,user_id)
    group = Group(group_id=vote.group_id)
    creator_id = vote.user_id
    creator = User(user_id = creator_id)
    members = group.get_members()
    if {'member_id': user_id} not in members :
        return redirect(url_for('groupDetail', group_id=vote.group_id)) 
    #votes for each option
    #in the form [v1-[op1,op2,op3...],v2-[op1,op2,op3..],[]]
    votes_distribution = vote.votes
    print votes_distribution
    #in the form [v1,v2,v3]
    vote_contents = vote.vote_contents
    #in the form [v1-[op1,op2,op3...],v2-[op1,op2,op3..],[]]
    vote_options = vote.vote_options
    title = vote.title
    vote_options_order = []
    for i in votes_distribution:
        order = [x for x in xrange(1,len(i)+1)]
        vote_options_order.append(order)

    votes_max = []
    # calcualte the max
    for i in votes_distribution:
        votes_max.append(max(i))

    latest=vote.get_recent_voted_record()

    return render_template('votes_static.html', user=user, creator=creator, group=group,\
                            vote=vote, votes_max=votes_max, title=title,latest=latest,\
                            vote_options_order = vote_options_order, vote_options = vote_options,\
                            vote_contents = vote_contents, votes_distribution = votes_distribution)

@app.route('/_create_bulletin/<int:group_id>')
def create_bulletin(group_id):
    title = request.args.get('title')
    text = request.args.get('text')
    user_id = session.get('user_id')
    group = Group(group_id)
    return jsonify(status=group.create_bulletin(user_id, title, text))


@app.route('/_delete_bulletin')
def delete_bulletin():
    bulletin_id = request.args.get('bulletin_id')
    print bulletin_id
    user_id = session.get('user_id')
    user = User(user_id=user_id)
    return jsonify(status=user.delete_bulletin(bulletin_id))

if __name__ == '__main__':
    app.run(debug=True, host=HOST, port=PORT)
    