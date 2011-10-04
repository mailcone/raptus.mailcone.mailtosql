"""This script provide a brige to store mails in a postgresql database 
(not tested with other sql databases).

arguments:

--config  takes a config file
--file    takes a file with a mail content

To use the script first configure the datas in config.py,
then you can give the script an stdin or a file like this:

echo "stdin data" | python mail_to_sql.py --config=main.cfg

python mail_to_sql.py --config=main.cfg --file=mail.txt
"""
import sys
import os
import getopt
import datetime
import logging

from data.attachment import Attachment
from data.mail import Mail

from controller.attachmentUtil import AttachmentUtil
from controller.databaseUtil import DatabaseUtil
from controller.mailParserUtil import MailParserUtil
from controller.loggers import Loggers
from controller.notificationSystem import NotificationSystem

from config import CONFIG

def parseData (data, logs, CONFIG):
    """ 
        parse a string to a dictionary by MailParserUtil
        return a dict with mail data parse from a string
    """
    logs.writeLog ('debug', 'info', 'mail_to_sql.py - parseData() - start')
    mpUtil = MailParserUtil (CONFIG, logs)
    mailDict = mpUtil.parseEmail (data)
    if not mailDict:
        logs.writeLog ('debug', 'error', 'mail_to_sql.py - parseData() - FAILED - mailDict is set')
        logs.writeLog ('error', 'error', 'parse pipe data failed')
        raise RuntimeError, u"mail_to_sql.py - parseData() - FAILED - mailDict is not set"
    else:
        logs.writeLog ('debug', 'info', 'mail_to_sql.py - parseData() - parse pipe data finished')
    return mailDict

def storeDataToDataobjects (mailDict, logs, CONFIG):
    """ 
        store parsed mail dictionary to mail object
        return mailObject
    """
    logs.writeLog ('debug', 'info', 'mail_to_sql.py - storeDataToDataobjects() - start')
    logs.writeLog ('debug', 'info', 'store parsed data in mail object') 
    try:
        newMail = Mail ()
        for key, value in mailDict.iteritems():
            if key == 'header_content':
                logs.writeLog ('debug', 'info', 'mail_to_sql.py - storeDataToDataobjects() - detecte mailDict key as header_content')
                # save header information to mail object
                for key, value in mailDict ['header_content'].iteritems():
                        newMail.__setattr__ (key,value)
            if key == 'attachments':
                logs.writeLog ('debug', 'info', 'mail_to_sql.py - storeDataToDataobjects() - detecte mailDict key as attachment')
                # for each attachment create an attachment obj
                # and add it to mail object
                for parsAtt in mailDict ['attachments']:
                    receiveTime = datetime.time (newMail.date.hour, newMail.date.minute)
                    attObj = Attachment (parsAtt.name,
                                         newMail.date,
                                         receiveTime,
                                         parsAtt.getvalue())
                    
                    newMail.addAttachment (attObj)
            else:
                # save rest of information to mail object
                # in our case it is the content
                newMail.__setattr__ (key,value)
        logs.writeLog ('debug', 'info', 'mail_to_sql.py - storeDataToDataobjects() - store parsed data to dataobjects')
        return newMail
    except Exception, e:
        logs.writeLog ('debug', 'error', 'mail_to_sql.py - storeDataToDataobjects() - FAILED - store parsed data to mail object failed - ' + str (e))
        logs.writeLog ('error', 'error', 'store parsed data to mail object failed - ' + str (e))
        raise RuntimeError, u"store parsed data to mail object failed - " + str(e)

