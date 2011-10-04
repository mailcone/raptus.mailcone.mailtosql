import logging
import os
import datetime

class Loggers (object):
    logs = {}
    overallMsg = ''
    notificationMail = ''
    
    def getLogfile (self, path, logfile, separate):
        """
            Check if the logfiles exists, else it will create
            return path to logfile
        """
        if not os.path.isdir (path):
            os.makedirs (path)
        # generate a filename which doesn't exist, with timestamp and suffix number
        filepath = ''
        if separate:
            timestamp = datetime.datetime.now().strftime ("%Y%m%d-%H%M%S")
            filename =  timestamp + '-' + logfile + '.log'
            filepath = os.path.join (path, filename)
            if os.path.isfile (filepath):
                i=0
                while True:
                    filename = timestamp + '-' + logfile + '-' + str (i) + '.log'
                    filepath = os.path.join (path, filename) 
                    if not os.path.isfile (filepath):
                        break
                    i += 1
        else:
            filename = logfile + '.log'
            filepath = os.path.join (path, filename)
        
        if not os.path.isfile (filepath):
            # must be done like this to create file 
            # because, logging.FileHandler doesn't work if file not exists
            file = open (filepath, 'w')
            file.close ()
        return filepath
    
    def createLog (self, id, path, filename, logname, logformat, separate):
        """
            create log
        """
        logfile = self.getLogfile (path, filename, separate)
        log = logging.getLogger (logname)
        log.setLevel (logging.INFO)
        lformatter = logging.Formatter(logformat)
        lhandler = logging.FileHandler(logfile)
        lhandler.setFormatter(lformatter)
        log.addHandler(lhandler)
        
        self.logs [id] = {'log' : log, 'handler' : lhandler}
    
    def setNotificationMail (self, mail):
        """
            set notificationMail object
        """
        self.notificationMail = mail
    
    def writeLog (self, logname, level, msg):
        """
            write line in log
        """
        # write every debug message in notificationMail.message
        if self.notificationMail and logname == 'debug':
            mailLine = level + " - " + msg
            self.notificationMail.addLine (mailLine)
        
        if logname == 'debug' and not self.logs.has_key ('debug'):
            return
        
        if level == 'info':
            self.logs [logname]['log'].info (msg)
        if level == 'warning':
            self.logs [logname]['log'].warning (msg)
        if level == 'error':
            self.logs [logname]['log'].error (msg)
    
    def hasDebug (self):
        """
            check logs dictionary if key debug is set
        """
        if self.logs.has_key ('debug'):
            return True
        return False
    
    def getLogfilename (self, id):
        """
            return log filename of log id
        """
        return self.logs[id]['handler'].baseFilename
    
    def startOverall (self):
        timestamp = datetime.datetime.now().strftime ("%d.%m.%Y %H:%M")
        self.overallMsg = "get new message at " + timestamp 
    
    def stopOverall (self, success):
        if success == True:
            self.overallMsg = self.overallMsg + " - successful"
            self.writeLog ('overall', 'info', self.overallMsg)
        else:
            self.overallMsg = self.overallMsg + " - FAILED"
            
            if self.logs.has_key ('debug'):
                self.overallMsg = self.overallMsg + " - debugfile: " + self.getLogfilename ('debug')
            else:
                self.overallMsg = self.overallMsg + " - debugfile: " + self.getLogfilename ('info')
            self.writeLog ('overall', 'error', self.overallMsg)
        
        self.logs
        
    def closeLog (self, id):
        """
            close log with id
        """
        self.logs[id]['handler'].close()
    
    def closeLogs (self, delEmptyError=False):
        """
            close logs and del empty error files
        """
        for log in self.logs.keys():
            self.logs[log]['handler'].close()
            
        if delEmptyError:
            logfile = open (self.logs['error']['handler'].baseFilename, 'r')
            if not logfile.readlines ():
                os.remove(self.logs['error']['handler'].baseFilename)