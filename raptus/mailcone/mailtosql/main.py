import os
import sys
from ConfigParser import ConfigParser
from optparse import OptionParser

from zope.app.appsetup import appsetup

from raptus.mailcone.app.startup import configurator




def main(config=None, file=None):

    parser = OptionParser()
    parser.add_option('-f',
                      '--file',
                      metavar='FILE',
                      dest='file',
                      default=None,
                      help='a file as mail source code')

    parser.add_option('-c',
                      '--config',
                      metavar='FILE',
                      dest='config',
                      default=None,
                      help='path to configuration file')


    options, args = parser.parse_args()
    
    if options.file is not None:
        data = open(options.file,'r').read()
    elif file is not None:
        data = open(file, 'r').read()
    else:
        data = sys.stdin.read()
    
    configparser = ConfigParser()
    if options.config is not None:
        config = options.config
    if not config:
        raise ValueError('missing configuration file. -c /path/config.cfg')


    configparser.read(config)
    
    zcml = os.path.join(os.path.dirname(__file__),'site.zcml')
    
    configurator(dict(here=__file__,
                      __file__=config,
                      zope_conf=zcml),
                **dict(configparser.items('mailtosql')))
    
    appsetup.config(zcml)


    from raptus.mailcone.mailtosql.parser import Parser
    Parser(data)




if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass