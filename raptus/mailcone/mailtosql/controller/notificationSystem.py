import datetime
import smtplib
from email.mime.text import MIMEText

class NotificationSystem (object):
    
    sender = None
    receivers = None
    smtpserver = None
    smtpuser = None
    smtppasswd = None
    smtpauthrequeried = False
    subject = None
    message = ""
    logs = None
    
    def __init__ (self, sender, receivers, smtp, auth, user, passwd, subject):
        """
            Constructor
        """
        self.sender = sender
        self.receivers = receivers
        self.smtpserver = smtp
        self.smtpuser = user
        self.smtppasswd = passwd
        self.smtpauthrequeried = auth
        self.subject = subject
    
    def createHeader (self):
        """
            create header of mail message
        """
        try:
            self.message = "This is an automatic notification of mail_to_sql\n\n"
            now = datetime.datetime.now ()
            self.addLine("mail_to_sql start: " + now.strftime("%d.%m.%Y %H:%M") + "\n")
        except Exception, e:
            raise RuntimeError, u"NotificationSystem - createHeader() - failed " + str (e)
        
    def createFooter (self):
        """
            create footer of mail message
        """
        try:
            now = datetime.datetime.now ()
            self.addLine("\nMail_to_sql end: " + now.strftime("%d.%m.%Y %H:%M"))
        except Exception, e:
            raise RuntimeError, u"NotificationSystem - createFooter() - failed " + str (e)
    
    def addLine (self, msg):
        """
            add new line to mail message
        """
        try:
            self.message = self.message + msg + "\n"
        except Exception, e:
            raise RuntimeError, u"NotificationSystem - addLine() - failed " + str (e)
    
    def sendNotificationMail (self):
        """
            create mail object, 
            set self.message as content and
            send mail
        """
        try:
            msg = MIMEText (self.message)
            msg['From'] = self.sender
            msg['To'] = ", ".join (self.receivers)
            msg['Subject'] = self.subject
    
            smtpObj = smtplib.SMTP(self.smtpserver)
            if self.smtpauthrequeried:
                smtpObj.login(self.smtpuser, self.smtppasswd)
            smtpObj.sendmail(self.sender, self.receivers, msg.as_string())
            self.logs.writeLog ('info', 'info', "sent email successful")
        except Exception, e:
            self.logs.writeLog ('info', 'error', "send mail failed")
            self.logs.writeLog ('debug', 'error', "NotificationSystem - sendNotificationMail () - send mail failed - " + str (e))
            raise RuntimeError, u"NotificationSystem - sendNotificationMail () - send mail failed - " + str (e)
    
    def setLogs (self, logs):
        """
            add mail message to object
            not in constructor because is initialized befor logs
        """
        self.logs = logs