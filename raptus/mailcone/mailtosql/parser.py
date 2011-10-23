import sys
import os

import transaction

from email.message import Message

from zope import component
from z3c.saconfig import Session

from pyzmail import message_from_string

from raptus.mailcone.mails.contents import Mail
from raptus.mailcone.mailtosql import interfaces





class Parser(object):
    def __init__(self, data):
        
        mail = message_from_string(data)
        
        session = Session()
        
        context = Mail()
        
        for name, adapter in component.getAdapters((context,), interfaces.IFieldMapper):
            adapter.parse(mail)
        
        payload = mail.get_payload()
        if isinstance(payload, str):
            mesg = Message()
            mesg.set_type('text/plain')
            mesg.set_payload(payload)
            payload = [mesg]
        for message in payload:
            type = message.get_content_type()
            adapter = component.queryAdapter(context, interface=interfaces.IContentMapper, name=type)
            if adapter is None:
                adapter = component.getAdapter(context, interface=interfaces.IContentMapper, name='default')
            adapter.parse(message)
        
        session.add(context)
        
        transaction.commit()
        
        session.close()
