#coding:utf-8-*-
import MySQLdb
from config import *
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self, name='', email='', user_id=0):
        if(name=='' and email==''):
            self.user_id = user_id
            # print 'user_id:', user_id
            try:
                data = self.get_data_by_id()
                self.username = data['username']
                self.email = data['email']
                self.role = data['role'] #admin or user?
            except Exception, e:
                print 'initUser', e
        else:
            self.username = name
            self.email = email
            if self.check_e():
                data = self.get_data_by_email()
                # print data
                self.role = data['role']

    def get_data_by_id(self):
        #if(self.check_id()):
        #    return {}
        conn = MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],user=db_config["db_user"],passwd=db_config["db_passwd"],db=db_config["db_name"],charset="utf8")
        cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        cursor.execute("select * from user where user_id='" + str(self.user_id) + "';")
        data = cursor.fetchall()
        conn.close()

        return data[0]

    def get_data_by_email(self):
        if not self.check_e():
            return {}
        conn = MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],user=db_config["db_user"],passwd=db_config["db_passwd"],db=db_config["db_name"],charset="utf8")
        cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        cursor.execute("select * from user where email='" + self.email + "';")
        data = cursor.fetchall()
        conn.close()
        return data[0]

    def get_data_by_name(self):
        if not self.check_u():
            return {}
        conn = MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],user=db_config["db_user"],passwd=db_config["db_passwd"],db=db_config["db_name"],charset="utf8")
        cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        sql = 'select * from user where user_id = %d;' % self.user_id
        cursor.execute(sql)
        data = cursor.fetchall()
        conn.close()
        return data[0]

    def get_messages(self):
        conn = MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],user=db_config["db_user"],passwd=db_config["db_passwd"],db=db_config["db_name"],charset="utf8")
        cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        
        receiver = self.user_id
        sql = "select * from message \
               where receiver = %d and viewed = 0 \
               order by time desc;" % (receiver)
        cursor.execute(sql)
        data = cursor.fetchall()
        # print "message data is:", data
        conn.close()
        return data;

    def create_group(self, groupname, topic, desc,confirmMessage):
        conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],user=db_config["db_user"],passwd=db_config["db_passwd"],db=db_config["db_name"],charset="utf8")
        cursor=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        groupname = groupname.encode('utf8')
        #判断是否存在
        cursor.execute("select name from groups where name='" + groupname + "';")
        exist=cursor.fetchall()
        if(exist):
            print 'failed to create group :', groupname
            return 'exist'

        cursor.execute("insert into groups(name,topic,description,confirmMessage,leader_id) values(%s,%s,%s,%s,%s);",\
            (groupname, topic,desc, confirmMessage, self.user_id))
        conn.commit()

        cursor.execute("select group_id from groups where name='"+groupname+"';")
        group_id=cursor.fetchone()['group_id']

        create_message = "Have a look at new bulletin(s) in Group %s!" % groupname
        sql = 'insert into message(type, group_id, receiver, content) \
               values(%d, %d, %d, "%s");' % (1, group_id, self.user_id, create_message)
        cursor.execute(sql)
        conn.commit()

        create_message = "Have a look at new discussion(s) in Group %s!" % groupname
        sql = 'insert into message(type, group_id, receiver, content) \
               values(%d, %d, %d, "%s");' % (3, group_id, self.user_id, create_message)
        cursor.execute(sql)
        conn.commit()

        create_message = "Have a look at new vote(s) in Group %s!" % groupname
        sql = 'insert into message(type, group_id, receiver, content) \
               values(%d, %d, %d, "%s");' % (2, group_id, self.user_id, create_message)
        cursor.execute(sql)
        conn.commit()

        cursor.execute("insert into groupMemberAssosiation(group_id,member_id) values(%s,%s);",(group_id,self.user_id))
        conn.commit()
        conn.close()
        print 'created group successfully:', groupname
        return 'success'

    def delete_group(self,group_id):
        group_id=str(group_id)
        conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],user=db_config["db_user"],passwd=db_config["db_passwd"],db=db_config["db_name"],charset="utf8")
        cursor=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        #判断是否存在且用户为leader
        cursor.execute("select name from groups where group_id='"+group_id+"' and leader_id='"+str(self.user_id)+"';")
        groupname=cursor.fetchone()
        print group_id, self.user_id
        if(groupname):
            print groupname
            cursor.execute("select * from groupMemberAssosiation where group_id='"+group_id+"';")
            
            relations = cursor.fetchall()
            for relation in relations:
                if relation['member_id'] == self.user_id:
                    continue
            delete_message = "The leader of group %s has deleted this group." % groupname['name']
            sql = "insert into message(type, group_id, receiver, content)\
                   values(%d, %s, %s, '%s');" % (4, group_id, 0, delete_message)
            cursor.execute(sql)
            

            cursor.execute("delete from message where group_id='"+group_id+"';")
            cursor.execute("delete from groups where group_id='"+group_id+"';")
            conn.commit()
            cursor.execute("delete from groupMemberAssosiation where group_id='"+group_id+"';")
            conn.commit()
            conn.close()
            print 'deleted group successfully :', group_id
            return True
        conn.close()
        print 'failed to delete group :', group_id
        return False

    def get_groups(self):
        conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],user=db_config["db_user"],passwd=db_config["db_passwd"],db=db_config["db_name"],charset="utf8")
        cursor=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        cursor.execute("select group_id from groupMemberAssosiation where member_id='"+str(self.user_id)+"';")
        # print "user_id is", self.user_id
        attendedGroups=cursor.fetchall()
        cursor.execute("select group_id from groups where leader_id='"+str(self.user_id)+"';")
        ownGroups=cursor.fetchall()
        conn.close()
        attendedGroupsName = []
        ownGroupsName = []
        for i in attendedGroups:
            attendedGroupsName += [i['group_id']]
        for i in ownGroups:
            ownGroupsName += [i['group_id']]
        # print ownGroups
        return attendedGroupsName, ownGroupsName
    #注意！！这里的返回值是所有的小组id组成的list，不是字典的list！！！

    def join_group(self, group_id, confirm):
        group_id=str(group_id)
        group = Group(group_id=group_id)
        conn = MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],user=db_config["db_user"],passwd=db_config["db_passwd"],db=db_config["db_name"],charset="utf8")
        cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        if(group.exist_group()):
            cursor.execute("select member_id from groupMemberAssosiation where group_id='"+str(group_id)+"';")
            member_list = cursor.fetchall()
            if(str(self.user_id) in member_list):
                return 'joined'
            if(confirm == group.confirmMessage):

                create_message = "Have a look at new bulletin(s) in Group %s!" % group.name
                sql = 'insert into message(type, group_id, receiver, content) \
                       values(%d, %s, %d, "%s");' % (1, group_id, self.user_id, create_message)
                cursor.execute(sql)
                conn.commit()

                create_message = "Have a look at new discussion(s) in Group %s!" % group.name
                sql = 'insert into message(type, group_id, receiver, content) \
                       values(%d, %s, %d, "%s");' % (3, group_id, self.user_id, create_message)
                cursor.execute(sql)
                conn.commit()

                create_message = "Have a look at new vote(s) in Group %s!" % group.name
                sql = 'insert into message(type, group_id, receiver, content) \
                       values(%d, %s, %d, "%s");' % (2, group_id, self.user_id, create_message)
                cursor.execute(sql)
                conn.commit()

                cursor.execute("insert into groupMemberAssosiation(group_id,member_id) values(%s,%s) ;", (group_id, self.user_id) )
                conn.commit()
                conn.close()
                return 'success'
            else:
                conn.close()
                return 'fail'
        conn.close()
        return 'non-ex'

    def quit_group(self,group_id):
        group = Group(group_id = group_id)
        group_id=str(group_id)
        conn = MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],user=db_config["db_user"],passwd=db_config["db_passwd"],db=db_config["db_name"],charset="utf8")
        cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        cursor.execute("select * from groupMemberAssosiation where member_id='"+str(self.user_id)+"' and group_id='"+group_id+"';")
        exist = cursor.fetchall()
        if(exist):

            quit_message = "The member %s quitted our group." % (self.username)
            sql = "insert into news(type, group_id, receiver, content)\
                   values(%d, %s, %s, '%s');" % (6, group_id, 0, quit_message)
            cursor.execute(sql)

            quit_message = "The member %s quitted your group %s." % (self.username, group.name)
            sql = "insert into message(type, group_id, receiver, content)\
                   values(%d, %s, %s, '%s');" % (8, group_id, group.leader_id, quit_message)
            cursor.execute(sql)

            cursor.execute("delete from message where receiver='"+str(self.user_id)+"' and group_id='"+group_id+"';")

            cursor.execute("delete from groupMemberAssosiation where member_id='"+str(self.user_id)+"' and group_id='"+group_id+"';")
            conn.commit()
            #whether he's leader
            cursor.execute("select name from groups where group_id='"+group_id+"' and leader_id='"+str(self.user_id)+"';")
            isLeader=cursor.fetchall()  
            if(isLeader):
                print "the user trying to quit is LEADER!"
                cursor.execute("delete from groups where group_id='"+group_id+"';")
                conn.commit()


            conn.close()
            print 'quit group successfully :',group_id
            return 1
        print 'failed to quit group :',group_id
        conn.close()
        return 0

    def search_group(self, group_id):
        group_id=str(group_id)
        conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],user=db_config["db_user"],passwd=db_config["db_passwd"],db=db_config["db_name"],charset="utf8")
        cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        #判断是否存在
        cursor.execute("select name from groups where group_id='"+group_id+"';")
        exist=cursor.fetchall()
        if(exist):
            Group1=Group(group_id)
            return Group1
        return None

    def kick_member(self,group_id,user_id):
        group_id=str(group_id)
        user_id=str(user_id)
        conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],user=db_config["db_user"],passwd=db_config["db_passwd"],db=db_config["db_name"],charset="utf8")
        cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        cursor.execute("select name from groups where group_id='%s' and leader_id='%s';"),(group_id,self.user_id)
        exist=cursor.fetchall()
        if(exist):
            cursor.execute("select * from groupMemberAssosiation where group_id='%s' and member_id='%s';"),(group_id,user_id)
            exist=cursor.fetchall()
            if(exist):

                user = User(user_id = user_id)
                delete_message = "Group member %s is removed from our group." % user.username
                sql = "insert into news(type, group_id, receiver, content)\
                       values(%d, %s, %s, '%s');" % (5, group_id, user_id, delete_message)
                cursor.execute(sql)

                delete_message = "The leader of group %s has removed you from the group." % exist.name
                sql = "insert into message(type, group_id, receiver, content)\
                       values(%d, %s, %s, '%s');" % (4, group_id, user_id, delete_message)
                cursor.execute(sql)

                sql = "delete from message where group_id = %s and receiver = %d;" % (group_id, user_id)
                cursor.execute(sql)

                cursor.execute("delete from groupMemberAssosiation where group_id='%s' and member_id='%s';"),(group_id,user_id)
                conn.commit()

                return True
            print "Cannot find user_id in the group"
            return False

        print "Not leader"
        return False

    def message_confirm(self,message_id):
        conn = MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],user=db_config["db_user"],passwd=db_config["db_passwd"],db=db_config["db_name"],charset="utf8")
        cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        sql = "update message set viewed = 1 where message.message_id = %s;" % message_id
        cursor.execute(sql)
        conn.commit()
        conn.close()
        return True

    def check_u(self):
        conn = MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],user=db_config["db_user"],passwd=db_config["db_passwd"],db=db_config["db_name"],charset="utf8")
        cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        cursor.execute("select * from user where username='" + unicode(self.username) + "';")
        exist = cursor.fetchall()
        if exist:
            return 1
        return 0

    def check_e(self):
        conn = MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],user=db_config["db_user"],passwd=db_config["db_passwd"],db=db_config["db_name"],charset="utf8")
        cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        cursor.execute("select * from user where email='" + str(self.email) + "';")
        exist = cursor.fetchall()
        if exist:
            return 1
        return 0

    def check_id(self):
        conn = MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],user=db_config["db_user"],passwd=db_config["db_passwd"],db=db_config["db_name"],charset="utf8")
        cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        cursor.execute("select * from user where user_id='" + str(self.user_id) + "';")
        exist = cursor.fetchall()
        if exist:
            return 1
        return 0

    def login(self, pw):
        conn = MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],user=db_config["db_user"],passwd=db_config["db_passwd"],db=db_config["db_name"],charset="utf8")
        cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        cursor.execute("select * from user where email='" + str(self.email) + "';")
        exist = cursor.fetchall()
        print exist
        if exist:
            if check_password_hash(exist[0]['password'], pw):
                return 1    #匹配成功
            else:
                return 0    #密码错误
        return -1               #邮箱不存在

    def register(self, password):
        conn = MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],user=db_config["db_user"],passwd=db_config["db_passwd"],db=db_config["db_name"],charset="utf8")
        cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        password = generate_password_hash(password)
        sql = 'insert into user(username, password, email) values("%s","%s","%s")' % (self.username, password, self.email)
        cursor.execute(sql)
        conn.commit()
        sql = 'select * from user where email="%s"' % self.email
        cursor.execute(sql)
        user = cursor.fetchone()

        welcome_content = "welcome to our Grape system, %s!" % user['username']
        sql = 'insert into message(type, group_id, receiver, content, viewed) \
               values(%d, %d, %d, "%s",0);' % (0, 0, user['user_id'], welcome_content)
        cursor.execute(sql)
        conn.commit()

        conn.close()
        return user

    def delete_vote(self,vote_id):
        conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],\
                             user=db_config["db_user"],passwd=db_config["db_passwd"],\
                             db=db_config["db_name"],charset="utf8")
        vote = Vote(vote_id,self.user_id)
        cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        cursor.execute("select * from groups where group_id = %d and leader_id = %d" % (vote.group_id,self.user_id))
        # only leader can delete vote
        right = cursor.fetchall()
        if (right):
            cursor.execute("delete from votes where vote_id = %d" % int(vote_id))
            conn.commit()
            conn.close()
            return True
        conn.close()
        return False

    def end_vote(self,vote_id):
        conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],\
                             user=db_config["db_user"],passwd=db_config["db_passwd"],\
                             db=db_config["db_name"],charset="utf8")
        vote = Vote(vote_id,self.user_id)
        cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        cursor.execute("select * from groups where group_id = %d and leader_id = %d" % (vote.group_id,self.user_id))
        # only leader can delete vote
        right = cursor.fetchall()
        if (right):
            cursor.execute("update votes set voting=0 and endtime=CURRENT_TIMESTAMP where vote_id=%s" % vote_id);
            conn.commit();
            conn.close();
            return True
        conn.close()
        return False

    def delete_discussion(self,discuss_id):
        conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],\
                             user=db_config["db_user"],passwd=db_config["db_passwd"],\
                             db=db_config["db_name"],charset="utf8")
        cursor=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        discuss = Discussion(discuss_id)
        group = Group(discuss.group_id)
        valid = (discuss.user_id == self.user_id) or (group.leader_id == self.user_id)
        if(valid):
            delete_message = "Your discussion %s in group %s has been deleted by leader."\
                              % (discuss.title,group.name)
            sql = "insert into news(type, group_id, receiver, content)\
                   values(%d, %s, %s, '%s');" % (6, group.group_id, discuss.user_id, delete_message)
            cursor.execute(sql)

            sql = "delete from discussion where discuss_id = %s;" % discuss_id
            cursor.execute(sql)
            conn.commit()
            conn.close()
            return True
        conn.close()
        return False

    def delete_reply(self,reply_id):
        conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],\
                             user=db_config["db_user"],passwd=db_config["db_passwd"],\
                             db=db_config["db_name"],charset="utf8")
        cursor=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        reply = Reply(reply_id)
        discuss = Discussion(reply.discuss_id)
        group = Group(discuss.group_id)
        valid = (reply.user_id == self.user_id) or (group.leader_id == self.user_id)
        if(valid):
            delete_message = 'Your reply: "%s" on discussion %s has been deleted by leader.'\
                              % (reply.content, discuss.title)
            sql = "insert into news(type, group_id, receiver, content)\
                   values(%d, %s, %s, '%s');" % (7, group.group_id, reply.user_id, delete_message)
            cursor.execute(sql)

            sql = "delete from reply_discuss where reply_id = %s;" % reply_id
            cursor.execute(sql)
            sql = "update discussion set reply_num = reply_num - 1\
                   where discussion.discuss_id = %d;" % reply.discuss_id
            cursor.execute(sql)
            conn.commit()
            conn.close()
            return True
        conn.close()
        return False

    def delete_bulletin(self, bulletin_id):
        conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],\
                             user=db_config["db_user"],passwd=db_config["db_passwd"],\
                             db=db_config["db_name"],charset="utf8")
        cursor=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        bulletin = Bulletin(bulletin_id)
        if (bulletin.user_id == self.user_id):
            print "Arrive here", bulletin.user_id
            sql = "delete from bulletin where bulletin_id = %s;" % bulletin_id
            cursor.execute(sql)
            conn.commit()
            conn.close()
            return True
        conn.close()
        return False

