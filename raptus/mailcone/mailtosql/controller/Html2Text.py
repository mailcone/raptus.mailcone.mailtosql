# -*- coding: utf-8 -*-
"""

File      :   Html2Text.py
Project   :   Raptus Helpdesk Mailend
Author    :   Guy Zuercher
Created   :   9.5.2007

"""

from formatter import NullWriter
from formatter import AbstractFormatter
from htmllib import HTMLParser

class MailBodyWriter(NullWriter):
    """
    """
    
    pieces = []
    
    def __init__(self): pass
    
    def flush(self): pass
    
    def new_alignment(self, align): pass
    
    def new_font(self, font): pass
    
    def new_margin(self, margin, level): pass

    def new_spacing(self, spacing): pass
    
    def new_styles(self, styles): pass
    
    def send_paragraph(self, blankline):
        self.pieces.append("\n\n" * blankline)
        
    def send_line_break(self):
        self.pieces.append("\n")

    def send_hor_rule(self, *args, **kw): 
        self.pieces.append("----------------------------------------\n")
        
    def send_label_data(self, data): pass

    def send_flowing_data(self, data):
        self.pieces.append(data)
        
    def send_literal_data(self, data):
        self.pieces.append(data)
    
    def getMailText(self):
        return " ".join(self.pieces)


"""
#####################################################################
"""


class Html2Text:
    """
        This class converts an html formatted email to plain text
    """

    htmlString = ""

    def __init__(self, htmlCode):
        """ 
            Class Constructor 
        """
        self.htmlString = htmlCode


    def convert(self):
        """
            converting function
        """
        writer = MailBodyWriter()
        parser = HTMLParser(AbstractFormatter(writer))
        parser.feed(self.htmlString)
        parser.close()
        return writer.getMailText()
