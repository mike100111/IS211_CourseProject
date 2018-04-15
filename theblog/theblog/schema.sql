drop table if exists post;
create table post (
  id integer primary key autoincrement,
  title text not null,
  published date not null,
  author integer not null, 
  content text not null,
  permalink text null,
  display bit not null,
  category text null
);