class Admin(User):
    def __init__(self, user_id):
        User.__init__(self,user_id=user_id)

    def delete_group(self,group_id):
        group_id=str(group_id)
        conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],user=db_config["db_user"],passwd=db_config["db_passwd"],db=db_config["db_name"],charset="utf8")
        cursor=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        #判断是否存在
        cursor.execute("select name from groups where group_id='"+group_id+"';")
        right=cursor.fetchall()
        if(right):

            delete_message = "The group %s is deleted by the Admin." % (self.name)
            sql = "insert into message(type, group_id, receiver, content)\
                   values(%d, %s, %d, '%s');" % (4, self.group_id, 0, delete_message)
            cursor.execute(sql)

            cursor.execute("delete from groups where group_id='"+group_id+"';")
            conn.commit()
            cursor.execute("delete from groupMemberAssosiation where group_id='"+group_id+"';")
            conn.commit()
            conn.close()
            print 'deleted group successfully :', group_id
            return True
        conn.close()
        print 'admin failed to delete group :', group_id
        return False

    def show_all_groups(self):
        conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],user=db_config["db_user"],passwd=db_config["db_passwd"],db=db_config["db_name"],charset="utf8")
        cursor=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)  
        cursor.execute("select * from groups;")
        groups=cursor.fetchall()
        # print groups
        conn.close()

        return groups

    def show_all_users(self):
        conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],user=db_config["db_user"],passwd=db_config["db_passwd"],db=db_config["db_name"],charset="utf8")
        cursor=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)  
        cursor.execute("select * from user;")
        users_info=cursor.fetchall()

        users=[]
        for user in users_info:
            attendedGroupsList=[]
            ownGroupsList=[]
            User1=User(user_id=user['user_id'])
            attendedGroups, ownGroups = User1.get_groups()

            for i in ownGroups:
                ownGroupsList += [Group(i).get_data()]
            for i in attendedGroups:
                if i not in ownGroups:
                    attendedGroupsList += [Group(i).get_data()]
            users+=[  [user,attendedGroupsList,ownGroupsList]  ]
        # for user in users:
        #     print user
        #     print 
        #     print 
        #     print 
        conn.close() 
        return users

    def delete_user(self,user_id):
        user_id=str(user_id)
        conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],user=db_config["db_user"],passwd=db_config["db_passwd"],db=db_config["db_name"],charset="utf8")
        cursor=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)

        if int(user_id)==int(self.user_id):
            print "cannot delete yourself!"
            return False
        cursor.execute("select user_id from user where user_id='"+user_id+"';")
        right=cursor.fetchall()
        if(right):
            #删除全部相关信息
            cursor.execute("delete from user where user_id='"+user_id+"';")
            conn.commit()
            cursor.execute("delete from groupMemberAssosiation where member_id='"+user_id+"';")
            conn.commit()
            cursor.execute("delete from message where receiver = '"+user_id+"';")
            conn.commit()
            cursor.execute("select group_id from groups where leader_id='"+user_id+"';")
            leadergroups=cursor.fetchall()
            # print 'leadergroups',leadergroups
            if(leadergroups):
                for i in leadergroups:
                    cursor.execute("delete from groupMemberAssosiation where group_id='"+str(i['group_id'])+"';")
                    conn.commit()
                cursor.execute("delete from groups where leader_id='"+user_id+"';")
                conn.commit()

            conn.close()
            print 'deleted user successfully :', user_id
            return True
        return False

