DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS polls;

CREATE TABLE users (
    id serial primary key ,
    username varchar(50) unique not null,
    password varchar(50) not null );


CREATE TABLE poll_names(
    poll_id serial primary key,
    poll_name varchar(30),
    question varchar(250));
    

CREATE TABLE poll_user(
    user_id integer not null,
    poll_id integer not null,
    FOREIGN KEY (user_id) references users (id),
    FOREIGN KEY (poll_id) references poll_names(poll_id));



CREATE TABLE poll_results(
    poll_id integer NOT NULL,
    ans varchar(15),
    FOREIGN KEY(poll_id) references poll_names(poll_id)
);