def saveMailInDatabase (dbUtil, mail, logs):
    """ 
        save mail object in database 
    """
    logs.writeLog ('debug', 'info', 'mail_to_sql.py - saveMailInDatabase() - start')
    try:
        dbUtil.saveObject (mail)
        logs.writeLog ('info', 'info', 'add mail object to database successful')
        logs.writeLog ('debug', 'info', 'mail_to_sql.py - saveMailInDatabase() - save mail object to database')
    except Exception, e:
        logs.writeLog ('debug', 'error', 'mail_to_sql.py - saveMailInDatabase() - FAILED - save mail object to database failed - ' + str (e))
        logs.writeLog ('error', 'error', 'save mail object to database failed - ' + str (e))
        raise RuntimeError, u"save mail object to database failed - " + str (e)

def saveAttachmentsOnFilesystem (mail, dbUtil, logs, CONFIG):
    """  
        save all attachment files of mail object on file system 
        return true if everything is done
    """
    logs.writeLog ('debug', 'info', 'mail_to_sql.py - saveAttachmentsOnFilesystem() - start')
    logs.writeLog ('info', 'info', 'save attachment files')
    try:
        # initialize attachment utility
        attUtil = AttachmentUtil (CONFIG, logs)
        for att in mail.getAttachments ():
            logs.writeLog ('debug', 'info', "mail_to_sql.py - saveAttachmentsOnFilesystem() - save file: " + att.filename + " in path: " + att.filepath)
            # first we have to set mail id, because wasn't known 
            # when create attachment object
            att.mailId = mail.id
            attUtil.saveFile (att)
            logs.writeLog ('info', 'info', '    save attachment: ' + att.filename + 'on filesystem')
            mail.addAttachmentPath (att.filepath)
        dbUtil.saveObject(mail)
        logs.writeLog ('debug', 'info', "mail_to_sql.py - saveAttachmentsOnFilesystem() - update attachment path in mail entry")
        logs.writeLog ('info', 'info', 'update sql entrie with path to attachments')
        return True
    except Exception, e:
        logs.writeLog ('debug', 'error', "mail_to_sql.py - saveAttachmentsOnFilesystem() - FAILED - save attachments on filesystem failed - " + str (e))
        logs.writeLog ('error', 'error', "save attachments on filesystem failed - " + str (e))
        raise RuntimeError, u"save attachments on filesystem failed - " + str (e)

def createLogger ():
    """ 
        create to logfiles, an info and an error log
        return the to logs in a dict (keys: info, error)
    """
    logConfigdata = []
    logs = Loggers ()
    
    overall = {}
    overall ['id'] = 'overall'
    overall ['logname'] = CONFIG ['overall_name']
    overall ['path'] = CONFIG ['overalllogpath']
    overall ['filename'] = CONFIG ['overall_filename']
    overall ['separate'] = False
    overall ['logformat'] = CONFIG ['overall_format']
    logConfigdata.append (overall)
    
    infolog = {}
    infolog ['id'] = 'info'
    infolog ['logname'] = CONFIG ['infolog_name']
    infolog ['path'] = CONFIG ['infologpath']
    infolog ['filename'] = CONFIG ['infolog_filename']
    infolog ['separate'] = CONFIG ['infolog_separate']
    infolog ['logformat'] = CONFIG ['infolog_format']
    logConfigdata.append (infolog)
    
    errorlog = {}
    errorlog ['id'] = 'error'
    errorlog ['logname'] = CONFIG ['errorlog_name']
    errorlog ['path'] = CONFIG ['errorlogpath']
    errorlog ['filename'] = CONFIG ['errorlog_filename']
    errorlog ['separate'] = CONFIG ['errorlog_separate']
    errorlog ['logformat'] = CONFIG ['errorlog_format']
    logConfigdata.append (errorlog)
    
    #XXX: not parsed as boolend!!
    if CONFIG ['debugmode']:
        debuglog = {}
        debuglog ['id'] = 'debug'
        debuglog ['logname'] = CONFIG ['debug_name']
        debuglog ['path'] = CONFIG ['debugpath']
        debuglog ['filename'] = CONFIG ['debug_filename']
        debuglog ['separate'] = True
        debuglog ['logformat'] = CONFIG ['debug_format']
        logConfigdata.append (debuglog)
    
    for log in logConfigdata:
        logs.createLog (**log)

    return logs