class Group:

    def __init__(self, group_id):
        ##名字与数据库中相同
        self.group_id = str(group_id)
        if(self.exist_group()):
            data = self.get_data()
            self.name = data['name']
            self.topic = data['topic']
            self.confirmMessage = data['confirmMessage']
            self.leader_id = data['leader_id']
            #NEW ITEM
            self.description=data['description']
            self.create_time=data['create_time']
        #这里leader的标识也变成id了，注意！！！

    def exist_group(self):
        conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],user=db_config["db_user"],passwd=db_config["db_passwd"],db=db_config["db_name"],charset="utf8")
        cursor=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        cursor.execute("select name from groups where group_id='" + self.group_id + "';")
        exist=cursor.fetchall()
        return exist

    def get_news(self, user_id):
        conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],user=db_config["db_user"],passwd=db_config["db_passwd"],db=db_config["db_name"],charset="utf8")
        cursor=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        receiver = -1*user_id
        sql = 'select * from news where \
               group_id = %s and ((receiver < 0 and receiver != %d )\
               or (receiver > 0 and receiver = %d and receiver != %d) or receiver = 0)\
               order by time desc;' % (self.group_id, receiver, user_id, self.leader_id)
        cursor.execute(sql)
        data = cursor.fetchall()
        return data

    def get_members(self):
        conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],user=db_config["db_user"],passwd=db_config["db_passwd"],db=db_config["db_name"],charset="utf8")
        cursor=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        cursor.execute("select member_id from groupMemberAssosiation where group_id=" + "'" + self.group_id + "';")
        members=cursor.fetchall()
        conn.close()
        return members
        #返回值是member的id dictionary！！！

    def get_discussions(self):
        conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],\
                             user=db_config["db_user"],passwd=db_config["db_passwd"],\
                             db=db_config["db_name"],charset="utf8")

        cursor=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        sql = "select * from discussion where group_id = %s \
               order by create_time desc;" % self.group_id
        cursor.execute(sql)
        discussions=cursor.fetchall()

        for discuss in discussions:
            user = User(user_id=discuss["user_id"])
            discuss['username'] = user.username

        conn.close()
        #print "discussions: ",discussions
        return discussions

    def create_discussion(self, user_id, title, content):
        conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],\
                             user=db_config["db_user"],passwd=db_config["db_passwd"],\
                             db=db_config["db_name"],charset="utf8")
        cursor=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)

        create_message = "A new discussion %s is created in our group" % (title)
        receiver = -1*(user_id)
        sql = "insert into news(type, group_id, receiver, content)\
               values(%d, %s, %d, '%s');" % (1, self.group_id, receiver, create_message)
        cursor.execute(sql)

        excluder = user_id
        sql = "update message \
               set viewed = 0, time = CURRENT_TIMESTAMP \
               where type = 3 and group_id = %s and receiver != %d;" % (self.group_id, excluder)
        cursor.execute(sql)
        conn.commit()

        sql = "insert into discussion(user_id, group_id, title, content) values(%d,%s,'%s','%s');"\
              % (user_id, self.group_id, title, content)
        cursor.execute(sql)
        conn.commit()
        conn.close()
        return True


    def create_vote(self,user_id,title,vote_contents_set,selection,options_set,vote_options_set,endtime):
        conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],\
                             user=db_config["db_user"],passwd=db_config["db_passwd"],\
                             db=db_config["db_name"],charset="utf8")
        cursor=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)

        create_message = "A new vote %s is created in our group!" % (title)
        receiver = -1*(user_id)
        sql = "insert into news(type, group_id, receiver, content)\
               values(%d, %s, %d, '%s');" % (3, self.group_id, receiver, create_message)
        cursor.execute(sql)

        excluder = user_id
        sql = "update message \
               set viewed = 0, time = CURRENT_TIMESTAMP \
               where type = 2 and group_id = %s and receiver != %d;" % (self.group_id, excluder)
        cursor.execute(sql)
        conn.commit()

        sql = """insert into votes (user_id,group_id,title,voting,type,endtime) values (%s,%s,%s,1,%s,%s)""" % (user_id,self.group_id,title,selection,endtime)
        cursor.execute(sql)
        conn.commit()

        cursor.execute("select LAST_INSERT_ID() from votes where group_id='%s'" % (self.group_id))

        """
        mid =  cursor.fetchall()
        print mid,"#########"
        voteid = mid[0][0]
        """

        voteid = cursor.fetchone()['LAST_INSERT_ID()']

        sql = """ CREATE EVENT event_%s ON SCHEDULE AT %s  ENABLE DO update votes set voting=0 where vote_id=%d;""" % (voteid,endtime,voteid)
        cursor.execute(sql)
        conn.commit()
        print len(options_set)+1
        for i in range (1,len(options_set)+1):
            sql = """insert into vote_contents (vote_id,vote_content,content_order,options) values (%s,%s,%d,%s)""" %(voteid,vote_contents_set[i-1],i,options_set[i-1])
            cursor.execute(sql)
            conn.commit()
            cursor.execute("""select LAST_INSERT_ID() from vote_contents where vote_id=%s""" % (voteid))
            content_id = cursor.fetchone()['LAST_INSERT_ID()']

            for j in range (1,options_set[i-1]+1):
                sql = """insert into vote_detail(content_id,option_order,vote_option,votes) values (%d,%d,%s,0)""" % (content_id,j,vote_options_set[i-1][j-1])
                cursor.execute(sql)
                conn.commit()
        conn.close()
        return True

    def get_votes_voting(self):
        votes_list_voting = []
        conn = MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],user=db_config["db_user"],passwd=db_config["db_passwd"],db=db_config["db_name"],charset="utf8")

        cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        sql = "select * from votes where group_id = %s and voting = 1 order by endtime" % self.group_id
        cursor.execute(sql)
        votes_data = cursor.fetchall()
        for vote in votes_data:
            sql = "select count(user_id) from vote_user_map where vote_id = %s" % vote['vote_id']
            cursor.execute(sql)
            voted_num = cursor.fetchone()['count(user_id)']
            sql = "select username from user where user_id = %d" % vote['user_id']
            cursor.execute(sql)
            username = cursor.fetchone()['username']
            vote_pair = (vote['vote_id'],vote['title'],voted_num,vote['begintime'], vote['endtime'], username)
            votes_list_voting.append(vote_pair)

        conn.close()
        return votes_list_voting
        # the last is the voted num of person


    def get_votes_expired(self):
        votes_list_end = []
        conn = MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],user=db_config["db_user"],passwd=db_config["db_passwd"],db=db_config["db_name"],charset="utf8")
        cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        sql = "select * from votes where group_id = %s and voting = 0 order by endtime desc" % self.group_id
        cursor.execute(sql);
        votes_data = cursor.fetchall()
        for vote in votes_data:
            sql = "select count(user_id) from vote_user_map where vote_id = %s" % vote['vote_id']
            cursor.execute(sql)
            voted_num = cursor.fetchone()['count(user_id)']
            sql = "select username from user where user_id = %d" % vote['user_id']
            cursor.execute(sql)
            username = cursor.fetchone()['username']
            vote_pair = (vote['vote_id'],vote['title'],voted_num, vote['begintime'], vote['endtime'], username)
            votes_list_end.append(vote_pair)

        conn.close()
        return votes_list_end

    def get_recent_voted_record(self):
        conn = MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],user=db_config["db_user"],passwd=db_config["db_passwd"],db=db_config["db_name"],charset="utf8")
        cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        sql = "select * from vote_user_map where group_id = %s order by vote_time desc limit 5" % self.group_id
        cursor.execute(sql)

        vote_record = []
        people_record = cursor.fetchall()
        sql = "select NOW()"
        cursor.execute(sql)
        timenow = cursor.fetchone()['NOW()']

        for vote_op in people_record:
            vote_time = vote_op['vote_time']
            dlta = str(timenow - vote_time)
            user = User(user_id = vote_op['user_id'])
            vote = Vote(vote_op['vote_id'],vote_op['user_id'])
            ######## 好像不是很合理 拿投票的人生成Vote对象###
            vote_op_pair = (user.username,vote.title,dlta)
            ######用户名 投了哪个 多久之前
            vote_record.append(vote_op_pair)

        return vote_record

    def create_bulletin(self, user_id, title, text):
        conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],\
                             user=db_config["db_user"],passwd=db_config["db_passwd"],\
                             db=db_config["db_name"],charset="utf8")
        cursor=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        if self.leader_id == user_id:

            create_message = "A new bulletin %s is created in our group!" % (title)
            receiver = -1*(user_id)
            sql = "insert into news(type, group_id, receiver, content)\
                   values(%d, %s, %d, '%s');" % (4, self.group_id, receiver, create_message)
            cursor.execute(sql)

            excluder = user_id
            sql = "update message \
                   set viewed = 0, time = CURRENT_TIMESTAMP \
                   where type = 1 and group_id = %s and receiver != %d;" % (self.group_id, excluder)
            cursor.execute(sql)
            conn.commit()

            sql = "insert into bulletin(user_id, group_id, title, text) values(%d,%s,'%s','%s');"\
                  % (user_id, self.group_id, title, text)
            cursor.execute(sql)
            conn.commit()
            conn.close()
            return True
        conn.close()
        return False;

    def get_bulletin(self):
        conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],\
                             user=db_config["db_user"],passwd=db_config["db_passwd"],\
                             db=db_config["db_name"],charset="utf8")

        cursor=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        sql = "select * from bulletin where group_id = %s \
               order by create_time desc;" % self.group_id
        cursor.execute(sql)
        bulletin=cursor.fetchall()

        for entry in bulletin:
            user = User(user_id=entry["user_id"])
            entry['username'] = user.username

        conn.close()
        return bulletin

    def get_data(self):
        conn = MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],user=db_config["db_user"],passwd=db_config["db_passwd"],db=db_config["db_name"],charset="utf8")
        cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        sql = "select * from groups where group_id="+self.group_id+";"
        cursor.execute(sql)
        data = cursor.fetchall()
        # get discussion data, including reply.
        try:
            discuss_list = self.get_discussions()
            data[0]['discuss_list'] = discuss_list
        except Exception,e:
            print 'get discuss:',e
        conn.close()
        # append some other lists
        leader = User(user_id=int(data[0]['leader_id']))
        data[0]['leader_info'] = {'name':leader.username, 'email':leader.email, 'id':leader.user_id}
        try:
            data[0]['user_info'] = []
            for member in self.get_members():
                member = User(user_id=member['member_id'])
                data[0]['user_info'] += [{'name':member.username, 'email':member.email, 'id':member.user_id}]
        except Exception, e:
            #data[0]['leader_info'] = {'name':'', 'email':'', 'id':''}
            data[0]['user_info'] = []
            print e
        return data[0]

    def news(self, type, receiver, content):
        conn = MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],user=db_config["db_user"],passwd=db_config["db_passwd"],db=db_config["db_name"],charset="utf8")
        cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        sql = "insert into message(type, group_id, receiver, content)\
                   values(%d, %s, %d, '%s');" % (type, self.group_id, receiver, content)
        cursor.execute(sql)

