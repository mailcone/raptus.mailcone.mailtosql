import sys

try:
    from sqlalchemy import *
    from sqlalchemy.orm import scoped_session, sessionmaker
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.exc import *
except ImportError:
    raise ImportError, u"mail-to-sql requires sqlalchemy."

try:
    import psycopg2
except ImportError:
    raise ImportError, u"mail-to-sql requires psycopg2."

class DatabaseUtil (object):
    """
        This utility handle all the stuff for the database connection
    """
    
    dbDriver = ''
    dbHostname = ''
    dbPort = ''
    dbUser = ''
    dbPw = None
    dbName = ''
    egnine = None
    session = None
    
    logs = None # dict with logfiles
    
    def __init__ (self, CONFIG, logs=logs):
        """
            Constructor
        """
        self.logs = logs
        
        self.dbDriver = CONFIG ['dbDriver']
        self.dbHostname = CONFIG ['dbHostname']
        self.dbPort = CONFIG ['dbPort']
        self.dbUser = CONFIG ['dbUser']
        self.dbPw = CONFIG ['dbPw']
        self.dbName = CONFIG ['dbName']
        
        #create engine and session
        self._createEngine()
        self._createSession()
    
    def _createEngine (self):
        """ 
            create sqlalchemy engine, with parameters from config.py
        """
        if self.logs: self.logs.writeLog ('debug', 'info', 'DatabaseUtil - _createEngine() - start')
        try:
            self.engine = create_engine ('%s://%s:%s@%s:%s/%s' % (self.dbDriver, 
                                                                  self.dbUser, 
                                                                  self.dbPw, 
                                                                  self.dbHostname, 
                                                                  self.dbPort, 
                                                                  self.dbName), convert_unicode=True, encoding="utf8")
        except Exception, e:
            if self.logs: self.logs.writeLog ('debug', 'error', 'DatabaseUtil - _createEngine() - FAILED - ' + str(e))
            if self.logs: self.logs.writeLog ('error', 'error', 'DatabaseUtil - _createEngine() - FAILED - ' + str(e))
            raise RuntimeError, u"DatabaseUtil - _createEngine() - FAILED - " + str(e)
    
    def _createSession (self):
        """ 
            create sqlalchemy session, with self.engine (self._createEngine) 
        """
        if self.logs: self.logs.writeLog ('debug', 'info', 'DatabaseUtil - _createSession() - start')
        try:
            Session = scoped_session (sessionmaker (bind=self.engine))
            self.session = Session ()
        except Exception, e:
            if self.logs: self.logs.writeLog ('debug', 'error', 'DatabaseUtil - _createSession() - FAILED - ' + str(e))
            if self.logs: self.logs.writeLog ('error', 'error', 'could not create database session - ' + str(e))
            raise RuntimeError, u"DatabaseUtil - _createSession() - FAILED - " + str(e)
    
    def connect (self):
        """
            create a connection to sql database
        """
        if self.logs: self.logs.writeLog ('debug', 'info', 'DatabaseUtil - connect() - start')
        try:
            self.engine.connect ()
            if self.logs: self.logs.writeLog ('debug', 'info', 'DatabaseUtil - connect() - connect with database: ' + self.dbName.upper())
        except Exception, e:
            if self.logs: self.logs.writeLog ('debug', 'error', 'DatabaseUtil - connect() - FAILED - ' + str(e))
            if self.logs: self.logs.writeLog ('error', 'error', 'could not connect to database ' + str(e))
            raise RuntimeError, u"DatabaseUtil - connect() - FAILED - " + str(e)
                   
    def closeConnection (self):
        """ 
            close session and enigne
        """
        if self.logs: self.logs.writeLog ('debug', 'info', 'DatabaseUtil - closeConnection() - start')
        try:
            self.session.close ()
            self.engine.dispose()
            if self.logs: self.logs.writeLog ('debug', 'info', 'DatabaseUtil - closeConnection() - connection closed')
        except Exception, e:
            if self.logs: self.logs.writeLog ('debug', 'error', 'DatabaseUtil - closeConnection() - FAILED - ' + str(e))
            if self.logs: self.logs.writeLog ('error', 'error', 'could not close database connection - ' + str(e))
            raise RuntimeError, u"DatabaseUtil - closeConnection() - FAILED - " + str(e)
        
    def saveObject (self, obj):
        """ 
            para: obj -> must be based on declarative_base and have set a __tablename__
            add given object to sql database 
        """
        if self.logs: self.logs.writeLog ('debug', 'info', 'DatabaseUtil - saveObject() - start')
        try:
            self.session.add (obj)
            if self.logs: self.logs.writeLog ('debug', 'info', 'DatabaseUtil - saveObject() - self.session.add (self) successful')
            self.session.commit()
            if self.logs: self.logs.writeLog ('debug', 'info', 'DatabaseUtil - saveObject() - self.session.commit (self) successful')
            return True
        except Exception, e:
            if self.logs: self.logs.writeLog ('debug', 'error', 'DatabaseUtil - saveObject() - FAILED - ' + str(e))
            if self.logs: self.logs.writeLog ('error', 'error', 'could not save mail object to database - ' + str(e))
            raise RuntimeError, u"DatabaseUtil - saveObject() - FAILED - " + str(e)    