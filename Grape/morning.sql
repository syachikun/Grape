Drop Database if exists Grape;
Create Database Grape;
use Grape;

Drop Table if exists groups;
Create Table groups(
group_id int not null primary key AUTO_INCREMENT,
name varchar(30) not null ,
topic varchar(20) not null,
-- groupCapacity int not null,
confirmMessage varchar(30) not null,
leadername varchar(30) not null
);

insert into groups(name,topic,confirmMessage,leadername) values('group1','AI','thisiskey','myn');
insert into groups(name,topic,confirmMessage,leadername) values('group2','ML','thisiskey','myn');
insert into groups(name,topic,confirmMessage,leadername) values('group3','IR','thisiskey','myn');
select * from groups;


Drop Table if exists groupMemberAssosiation;
Create Table groupMemberAssosiation(
groupname varchar(30) not null ,
membername varchar(30) not null
);

insert into groupMemberAssosiation(groupname,membername) values('group1','myn');
insert into groupMemberAssosiation(groupname,membername) values('group2','myn');
insert into groupMemberAssosiation(groupname,membername) values('group3','myn');
select * from groupMemberAssosiation;

Drop Table if exists user;
Create Table user(
user_id int not null primary key AUTO_INCREMENT,
username varchar(128) not null,
password varchar(128) not null, 
email varchar(128),
role int not null default 0
);
insert into user(username, password, email) values('123','123','123@123.com');
insert into user(username, password, email) values('myn','myn','myn@123.com');


Drop Table if exists question;
Create Table question(
question_id int not null primary key AUTO_INCREMENT,
user_id int not null,
group_id int not null,
title varchar(256) not null,
content varchar(256) not null
);
insert into question(user_id, group_id, title, content) values('1','1','question1','This is question 1');
insert into question(user_id, group_id, title, content) values('1','2','question2','This is question 2');
insert into question(user_id, group_id, title, content) values('1','1','question3','This is question 3');