class Discussion:
    def __init__(self,discuss_id):
        self.discuss_id = int(discuss_id)
        if self.exist():
            data = self.get_data()
            self.group_id = data['group_id']
            self.user_id = data['user_id']
            self.title = data['title']
            self.content = data['content']

    def get_data(self):
        conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],\
                             user=db_config["db_user"],passwd=db_config["db_passwd"],\
                             db=db_config["db_name"],charset="utf8")
        cursor=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        sql = "select * from discussion where discuss_id="+str(self.discuss_id)+";"
        cursor.execute(sql)
        item = cursor.fetchone()
        user = User(user_id=item["user_id"])
        item["username"] = user.username
        conn.close()
        return item

    def increase_read_num(self):
        conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],\
                             user=db_config["db_user"],passwd=db_config["db_passwd"],\
                             db=db_config["db_name"],charset="utf8")
        cursor=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        sql = "update discussion set read_num = read_num + 1 \
               where discussion.discuss_id = %d;" % self.discuss_id
        cursor.execute(sql)
        conn.commit()
        conn.close()

    def add_reply(self,user_id,content):
        conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],\
                             user=db_config["db_user"],passwd=db_config["db_passwd"],\
                             db=db_config["db_name"],charset="utf8")
        cursor=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)

        # sql = "select receiver from news where type = 2 and group_id = %s" % self.group_id;
        # create_message = "New replies in discussion <i>%s</i>!" % (self.title)
        # receiver = -1*(user_id)
        # sql = "insert into news(type, group_id, receiver, content)\
        #        values(%d, %s, %d, '%s');" % (2, self.group_id, receiver, create_message)
        # cursor.execute(sql)

        sql = "insert into reply_discuss(discuss_id, user_id, content) values(%d,%d,'%s');"\
              % (self.discuss_id, user_id, content)
        cursor.execute(sql)
        sql = "update discussion set reply_num = reply_num + 1 \
               where discussion.discuss_id = %d;" % self.discuss_id
        cursor.execute(sql)
        conn.commit()
        conn.close()

    def get_reply(self):
        conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],\
                             user=db_config["db_user"],passwd=db_config["db_passwd"],\
                             db=db_config["db_name"],charset="utf8")
        cursor=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        sql = "select * from reply_discuss where discuss_id = %d\
               order by reply_id desc;" % self.discuss_id
        cursor.execute(sql)
        reply = cursor.fetchall()
        for item in reply:
            user = User(user_id=item['user_id'])
            item['username'] = user.username
        conn.close()
        return reply

    def exist(self):
        conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],\
                             user=db_config["db_user"],passwd=db_config["db_passwd"],\
                             db=db_config["db_name"],charset="utf8")
        cursor=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        sql = "select * from discussion where discuss_id="+str(self.discuss_id)+";"
        cursor.execute(sql)
        exist = cursor.fetchall()
        conn.close()
        if exist:
            return 1    #exist
        return 0        #non-ex


