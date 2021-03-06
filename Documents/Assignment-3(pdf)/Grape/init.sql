Drop Database if exists Grape;
Create Database Grape;
use Grape;

Drop Table if exists groups;
Create Table groups(
group_id int not null primary key AUTO_INCREMENT,
name varchar(30) not null,
topic varchar(20) not null,
description varchar(90) not null default "this is my group!",
create_time timestamp not null default CURRENT_TIMESTAMP,
-- groupCapacity int not null,
confirmMessage varchar(30) not null,
leader_id int not null
);
insert into groups(name,topic,confirmMessage,leader_id) values('group1','AI','thisiskey','2');
insert into groups(name,topic,confirmMessage,leader_id) values('group2','ML','thisiskey','2');
insert into groups(name,topic,confirmMessage,leader_id) values('group3','IR','thisiskey','2');
select * from groups;


Drop Table if exists groupMemberAssosiation;
Create Table groupMemberAssosiation(
group_id int not null ,
member_id int not null
);
insert into groupMemberAssosiation(group_id,member_id) values('1','2');
insert into groupMemberAssosiation(group_id,member_id) values('2','2');
insert into groupMemberAssosiation(group_id,member_id) values('3','2');
insert into groupMemberAssosiation(group_id,member_id) values('1','1');
insert into groupMemberAssosiation(group_id,member_id) values('2','1');
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
insert into user(username, password, email,role) values('admin','admin','admin@123.com',1);

Drop Table if exists discussion;
Create Table discussion(
discuss_id int not null primary key AUTO_INCREMENT,
user_id int not null,
group_id int not null,
create_time timestamp not null default CURRENT_TIMESTAMP,
title varchar(256) not null,
content varchar(1024) not null, -- more reasonable than using TEXT.
read_num int not null default 0,
reply_num int not null default 0
);

insert into discussion(user_id, group_id, title, content) values('1','1','discussion1','This is discussion 1');
insert into discussion(user_id, group_id, title, content) values('1','2','discussion2','This is discussion 2');
insert into discussion(user_id, group_id, title, content) values('1','1','discussion3','This is discussion 3');

Drop Table if exists reply_discuss;
Create Table reply_discuss(
reply_id int not null primary key AUTO_INCREMENT,
discuss_id int not null,
user_id int not null,
reply_time timestamp not null default CURRENT_TIMESTAMP,
content varchar(512) not null,
foreign key (discuss_id) references discussion(discuss_id) on delete cascade
);

insert into reply_discuss(discuss_id, user_id, content) values(1, 2, 'This is reply1 for discussion1');
insert into reply_discuss(discuss_id, user_id, content) values(2, 2, 'This is reply1 for discussion2');
insert into reply_discuss(discuss_id, user_id, content) values(3, 2, 'This is reply1 for discussion3');
insert into reply_discuss(discuss_id, user_id, content) values(1, 1, 'This is reply2 for discussion1');

Drop Table if exists votes;
CREATE TABLE `votes` (
  `vote_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `vote_content` text,
  `voting` tinyint(1) NOT NULL,
  `begintime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `endtime` timestamp NOT NULL DEFAULT "00-00-00 00:00:00",
  PRIMARY KEY (`vote_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

Drop Table if exists vote_detail;
CREATE TABLE `vote_detail` (
`option_id` bigint(20) NOT NULL AUTO_INCREMENT,
`vote_id` bigint(20) DEFAULT NULL,
`option_order` int(11) DEFAULT NULL,
`vote_option` text,
`votes` int(11) DEFAULT NULL,
PRIMARY KEY (`option_id`)
) ENGINE=MyISAM AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;

Drop Table if exists vote_user_map;
CREATE TABLE `vote_user_map` (
`map_id` bigint(20) NOT NULL AUTO_INCREMENT,
`vote_id` bigint(20) DEFAULT NULL,
`user_id` int(11) DEFAULT NULL,
`votefor` int(11) DEFAULT NULL,
PRIMARY KEY (`map_id`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

Drop table if exists message;
Create table message (
message_id int primary key AUTO_INCREMENT,
type int not null default 0,	  -- 0 = first-time, 1 = delete from group,
								  -- 2 = delete discuss, 3 = delete reply
generator int not null default 0, -- note that always the system generate the message, 
receiver int not null,			  -- but the actual executor of the action is different.
time timestamp not null default CURRENT_TIMESTAMP,
content varchar(256) not null,
viewed tinyint(1) default 0
);

insert into message(type, generator,receiver, content) values(0,0,2,"test");

alter table vote_user_map add column vote_time timestamp;

