CREATE SEQUENCE mail_id_seq;

CREATE TABLE mail (
    id integer DEFAULT nextval('mail_id_seq') NOT NULL, 
    date date,
    mail_from varchar(250),
    mail_from_domain varchar(250),
    organisation varchar(250),
    mail_to text,
    mail_to_domain text,
    mail_cc text,
    in_reply_to text,
    mail_references text,
    header text,
    subject varchar(250),
    content text,
    path_to_attachments text,
    matched boolean,
    match_on date
);
