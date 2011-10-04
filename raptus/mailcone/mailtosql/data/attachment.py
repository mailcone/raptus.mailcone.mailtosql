class Attachment (object):
    filepath = ''
    mailId = ''
    filename = ''
    receiveDate = ''
    receiveTime = ''
    strFullhour = ''
    data = ''
    
    # mailId is the id for sql row in mail table
    def __init__(self, filename, receiveDate, receiveTime, data):
        self.filename = filename
        self.receiveDate = receiveDate
        self.receiveTime = receiveTime
        self.data = data