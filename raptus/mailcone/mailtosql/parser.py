import os
import sys
import time
import hashlib

import transaction

from email.message import Message

from zope import component
from z3c.saconfig import Session

from pyzmail import message_from_string

from raptus.mailcone.mails.contents import Mail
from raptus.mailcone.app.config import local_configuration

from raptus.mailcone.mailtosql import interfaces





class Parser(object):
    def __init__(self, data):
        
        session = Session()
        context = Mail()
        mail = message_from_string(data)
        
        for name, adapter in component.getAdapters((context,), interfaces.IFieldMapper):
            adapter.parse(mail)
        
        for part in mail.mailparts:
            type = part.type
            adapter = component.queryAdapter(context, interface=interfaces.IContentMapper, name=type)
            if adapter is None:
                adapter = component.getAdapter(context, interface=interfaces.IContentMapper, name='default')
            adapter.parse(part)
        
        backuppath = local_configuration['backup'].get('backup', '')
        if os.path.isdir(backuppath):
            name = time.strftime('%Y%m%d%H%M')
            path = os.path.join(backuppath, '%s.mail' % name)
            counter = 0
            while os.path.isfile(path):
                path = os.path.join(backuppath, '%s_%s.mail' % (name, counter,))
                counter += 1
            context.original_path = os.path.abspath(path)
            with open(path, 'w') as f:
                f.write(data)
            f.close()

        context.hash = hashlib.md5(data).hexdigest()

        session.add(context)
        transaction.commit()
        session.close()
