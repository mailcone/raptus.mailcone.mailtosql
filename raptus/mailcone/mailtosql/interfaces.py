from zope import interface

class IFieldMapper(interface.Interface):
    
    
    def parse(self, value):
        """ parse string value to specified
            type and store it on the context
        """


class IContentMapper(interface.Interface):

    def parse(self, message):
        """ parse mail content like attachment or html
        """