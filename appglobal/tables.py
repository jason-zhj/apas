from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from mixins import NameFormatMixin

class BaseTable(NameFormatMixin,object):
    template="appglobal/table-template-default.html"
    edit_html="<a href='#'><i class='fa fa-edit'></a>"
    delete_html="""<a href='#' role='single-delete'><i class='fa fa-gavel'></a>"""

    field_names=[]

    def __init__(self,*args,**kwargs):
        """
        :param enable_edit: if True, the table will have an edit field
        For the url of the edit link, the system will try (1) The edit_url attribute of the object, (2) lower_case_underscored_class_name + "_edit"
        For the url parameter, the system will try (1) object.slug (2) object.id
        :param enable_delete: if True, the table will have a delete field
        For the url of the edit link, the system will try (1) The delete_url attribute of the object, (2) lower_case_underscored_class_name + "_delete"
        For the url parameter, the system will try (1) object.slug (2) object.id
        :param title: the title of the table
        :param field_names: the field_names to be included in the table
        each field name can either be the name of an attribute or the name of a function, if function, it will be called to get the return value
        if any of the field names is invalid, "NA" will be displayed
        The column will be the field name with "get_" stripped and title-styled
        If the field_names is left blank, the system will call get_table_fields() method of the model class,
        If all the above fail, the system will get the first DEFAULT_NUMBER_OF_DATA_COLUMNS fields from the object
        :param object_list: a query set
        :param template: template for generating the table html, if not specified, DEFAULT_TABLE_TEMPLATE will be used
        The template needs to have 'title','data','fields' variables
        """
        self.object_list=kwargs.get("object_list")
        self.enable_edit=kwargs.get("enable_edit")
        self.enable_delete=kwargs.get("enable_delete")
        self.field_names=kwargs.get("field_names") # compulsory
        self.attr_method_args={}
        self.args=args

    def generate_table_html(self):
        normalized_field_names=self._normalized_field_names(self.field_names)
        self._extend_field_names(normalized_field_names)
        data_table=[]
        if (len(self.object_list)==0):
            return render_to_string(self.template,{"fields":normalized_field_names,"data":data_table,"delete":False,"group_delete_url":None})

        group_delete_url=self.get_delete_url(self.object_list[0]) if self.enable_delete else "#"
        for datum in self.object_list:
            row=[]
            # if delete, add an id field
            row.append(datum.id)
            # fill the row
            for field in self.field_names:
                if (field in self.attr_method_args.keys()):
                    item=getattr(datum,field)(self.attr_method_args[field])
                elif (hasattr(datum,field)):
                   if (hasattr(getattr(datum,field),'__call__')):
                       try:
                           item=getattr(datum,field)()
                       except:
                           item=getattr(datum,field)(self.args)
                   else:
                       item=getattr(datum,field)
                else:
                    item="NA"
                row.append(item)
            self._extend_row(row,datum)
            data_table.append(row)

        return render_to_string(self.template,{"fields":normalized_field_names,"data":data_table,"delete":self.enable_delete,"group_delete_url":group_delete_url})


    def get_delete_url(self,item):
        return reverse(self._get_normalized_class_name(self.object_list[0])+"_delete_selected")

    def get_edit_url(self,item):
        return self._guess_edit_url(item)

    def set_attr_method_args(self,dict):
        self.attr_method_args.update(dict)

    def _extend_field_names(self,fields):
        if (self.enable_edit):
            fields.append("Edit")
        if(self.enable_delete):
            fields.append("Delete")

    def _extend_row(self,row,datum):
        if (self.enable_edit):
            edit_url=self.get_edit_url(item=datum)
            row.append(self.edit_html.replace("#",edit_url))

        if (self.enable_delete):
            row.append(self.delete_html)

    def _guess_edit_url(self,datum):
        return reverse(self._get_normalized_class_name(datum)+"_edit",args=[self._get_arg(datum)])

    def _get_arg(self,datum):
        return datum.slug if hasattr(datum,"slug") else datum.id
