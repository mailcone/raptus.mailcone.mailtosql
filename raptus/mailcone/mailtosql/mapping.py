import grok
from raptus.mailcone.mailtosql import interfaces
from raptus.mailcone.mails.interfaces import IMail

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