class Reply:
    def __init__(self,reply_id):
        self.reply_id = int(reply_id)
        if self.exist():
            data = self.get_data()
            self.user_id = data['user_id']
            self.discuss_id = data['discuss_id']
            self.content = data['content']

    def get_data(self):
        conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],\
                             user=db_config["db_user"],passwd=db_config["db_passwd"],\
                             db=db_config["db_name"],charset="utf8")
        cursor=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        sql = "select * from reply_discuss where reply_id="+str(self.reply_id)+";"
        cursor.execute(sql)
        item = cursor.fetchone()
        conn.close()
        return item

    def exist(self):
        conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],\
                     user=db_config["db_user"],passwd=db_config["db_passwd"],\
                     db=db_config["db_name"],charset="utf8")
        cursor=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        sql = "select * from reply_discuss where reply_id = %d;" % self.reply_id
        cursor.execute(sql)
        exist = cursor.fetchall()
        conn.close()
        if exist:
            return 1    #exist
        return 0        #non-ex

class Bulletin:
    def __init__(self, bulletin_id):
        self.bulletin_id = int(bulletin_id)
        if self.exist():
            data = self.get_data()
            self.group_id = data['group_id']
            self.user_id = data['user_id']
            self.title = data['title']
            self.text = data['text']

    def get_data(self):
        conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],\
                             user=db_config["db_user"],passwd=db_config["db_passwd"],\
                             db=db_config["db_name"],charset="utf8")
        cursor=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        sql = "select * from bulletin where bulletin_id="+str(self.bulletin_id)+";"
        cursor.execute(sql)
        item = cursor.fetchone()
        user = User(user_id=item["user_id"])
        item["username"] = user.username
        conn.close()
        return item

    def increase_read_num(self):
        conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],\
                             user=db_config["db_user"],passwd=db_config["db_passwd"],\
                             db=db_config["db_name"],charset="utf8")
        cursor=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        sql = "update bulletin set read_num = read_num + 1 \
               where bulletin.bulletin_id = %d;" % self.bulletin_id
        cursor.execute(sql)
        conn.commit()
        conn.close()

    def exist(self):
        conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],\
                     user=db_config["db_user"],passwd=db_config["db_passwd"],\
                     db=db_config["db_name"],charset="utf8")
        cursor=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        sql = "select * from bulletin where bulletin_id = %d;" % self.bulletin_id
        cursor.execute(sql)
        exist = cursor.fetchall()
        conn.close()
        if exist:
            return 1    #exist
        return 0 


