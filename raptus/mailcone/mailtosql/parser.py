import sys
import os

import transaction

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
            adapter.parse(dict(mail.items()))
        
        session.add(context)
        
        transaction.commit()
        
        session.close()
