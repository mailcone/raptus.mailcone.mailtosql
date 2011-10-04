import email
import email.Parser  
from email.Header import decode_header
import Html2Text

import re
from StringIO import StringIO

import chardet
from dateutil.parser import *


class MailParserUtil (object):
    """
        This utility is used for parse mails from a pipe.
    """
    pipeData = None
    parseObj = None # contain the parsed object from email.message_from_string ()
    logs = None # dict with logfiles
    
    def __init__ (self, CONFIG, logs=logs):
        """
            Constructor
        """
        self.CONFIG = CONFIG
        self.logs = logs
    
    def _parseDate(self, datastr):
        """ 
            parse a date string object to a datetime object
            return a datetime object
            
            RFC 5322 point 3.3. Date and Time Specification
            declare a fix number of characters, which are needed.
            In this case we decide to cut just this characters in
            a first step. Maybe there would be an implementation of
            regex in the future. 
        """
        if self.logs: self.logs.writeLog ('debug', 'info', 'MailParserUtil - _parseDate() - start')
        try:
            # maybe in future with regex
            # parse str with dateutil    
            return parse(datastr [:31])
        except Exception, e:
            if self.logs: self.logs.writeLog ('debug', 'error', 'MailParserUtil - _parseDate() - FAILED - ' + str(e))
            if self.logs: self.logs.writeLog ('error', 'error', 'parse date string of pipe data failed - ' + str(e))
            raise RuntimeError, u"MailParserUtil - _parseDate() - FAILED - " + str(e)
    
    def _parseStrWithPattern (self, parseStr, pattern):
        """
            returns a parsed str with pattern condition
        """
        if self.logs: self.logs.writeLog ('debug', 'info', 'MailParserUtil - _parseStrWithPattern() - start - PARAM: parseStr: ' + parseStr + ' pattern: ' + pattern)
        try:
            p = re.search (pattern, parseStr.strip ())
            if self.logs: self.logs.writeLog ('debug', 'info', 'MailParserUtil - _parseDate() - re.search() - Identified parse string (' + parseStr + ') as: ' + str(p.group(1)))
            if self.logs: self.logs.writeLog ('info', 'info', '        Identified parse string (' + parseStr + ') as: ' + str(p.group(1)))
            return p.group (1)
        except Exception, e:
            if self.logs: self.logs.writeLog ('debug', 'error', 'MailParserUtil - _parseStrWithPattern() - FAILED - ' + str(e))
            if self.logs: self.logs.writeLog ('error', 'error', 'parse string with pattern failed - ' + str(e))
            raise RuntimeError, u"MailParserUtil - _parseStrWithPattern() - FAILED - " + str(e)
    
    def _getDecodeHeaderString(self, string):
        """
            decode string with header information
            and encode string to utf-8
        """
        if self.logs: self.logs.writeLog ('debug', 'info', 'MailParserUtil - _getDecodeHeaderString() - start - PARAM: string: ' + string)
        try:
            header_and_encoding = email.Header.decode_header(string) 
            list = []
            for part in header_and_encoding:
                if part[1] is None:   
                    list.append (part[0])
                else:
                    upart = (part[0]).decode(part[1])
                    list.append (upart.encode('utf-8'))
            return ' '.join(list)
        except Exception, e:
            if self.logs: self.logs.writeLog ('debug', 'error', 'MailParserUtil - _getDecodeHeaderString() - FAILED - ' + str(e))
            if self.logs: self.logs.writeLog ('error', 'error', 'search for decode in mail header failed - ' + str(e))
            raise RuntimeError, u"MailParserUtil - _getDecodeHeaderString() - FAILED - " + str(e)
    
    def _parseHeader(self):
        """ 
            parse the whole header data for received mail data
            return a dict with parsed header data, keys:
                - header (whole header)
                - mail_from
                - mail_from_domain
                - mail_to
                - mail_to_domain
                - date (datetime object)
                - mail_cc
                - organisation
                - mail_references
                - in_reply_to
                - subject
        """
        if self.logs: self.logs.writeLog ('debug', 'info', 'MailParserUtil - _parseHeader() - start')
        if self.logs: self.logs.writeLog ('info', 'info', '    parse header data')
        try:
            headerDict = {}
            parseObj = self.parseObj
    
            # convert header list to a string
            headerDict ['header'] = ''
            for part in parseObj._headers:
                headerDict ['header'] += ' '.join (part) + '\n'
        
            # parse from and from_domain strings
            fromstr = parseObj ['From']
            if not fromstr:
                if self.logs: self.logs.writeLog ('debug', 'error', 'MailParserUtil - _parseHeader() - FAILED - fromstr is not set')
                if self.logs: self.logs.writeLog ('error', 'error', "don't found any FROM address in pipe data!")
                raise ValueError, u"MailParserUtil - _parseHeader() - fromstr is not set"
            mail_from = self._parseStrWithPattern (fromstr, self.CONFIG ['FROM_PATTERN'])
            if self.logs: self.logs.writeLog ('info', 'info', "        parse 'FROM' string")
            # pattern ignore '"', so we have to replace it 
            headerDict ['mail_from'] = mail_from.replace ('"', '')
            mail_from_domain = self._parseStrWithPattern (fromstr, self.CONFIG ['FROM_DOM_PATTERN'])
            if self.logs: self.logs.writeLog ('info', 'info', "        parse 'FROM DOMAIN' string")
            # pattern ignore '"', so we have to replace it 
            headerDict ['mail_from_domain'] = mail_from_domain.replace ('"', '') 
              
            # parse to and to_domain strings
            tostr = parseObj ['To']  
            if not tostr:
                if self.logs: self.logs.writeLog ('debug', 'error', 'MailParserUtil - _parseHeader() - FAILED - tostr is not set')
                if self.logs: self.logs.writeLog ('error', 'error', "don't found any TO address in pipe data!")
                raise ValueError, u"MailParserUtil - _parseHeader() - tostr is not set"
            if self.logs: self.logs.writeLog ('info', 'info', "        parse 'TO' string")
            mail_to = self._parseStrWithPattern (tostr, self.CONFIG ['TO_PATTERN'])
            # pattern ignore '"', so we have to replace it
            headerDict ['mail_to'] = mail_to.replace ('"', '')
            mail_to_domain =  self._parseStrWithPattern (tostr, self.CONFIG ['TO_DOM_PATTERN'])
            if self.logs: self.logs.writeLog ('info', 'info', "        parse 'TO DOMAIN' string")
            # pattern ignore '"', so we have to replace it
            headerDict ['mail_to_domain'] = mail_to_domain.replace ('"', '')
            
            # parse to and to_domain strings
            datestr = parseObj ['Date']
            if not datestr:
                if self.logs: self.logs.writeLog ('debug', 'error', 'MailParserUtil - _parseHeader() - FAILED - datestr is not set')
                if self.logs: self.logs.writeLog ('error', 'error', "don't found any DATE string in pipe data!")
                raise ValueError, u"MailParserUtil - _parseHeader() - FAILED - datestr is not set"
            if self.logs: self.logs.writeLog ('info', 'info', "        parse 'DATE' string")
            headerDict ['date'] = self._parseDate(datestr)
            
            # parse cc strings
            if parseObj ['CC']: 
                ccstr = parseObj ['CC']
                mail_cc = self._parseStrWithPattern (ccstr, self.CONFIG ['CC_PATTERN'])
                if self.logs: self.logs.writeLog ('info', 'info', "        parse 'CC' string")
                # pattern ignore '"', so we have to replace it
                headerDict ['mail_cc'] = mail_cc.replace ('"', '')
            
            # parse organization strings
            if parseObj ['Organization']: 
                if self.logs: self.logs.writeLog ('info', 'info', "        parse 'ORGANIZATION' string")
                headerDict ['organisation'] = self._getDecodeHeaderString (parseObj ['Organization'])
            
            # parse references strings
            if parseObj ['References']:
                references = parseObj ['References']
                if self.logs: self.logs.writeLog ('info', 'info', "        parse 'REFERENCES' string")
                headerDict ['mail_references'] = self._parseStrWithPattern (references, self.CONFIG ['REFERENCES_PATTERN'])
            
            # parse in-reply-to strings
            if parseObj ['In-Reply-To']:
                in_reply_to = parseObj ['In-Reply-To']
                if self.logs: self.logs.writeLog ('info', 'info', "        parse 'IN-REPLY-TO' string")
                headerDict ['in_reply_to'] = self._parseStrWithPattern (in_reply_to, self.CONFIG ['IN_REPLY_TO_PATTERN'])
            
            # parse subject strings
            if parseObj ['Subject']:
                if self.logs: self.logs.writeLog ('info', 'info', "        parse 'SUBJECT' string")
                headerDict ['subject'] = self._getDecodeHeaderString (parseObj ['Subject'])
        
            return headerDict
        except Exception, e:
            if self.logs: self.logs.writeLog ('debug', 'error', 'MailParserUtil - _parseHeader() - FAILED - ' + str (e))
            if self.logs: self.logs.writeLog ('error', 'error', "parse header part of pipe data failed")
            raise ValueError, u"MailParserUtil - _parseHeader() - FAILED - " + str (e)
    
    def _parsePlainContent(self, part):
        """ 
            parse the content of received data in text/plain format
        """
        if self.logs: self.logs.writeLog ('debug', 'info', 'MailParserUtil - _parsePlainContent() - start')
        try:
            pl = part.get_payload ()
            
            if self.parseObj.has_key ('Content-Transfer-Encoding'):
                if self.parseObj ['Content-Transfer-Encoding'] == 'base64':
                    # decoding of a base64 encode email
                    if self.logs: self.logs.writeLog ('debug', 'info', 'MailParserUtil - _parsePlainContent() - Content-Transfer-Encoding: base64')
                    if self.logs: self.logs.writeLog ('info', 'info', '        Guessed encoding of content: base64')
                    try:
                        import base64
                    except Exception, e:
                        if self.logs: self.logs.writeLog ('debug', 'error', 'MailParserUtil - _parsePlainContent() - import base64 FAILED - ' + str (e))
                        if self.logs: self.logs.writeLog ('error', 'error', "import base64 FAILED")
                        raise ImportError, u"MailParserUtil - _parsePlainContent() - import base64 FAILED - " + str (e)
                    pl = base64.b64decode (pl)

                if self.parseObj ['Content-Transfer-Encoding'] == 'quoted-printable':
                    # decoding of a quoted-printable encode email
                    if self.logs: self.logs.writeLog ('debug', 'info', 'MailParserUtil - _parsePlainContent() - Content-Transfer-Encoding: quoted-printable')
                    if self.logs: self.logs.writeLog ('info', 'info', '        Guessed encoding of content: quoted-printable')
                    try:
                        import quopri
                    except Exception, e:
                        if self.logs: self.logs.writeLog ('debug', 'error', 'MailParserUtil - _parsePlainContent() - import quopri FAILED - ' + str (e))
                        if self.logs: self.logs.writeLog ('error', 'error', "import quopri FAILED")
                        raise ImportError, u"MailParserUtil - _parsePlainContent() - import quopri FAILED - " + str (e)
                    
                    try:
                        pl = quopri.decodestring (pl)
                        pl = self._decToUniAndEncUtf(pl)
                    except Exception, e:
                        if self.logs: self.logs.writeLog ('debug', 'error', 'MailParserUtil - _parsePlainContent() - parse quoted-printable - FAILED - ' + str (e))
                        if self.logs: self.logs.writeLog ('error', 'error', "parse content with encoding quoted-printable failed - " + str (e))
                        raise RuntimeError, u"MailParserUtil - _parsePlainContent() - parse quoted-printable - FAILED - " + str (e)
            else:
                # default decoding
                pl = self._decToUniAndEncUtf(pl)
            return pl
        except Exception, e:
            if self.logs: self.logs.writeLog ('debug', 'error', 'MailParserUtil - _parsePlainContent() - FAILED - ' + str (e))
            if self.logs: self.logs.writeLog ('error', 'error', "parse plain content failed - " + str (e))
            raise RuntimeError, u"MailParserUtil - _parsePlainContent() - FAILED - " + str (e)

    def _decToUniAndEncUtf (self, pl):
        """ 
            detect encoding of pl, convert to unicode and encode in utf-8
        """ 
        denc = chardet.detect(pl)["encoding"]
        if self.logs: self.logs.writeLog ('debug', 'info', 'MailParserUtil - _parsePlainContent() - Content-Transfer-Encoding: ' + str(denc))
        if self.logs: self.logs.writeLog ('info', 'info', '        Guessed encoding of content: ' + str(denc))
        pl = unicode(pl, denc)
        pl = pl.encode ('utf-8')
        return pl

    def _parseHtmlContent(self, part):
        """
            parse the content of received data in text/html format
        """
        if self.logs: self.logs.writeLog ('debug', 'info', 'MailParserUtil - _parseHtmlContent() - start')
        try:
            if self.logs: self.logs.writeLog ('debug', 'info', 'MailParserUtil - _parseHtmlContent() - call Html2Text.Html2Text')
            parser = Html2Text.Html2Text (part.get_payload(decode = False))
            return parser.convert()
        except Exception, e:
            if self.logs: self.logs.writeLog ('debug', 'error', 'MailParserUtil - _parseHtmlContent() - FAILED - ' + str (e))
            if self.logs: self.logs.writeLog ('error', 'error', "parse html content failed - " + str (e))
            raise RuntimeError, u"MailParserUtil - _parseHtmlContent() - FAILED - " + str (e)
    
    def _parseAttachment(self, message_part):
        """ 
            parse the attachments of an email
            
            returns an StringIO file. 
        """
        if self.logs: self.logs.writeLog ('debug', 'info', 'MailParserUtil - _parseAttachment() - start')
        content_disposition = message_part.get("Content-Disposition", None)
        if content_disposition:
            dispositions = content_disposition.strip().split(";")
            if bool(content_disposition and dispositions[0].lower() == "attachment"):
                if self.logs: self.logs.writeLog ('debug', 'info', 'MailParserUtil - _parseAttachment() - parse attachment')
                try:
                    if self.logs: self.logs.writeLog ('info', 'info', '    parse attachment file')
                    file_data = message_part.get_payload(decode=True)
                    attachment = StringIO(file_data)
                    attachment.content_type = message_part.get_content_type()
                    attachment.size = len(file_data)
                    if self.logs: self.logs.writeLog ('info', 'info', '        file size: ' + str (attachment.size))
                    attachment.name = None
                    attachment.create_date = None
                    attachment.mod_date = None
                    attachment.read_date = None
        
                    for param in dispositions[1:]:
                        name,value = param.split("=")
                        name = name.lower()
                        if name.find ("filename"):
                            # have to replace ("), otherwise, files wouldn't be stored right
                            attachment.name = value.replace ('"', '')
                            if self.logs: self.logs.writeLog ('debug', 'info', 'MailParserUtil - _parseAttachment() - find filename: ' + attachment.name)
                            if self.logs: self.logs.writeLog ('info', 'info', '        file name: ' + str (attachment.name))
                        else:
                            if self.logs: self.logs.writeLog ('debug', 'error', 'MailParserUtil - _parseAttachment() - FAILED - do not find any filename')
                            if self.logs: self.logs.writeLog ('error', 'error', 'find no filename for attachment in pipe data, parseAttachment failed')
                            raise ValueError, u"find no filename for attachment in pipe data"
                        # XXX: at the moment not importent maybe later
                        #elif name == "create-date":
                        #    attachment.create_date = value  #TODO: datetime
                        #elif name == "modification-date":
                        #    attachment.mod_date = value #TODO: datetime
                        #elif name == "read-date":
                        #    attachment.read_date = value #TODO: datetime
                    if self.logs: self.logs.writeLog ('debug', 'info', 'MailParserUtil - _parseAttachment() - finish parse attachment')
                    return attachment
                except Exception, e:
                    if self.logs: self.logs.writeLog ('debug', 'error', 'MailParserUtil - _parseAttachment() - FAILED - ' + str (e))
                    if self.logs: self.logs.writeLog ('error', 'error', "parse attachment failed - " + str (e))
                    raise RuntimeError, u"MailParserUtil - _parseAttachment() - FAILED - " + str (e)
                
    def parseEmail (self, pipeData):
        """ 
            parse a string with mail content an returns a dict
            parameters:
                pipeData: email string
                
            return: a dict with following keys:
            - header_content
                - header (whole header)
                - mail_from
                - mail_from_domain
                - mail_to
                - mail_to_domain
                - date (datetime object)
                - mail_cc
                - organisation
                - mail_references
                - in_reply_to
                - subject
            - content
            - attachments (list of attachments)
                - one attachment is an StringIO with the following keys:
                    - content_type
                    - size
                    - name (filename)
        """
        if self.logs: self.logs.writeLog ('debug', 'info', 'MailParserUtil - parseEmail() - start')
        if self.logs: self.logs.writeLog ('info', 'info', 'start data parsing')
        resultDict = {}
        
        if pipeData:
            self.pipeData = pipeData
        else:
            if self.logs: self.logs.writeLog ('debug', 'error', 'MailParserUtil - parseEmail() - FAILED - do not get any pipe data')
            if self.logs: self.logs.writeLog ('error', 'error', "parser do not get any pipe data")
            raise ValueError, u"MailParserUtil - parseEmail() - FAILED - do not get any pipe data"
        
        try:
            # parse Mail with email.Parser
            self.parseObj = email.message_from_string (self.pipeData)
            # parse the whole header an returns a dict, with parsed values.
            resultDict ['header_content'] = self._parseHeader()
            
            attachments = []
            body = ""
            html = ""
            content = ""
            
            if self.parseObj.is_multipart() and self.logs:
                if self.logs: self.logs.writeLog ('debug', 'info', 'MailParserUtil - parseEmail() - received mail object is a multipart email')
                if self.logs: self.logs.writeLog ('info', 'info', '    received mail object is a multipart email')
            
            for part in self.parseObj.walk():
                attachment = self._parseAttachment (part)
                if attachment:
                    attachments.append(attachment)
                
                elif part.get_content_type() == "text/plain":
                    if self.logs: self.logs.writeLog ('debug', 'info', 'MailParserUtil - parseEmail() - received mail object has text/plain content')
                    if self.logs: self.logs.writeLog ('info', 'info', '    received mail object has text/plain content')
                    body = self._parsePlainContent(part) + '\n'
                
                # Some problems with html, parse two times by one test
                elif part.get_content_type() == "text/html":
                    if self.logs: self.logs.writeLog ('debug', 'info', 'MailParserUtil - parseEmail() - received mail object has text/html content')
                    if self.logs: self.logs.writeLog ('info', 'info', '    received mail object has text/html content')
                    html = self._parseHtmlContent(part)
            
            if html:
                resultDict ['content'] = html
            else:
                resultDict ['content'] = body
            resultDict ['attachments'] = attachments
            
            return resultDict
        except Exception, e:
            if self.logs: self.logs.writeLog ('debug', 'error', 'MailParserUtil - parseEmail() - FAILED - ' + str (e))
            if self.logs: self.logs.writeLog ('error', 'error', "parse pipe data as mail failed - " + str (e))
            raise RuntimeError, u"MailParserUtil - parseEmail() - FAILED - " + str (e)