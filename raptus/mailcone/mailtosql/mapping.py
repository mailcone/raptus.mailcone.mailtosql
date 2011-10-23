import os
import grok
import logging
import rfc822
import time

from pyzmail import utils
from email import encoders
from stripogram import html2text
from datetime import datetime

from raptus.mailcone.app.config import local_configuration

from raptus.mailcone.mailtosql import interfaces
from raptus.mailcone.mailtosql import config

from raptus.mailcone.mails.interfaces import IMail
from raptus.mailcone.mails.contents import Attachment


log = logging.getLogger('raptus.mailcone.mailtosql')


class FieldMapper(grok.Adapter):
    grok.context(IMail)
    grok.implements(interfaces.IFieldMapper)
    grok.name('base.field.mapper')
    grok.baseclass()
    multi = False
    regex = None
    
    def __init__(self, context):
        self.mail = context
        self.name = getattr(self, 'grokcore.component.directive.name')
    
    def parse(self, mail):
        key = self.key
        if not isinstance(key, list):
            key = [key]
        for k in key:
            for field, value in mail.items():
                if not k == field:
                    continue
                value = self.modify(value)
                if self.multi:
                    self.add(value)
                else:
                    self.set(value)
                    break
    
    def modify(self, value):
        if self.regex is None:
            return value
        m = self.regex.match(value)
        if not m:
            log.warning("regex not match and can't be parsed. value: %s, regex: %s", (value, self.regex.pattern,))
            return value
        return m.group(1)

    def set(self, value):
        """ add a single attribute
        """
        setattr(self.mail, self.name, value)
        
    def add(self, value):
        """ store multivalue
        """
        li = getattr(self.mail, self.name)
        li.append(value)


class Subject(FieldMapper):
    grok.name('subject')
    key = 'Subject'

class From(FieldMapper):
    grok.name('mail_from')
    key = 'From'

class FromDomain(FieldMapper):
    grok.name('mail_from_domain')
    key = 'From'
    regex = config.DOMAIN_REGEX

class To(FieldMapper):
    grok.name('mail_to')
    key = 'To'
    multi = True

class ToDomain(FieldMapper):
    grok.name('mail_to_domain')
    key = 'To'
    multi = True
    regex = config.DOMAIN_REGEX

class CC(FieldMapper):
    grok.name('mail_cc')
    key = 'Cc'
    multi = True

class CCDomain(FieldMapper):
    grok.name('mail_cc_domain')
    key = 'Cc'
    regex = config.DOMAIN_REGEX

class BBC(FieldMapper):
    grok.name('mail_bbc')
    key = 'Bcc'
    multi = True

class BBCDomain(FieldMapper):
    grok.name('mail_bbc_domain')
    key = 'Bcc'
    multi = True
    regex = config.DOMAIN_REGEX

class Received(FieldMapper):
    grok.name('received')
    key = 'Received'
    multi = True

class Reply(FieldMapper):
    grok.name('reply_to')
    key = 'Reply-To'

class Sender(FieldMapper):
    grok.name('sender')
    key = 'Sender'

class XSourceIP(FieldMapper):
    grok.name('x_source_ip')
    key = 'X-SourceIP'

class Mime(FieldMapper):
    grok.name('mime_version')
    key = 'MIME-Version'

class Date(FieldMapper):
    grok.name('date')
    key = 'Date'
    def modify(self, value):
        return datetime.fromtimestamp(time.mktime(rfc822.parsedate(value)))


class ContentMapper(grok.Adapter):
    grok.context(IMail)
    grok.implements(interfaces.IContentMapper)
    grok.baseclass()

    def __init__(self, context):
        self.mail = context
        if self.mail.content is None:
            self.mail.content = ''

    def content(self, message):
        content = message.get_payload(decode=True)
        if content is None:
            return 
        return content


class PlainContentMapper(ContentMapper):
    grok.name('text/plain')
    
    def parse(self, message):
        self.mail.content += self.content(message)


class HTMLContentMapper(ContentMapper):
    grok.name('text/html')
    
    def parse(self, message):
        self.mail.content += html2text(self.content(message))


class AttachmentContentMapper(ContentMapper):
    # default Adapter if no other match
    grok.name('default')
    
    def parse(self, message):
        path = local_configuration['attachments']['output']
        filename = utils.sanitize_filename(message.get_filename(),None,None)
        filename = utils.handle_filename_collision(filename, os.listdir(path))
        fullpath = os.path.abspath(os.path.join(path, filename))
        with open(fullpath, 'w') as f:
            print >> f, self.content(message)

        attachment = Attachment()
        attachment.path = fullpath
        attachment.filesize = os.path.getsize(fullpath)
        self.mail.attachments.append(attachment)


