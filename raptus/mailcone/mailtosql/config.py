CONFIG = {
          'saveBrokenDataPath' : '/path/to/mail-to-sql/brokenPipeData',

          # parameters for sql tables
          # could not be done in default.cfg at the moment
          'dbMailtableName' : 'mail',
          'mail_id_seq_name' : 'mail_id_seq',

          # parameters for attachment storage
          'attachmentRootPath' : '/path/to/mail-to-sql/mailAttachments',
          
          # mail parse config
          'FROM_DOM_PATTERN' : '[^<>\s]*@([^<>\s]*)',
          'FROM_PATTERN' : '([^<>\s]*@[^<>\s]*)',
          
          'TO_DOM_PATTERN' : '[^<>\s]*@([^<>\s]*)',
          'TO_PATTERN' : '([^<>\s]*@[^<>\s]*)',
          
          'CC_PATTERN' : '([^<>\s]*@[^<>\s]*)',
          
          'REFERENCES_PATTERN' : '([^<>\s]*@[^<>\s]*)',
          
          'IN_REPLY_TO_PATTERN' : '([^<>\s]*@[^<>\s]*)',
          
          'BOOLEAN_VALUES' : ['debugmode', 
                              'infolog_separate', 
                              'errorlog_separate', 
                              'error_separatedLogs_deleteEmpty',
                              'sendMailnotification',
                              'smtpauth',]
}
