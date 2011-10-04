import os

class AttachmentUtil (object):
    """
        This utility handle the whole stuff for attachments.
    """

    rootPath = ''
    logs = None # dict with logfiles

    def __init__ (self, CONFIG, logs=logs):
        """
            Constructur
        """
        self.rootPath = CONFIG ['attachmentRootPath']
        self.logs = logs

    def _getFullhour (self, attachment):
        """
            para: attachment obj
            this function set the full hour of the recieve date 
            (1335 -> set attachment.strFullhour 1300)
        """
        if self.logs: self.logs.writeLog ('debug', 'info', 'AttachmentUtil - _getFullhour() - start')
        try:
            attachment.strFullhour = attachment.receiveTime.strftime("%H00")
            if self.logs: self.logs.writeLog ('debug', 'info', 'AttachmentUtil - _getFullhour() - return: ' + attachment.strFullhour)
        except Exception, e:
            if self.logs: self.logs.writeLog ('debug', 'error', 'AttachmentUtil - _getFullhour() - FAILED - ' + str(e))
            if self.logs: self.logs.writeLog ('error', 'error', 'AttachmentUtil - _getFullhour() - FAILED - ' + str(e))
            raise RuntimeError, u"AttachmentUtil - _getFullhour() - FAILED - " + str(e)
    
    def _joinPath (self, attachment):
        """ 
            para: attachment obj
            compose path for data storage 
        """
        if self.logs: self.logs.writeLog ('debug', 'info', 'AttachmentUtil - _joinPath() - start')
        try:
            date = attachment.receiveDate.strftime ("%Y-%m-%d")
            self._getFullhour (attachment)
            attachment.filepath = os.path.join (self.rootPath, date, attachment.strFullhour, str(attachment.mailId))
            if self.logs: self.logs.writeLog ('debug', 'info', 'AttachmentUtil - _joinPath() - join path: ' + attachment.filepath)
        except Exception, e:
            if self.logs: self.logs.writeLog ('debug', 'error', 'AttachmentUtil - _joinPath() - FAILED - ' + str(e))
            if self.logs: self.logs.writeLog ('error', 'error', 'AttachmentUtil - _joinPath() - FAILED - ' + str(e))
            raise RuntimeError, u"AttachmentUtil - _joinPath() - FAILED - " + str(e)
        
    def _createPath (self, filepath):
        """ 
            check if path exist on filesystem, if not create path 
        """
        if self.logs: self.logs.writeLog ('debug', 'info', 'AttachmentUtil - _createPath() - start')
        try:    
            if not os.path.isdir (filepath):
                os.makedirs (filepath)
                if self.logs: self.logs.writeLog ('debug', 'info', 'AttachmentUtil - _createPath() - create path: ' + filepath)
        except Exception, e:
            if self.logs: self.logs.writeLog ('debug', 'error', 'AttachmentUtil - _createPath() - FAILED - ' + str(e))
            if self.logs: self.logs.writeLog ('error', 'error', 'AttachmentUtil - _createPath() - FAILED - ' + str(e))
            raise RuntimeError, u"AttachmentUtil - _createPath() - FAILED - " + str(e)
    
    def saveFile (self, attachment):
        """ 
            save attachment file on the file system 
        """
        if self.logs: self.logs.writeLog ('debug', 'info', 'AttachmentUtil - saveFile() - start')
        try:
            # compose file path for file
            self._joinPath(attachment)
            # create path for filestorage, not there
            self._createPath (attachment.filepath)
            
            # create and wirte file on filesystem
            file = os.path.join (attachment.filepath, attachment.filename)
            attachmentFile = open (file, 'w')
            attachmentFile.write (attachment.data)
            attachmentFile.close()
            if self.logs: self.logs.writeLog ('debug', 'info', 'AttachmentUtil - saveFile() - write data in file: ' + file)
            return True
        except Exception, e:
            if self.logs: self.logs.writeLog ('debug', 'error', 'AttachmentUtil - saveFile() - FAILED - ' + str(e))
            if self.logs: self.logs.writeLog ('error', 'error', 'AttachmentUtil - saveFile() - FAILED - ' + str(e))
            raise RuntimeError, u"AttachmentUtil - saveFile() - FAILED - " + str(e)