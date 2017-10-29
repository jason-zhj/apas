from mixins import NameFormatMixin
from django.template.loader import render_to_string
from abc import ABCMeta,abstractmethod

class BaseObjectSummarizer(NameFormatMixin,object):
    """
    Generate html summary for a model object
    """
    __metaclass__=ABCMeta
    template="appglobal/summary-template-default.html"

    def __init__(self,source,fields):
        """
        :param object: a Model object
        :param fields: a list of strings
        each field be either the name of an attribute of the model object, or the name of a method of the model object
        if method, it will be called to get the return value
        the data field name displayed will be the field with "get_" and anything before it striped off, underscore removed and titled
        """
        self.source=source
        self.fields=fields

    def get_summary(self):
        items=[]
        for field in self.fields:
            attr=getattr(self.source,field)
            if (hasattr(attr,'__call__')):
                attr=attr()
            items.append((self._format_field_name(field),attr))
        return render_to_string(self.template,{'items':items})



class ListObjectSummarizer(BaseObjectSummarizer):
    pass