def forkParseMail (pipeData, logs, CONFIG):
    """ 
        function which is called as a fork - run as a child
    """
    try:
        mailDict = parseData (pipeData, logs, CONFIG)
        dbUtil = DatabaseUtil (CONFIG, logs=logs)
        dbUtil.connect ()
        mail = storeDataToDataobjects (mailDict, logs, CONFIG)
        saveMailInDatabase (dbUtil, mail, logs)
        if mail.getAttachments ():
            saveAttachmentsOnFilesystem (mail, dbUtil, logs, CONFIG)
        dbUtil.closeConnection ()
    except  Exception, e:
        logs.writeLog ('debug', 'error', 'mail_to_sql.py - forkParseMail() - FAILED - ' + str (e))
        logs.writeLog ('error', 'error', 'mail_to_sql.py - forkParseMail() - FAILED - ' + str (e))
        raise RuntimeError, u"mail_to_sql.py - forkParseMail() - FAILED - " + str (e)

def savePipeData (pipeData, logs):
    """
        If script break, this function will save pipe data in a file, so the data's are not lost
    """
    logs.writeLog ('debug', 'info', 'mail_to_sql.py - savePipeData() - start')
    file = None
    
    if not os.path.isdir (CONFIG ['saveBrokenDataPath']):
        os.makedirs (CONFIG ['saveBrokenDataPath'])
    notUnique = True
    while notUnique:
        timestamp = datetime.datetime.now().strftime ("%Y%m%dT%H%M%S")
        # for loop is needed otherwise it could happen, that while-loop hangs in a
        # never ending loop
        for i in range (1, 50):
            filename = timestamp + '_' + str(i)
            file = os.path.join (CONFIG ['saveBrokenDataPath'], filename)
            if not os.path.exists(file):
                file = open (file, 'w')
                notUnique = False
                break
    file.write (pipeData)
    # log filename, if anything break and pipeData will be stored
    logs.writeLog ('debug', 'info', "mail_to_sql.py - save pipeData in: " + filename + " path: " + CONFIG ['saveBrokenDataPath'])
    logs.writeLog ('error', 'info', "mail_to_sql.py - save pipeData in: " + filename + " path: " + CONFIG ['saveBrokenDataPath'])

def parseConfig (filename):
    """
        arg:
        - filename: filename of cfg
        parse config file, given by --option parameter on call
    """
    try:
        import ConfigParser
    except ImportError:
        raise ImportError, u"mail-to-sql requires ConfigParser."    
    
    config = ConfigParser.ConfigParser()
    # optionxform needed for case sensitive
    config.optionxform = str
    config.readfp(open(filename))  
    
    for section in config.sections ():
        for option in config.options (section):
            # BOOLEAN_VALUES is defined in config.py
            if option in CONFIG ['BOOLEAN_VALUES']:
                CONFIG [option] = config.getboolean (section, option)
            else:
                CONFIG [option] = config.get (section, option, raw=True)

