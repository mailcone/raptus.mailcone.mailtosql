try:
    from sqlalchemy import *
    from sqlalchemy.ext.declarative import declarative_base
except ImportError:
    raise ImportError, u"mail-to-sql requires sqlalchemy."

# XXX must came from mail_to_sql.py 
from config import CONFIG 

Base = declarative_base ()

class Mail (Base):
    __tablename__ = CONFIG ['dbMailtableName']
    
    id = Column ('id', Integer, Sequence(CONFIG ['mail_id_seq_name']), primary_key=True)
    date = Column ('date', Date)
    mail_from = Column ('mail_from', String(250))
    mail_from_domain = Column ('mail_from_domain', String(250))
    organisation = Column ('organisation', String(250))
    mail_to = Column ('mail_to', Text)
    mail_to_domain = Column ('mail_to_domain', Text)
    mail_cc = Column ('mail_cc', Text)
    in_reply_to = Column ('in_reply_to', Text)
    mail_references = Column ('mail_references', Text)
    header = Column ('header', Text)
    subject = Column ('subject', String(250))
    content = Column ('content', Text)
    path_to_attachments = Column ('path_to_attachments', Text)
    matched = Column('matched', Boolean)
    match_on = Column ('match_on', Date)

    attachments = []
    
    def addAttachment (self, attachment):
        self.attachments.append (attachment)
    
    def getAttachments (self):
        return self.attachments
    
    def addAttachmentPath (self, path):
        self.path_to_attachments = path