class Vote:
    def __init__(self,vote_id,user_id):
        self.vote_id = int(vote_id)
        if self.exist():
            data = self.get_data(user_id)
            self.user_id = data['user_id']
            self.group_id = data['group_id']
            self.vote_contents = data['vote_contents'] # a list
            self.vote_options = data['options_content'] # a list
            self.title = data['title']
            # array
            self.is_voted = data['is_voted']    # a num 0 or 1
            # 0 not voted
            self.options_voted = data['options_voted'] # a set
            # 0 not voted
            self.begintime = data['begintime']
            self.endtime = data['endtime']
            self.timedelta = str(self.endtime - self.begintime)
            self.voted_num = data['voted_num']
            self.options_num = data['options_num']
            self.votes = data['votes']
            self.contents_num = len( self.vote_contents)

    def get_data(self,user_id):
        conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],\
                             user=db_config["db_user"],passwd=db_config["db_passwd"],\
                             db=db_config["db_name"],charset="utf8")
        cursor=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)

        sql="select * from votes where vote_id = %s" % self.vote_id;
        cursor.execute(sql)
        item = cursor.fetchone() #title and so on
        ##########################
        sql = "select * from vote_contents where vote_id = %s" % self.vote_id;
        cursor.execute(sql)
        vote_contents_data = cursor.fetchall()


        sql = "select * from vote_user_map where vote_id= %s and user_id= %s" % (self.vote_id,user_id)
        cursor.execute(sql)
        map = cursor.fetchall()

        if (len(map) == 0):
            item['is_voted'] = 0
        else:
            item['is_voted'] = 1


        item['vote_contents'] = []
        item['options_num']=[]
        item['options_content'] = []
        item['votes'] = []
        item['options_voted'] = []
        for vote_content in vote_contents_data: 
            item['vote_contents'].append(vote_content['vote_content'])
            item['options_num'].append(vote_content['options']) #set the width
            sql = "select * from vote_detail where content_id = %d" % vote_content['content_id']
            cursor.execute(sql)
            options_set = cursor.fetchall()
            options_content = []
            votes = []
            for option in options_set:
                options_content.append(option['vote_option'])
                votes.append(int(option['votes']))
            item['votes'].append(votes)
            item['options_content'].append(options_content)
            option_voted = 0
            if (item['is_voted'] == 1):
                sql = "select * from content_user_map where content_id= %s and user_id= %s" % (vote_content['content_id'],user_id)
                print sql
                cursor.execute(sql)
                option_voted = cursor.fetchone()
                print type(option_voted)
                option_voted = option_voted['votefor']
            item['options_voted'].append(option_voted)


        
       ###########################
        sql = "select count(user_id) from vote_user_map where vote_id = %s" % self.vote_id
        cursor.execute(sql)
        voted_num = cursor.fetchone()['count(user_id)']

        item['voted_num'] = voted_num
        ####################################################3

        user = User(user_id = item["user_id"]) # the leader
        item["username"] = user.username
        conn.close()
        return item

    def vote_op(self,user_id,vote_options):
        conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],\
                             user=db_config["db_user"],passwd=db_config["db_passwd"],\
                             db=db_config["db_name"],charset="utf8")
        cursor=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        sql = "select content_id from vote_contents where vote_id=%s" % (self.vote_id)
        cursor.execute(sql)

        
        diff = cursor.fetchall()

        sql = "insert into vote_user_map(vote_id,user_id) values (%s,%s)" % (self.vote_id,user_id)
        cursor.execute(sql)
        conn.commit()

        for i in range(1,len(vote_options)+1):
            sql = "insert into content_user_map(vote_id,content_id,user_id,votefor) values(%s,'%s','%s','%s')" % (self.vote_id,diff[i-1]['content_id'],user_id,vote_options[i-1])
            cursor.execute(sql)
            conn.commit()
            sql = "select count(user_id) from content_user_map where content_id=%s and votefor = %s" % (diff[i-1]['content_id'],vote_options[i-1])
            cursor.execute(sql)
            new_votes = cursor.fetchone()['count(user_id)']
            print new_votes
            sql = "update vote_detail set votes=%s where content_id=%s and option_order=%s" % (new_votes,diff[i-1]['content_id'],vote_options[i-1])
            print new_votes
            cursor.execute(sql)
            conn.commit()
        conn.close()

    def get_recent_voted_record(self):
        conn = MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],user=db_config["db_user"],passwd=db_config["db_passwd"],db=db_config["db_name"],charset="utf8")
        cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        sql = "select * from vote_user_map where vote_id = %s order by vote_time desc limit 5" % self.vote_id
        cursor.execute(sql)

        vote_record = []
        people_record = cursor.fetchall()
        sql = "select NOW()"
        cursor.execute(sql)
        timenow = cursor.fetchone()['NOW()']

        for vote_op in people_record:
            vote_time = vote_op['vote_time']
            dlta = str(timenow - vote_time)
            user = User(user_id = vote_op['user_id'])
            ######## 好像不是很合理 拿投票的人生成Vote对象###
            vote_op_pair = (user.username,self.title,dlta)
            ######用户名 投了哪个 多久之前
            vote_record.append(vote_op_pair)

        return vote_record

    # def votes_distribution(self):
    #     conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],\
    #                          user=db_config["db_user"],passwd=db_config["db_passwd"],\
    #                          db=db_config["db_name"],charset="utf8")
    #     cursor=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
    #     sql = "select * from vote_detail where vote_id='%s'" % self.vote_id
    #     cursor.execute(sql)
    #     votes_static = cursor.fetchall()
    #     vote_options_list = []
    #     votes_distribution = []
    #     option = 0;
    #     for vote_item in votes_static:
    #         vote_options_list.append(str(chr(65+option)))
    #         votes_distribution.append(int(vote_item['votes']))
    #         option+=1
    #     conn.close()
    #     return vote_options_list,votes_distribution


    def exist(self):
        conn=MySQLdb.connect(host=db_config["db_host"],port=db_config["db_port"],\
                     user=db_config["db_user"],passwd=db_config["db_passwd"],\
                     db=db_config["db_name"],charset="utf8")
        cursor=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        sql = "select * from votes where vote_id=%d;" % self.vote_id
        cursor.execute(sql)
        exist = cursor.fetchall()
        conn.close()
        if exist:
            return 1    #exist
        return 0        #non-ex
