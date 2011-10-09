import os
import grok

from pyzmail import utils
from email import encoders
from stripogram import html2text

from raptus.mailcone.app import config
from raptus.mailcone.mailtosql import interfaces
from raptus.mailcone.mails.interfaces import IMail
from raptus.mailcone.mails.contents import Attachment



class FieldMapper(grok.Adapter):
    grok.context(IMail)
    grok.implements(interfaces.IFieldMapper)
    grok.name('base.field.mapper')
    grok.baseclass()
    
    def __init__(self, context):
        self.mail = context
        self.name = getattr(self, 'grokcore.component.directive.name')
    
    def parse(self, items):
        for key in self.keys:
            value = items.get(key, None)
            if value is not None:
                break
        setattr(self.mail,self.name, value)





class From(FieldMapper):
    grok.name('mail_from')
    keys = ['From']







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
    grok.name('')
    
    def parse(self, message):
        path = config.local_configuration['attachments']['output']
        filename = utils.sanitize_filename(message.get_filename(),None,None)
        filename = utils.handle_filename_collision(filename, os.listdir(path))
        fullpath = os.path.abspath(os.path.join(path, filename))
        with open(fullpath, 'w') as f:
            print >> f, self.content(message)

        attachment = Attachment()
        attachment.path = fullpath
        attachment.filesize = os.path.getsize(fullpath)
        self.mail.attachments.append(attachment)