def main():
    """ 
        main function
    """
    pipeData = "" #store data get from pipe
    
    if len(sys.argv) == 1:
        print __doc__
        sys.exit(0)
    
    # parse command line options    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help", "file=", "config="])
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)
    
    # process options
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print __doc__
            sys.exit(0)

        # parse config file and initialize logs
        if opt in ("--config"):
            try: 
                parseConfig (arg)
                os.environ ["TMPDIR"] = CONFIG ["tempDir"]
                logs = createLogger ()
                if CONFIG.has_key ('sendMailnotification') and CONFIG ['sendMailnotification']:
                    notificationMail = NotificationSystem (CONFIG ['sender'], 
                                                           CONFIG ['receivers'], 
                                                           CONFIG ['smtpserver'], 
                                                           CONFIG ['smtpauth'], 
                                                           CONFIG ['smtpuser'], 
                                                           CONFIG ['smtppassword'], 
                                                           CONFIG ['subject'])
                    notificationMail.setLogs (logs)
                    notificationMail.createHeader ()
                    logs.setNotificationMail (notificationMail)
                logs.startOverall ()
            except  Exception, e:
                raise RuntimeError, u"Could not parse config file ("+ str(e) + ")"
        
        if opt in ("--file"):
            try:
                logs.writeLog ('debug', 'info', "mail_to_sql.py - main() - get data in file")
                sourcefile = open (arg, 'r')
                pipeData = sourcefile.read ()
                sourcefile.close ()
                logs.writeLog ('debug', 'info', "mail_to_sql.py - main() - data: \n\n" + pipeData + "\n")
            except Exception, e:
                logs.writeLog ('debug', 'error', "mail_to_sql.py - main() - FAILED - try read received file - Error: " + str(e))
                logs.writeLog ('error', 'error', "mail_to_sql.py - main() - FAILED - try read received file - Error: " + str(e))
    
    # detects whether have pipe line parsing in
    try:
        if not sys.stdin.isatty():
            logs.writeLog ('debug', 'info', "get data over as stdin\n")
            pipeData = sys.stdin.read()
            logs.writeLog ('debug', 'info', "mail_to_sql.py - main() - data: \n\n" + pipeData + "\n")
    except Execption, e:
        logs.writeLog ('debug', 'error', "mail_to_sql.py - main() - FAILED - problems with sys.stdin - Error: " + str(e))
        logs.writeLog ('error', 'error', "mail_to_sql.py - main() - FAILED - problems with sys.stdin - Error: " + str(e))
    
    try:
        child_pid = os.fork ()
        if child_pid == 0:
            logs.writeLog ('debug', 'info', "mail_to_sql.py - main() - start fork process: PID# %s" % os.getpid())
            logs.writeLog ('info', 'info', "start child proccess")
            
            forkParseMail (pipeData, logs, CONFIG)
            
            logs.writeLog ('debug', 'info', "mail_to_sql.py - main() - end fork process: PID# %s" % os.getpid())
            logs.writeLog ('info', 'info', "end mail_to_sql successful")
            
            blnDelEmptyError = False
            if CONFIG ['errorlog_separate'] and CONFIG ['error_separatedLogs_deleteEmpty']:
                blnDelEmptyError = True
            logs.stopOverall (True)
            logs.closeLogs (blnDelEmptyError)
            sys.exit (0)
        else:
            # end main process
            logs.writeLog ('debug', 'info', "mail_to_sql.py - main() - end main process: PID# %s" % os.getpid())
            sys.exit(0)
    except Exception, e:
        
        logs.writeLog ('error', 'error', "script FAILED - Error: " + str(e))
        logs.writeLog ('debug', 'error', "mail_to_sql.py - main() - script FAILED - Error: " + str(e))
        try:
            savePipeData (pipeData, logs)
        except Exception, e:
            logs.writeLog ('debug', 'error', "mail_to_sql.py - main() - could not save pipeData - Error: " + str(e) +" \n pipeData: \n" + pipeData)
            logs.writeLog ('error', 'error', "could not save pipeData - Error: " + str(e) +" \n pipeData: \n" + pipeData)
        finally:
            if logs.hasDebug ():
                logs.writeLog ('error', 'error', "INFORMATION - DEBUG MODE ON - Name of debug file: " + logs.getLogfilename ('debug'))
            if CONFIG.has_key ('sendMailnotification') and CONFIG ['sendMailnotification']:
                notificationMail.sendNotificationMail ()
            logs.writeLog ('info', 'info', "send mail notification")
            logs.writeLog ('info', 'error', "ERROR INFOMATION in error file: " + logs.getLogfilename ('error'))
            logs.stopOverall (False)
            logs.closeLogs ()
            sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
