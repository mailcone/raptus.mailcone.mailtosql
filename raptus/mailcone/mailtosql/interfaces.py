from zope import interface

class IFieldMapper(interface.Interface):
    
    
    def parse(self, value):
        """ parse string value to specified
            type and store it on the context
        """
    
