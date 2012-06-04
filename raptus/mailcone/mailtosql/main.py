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
    if options.file is not None:
        for f in files(options.file):
            Parser(open(f,'r').read())
    elif file is not None:
        for f in files(file):
            Parser(open(f, 'r').read())
    else:
        Parser(sys.stdin.read())



def files(path):
    if isinstance(path, list):
        return path
    if os.path.isdir(path):
        return [os.path.join(path, i) for i in os.listdir(path)]
    return [path]
    



if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
