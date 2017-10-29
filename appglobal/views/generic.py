from mixins import *
from django.views.generic import View
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from account.helper import is_staff

from appglobal.helper import call_or_none
from appglobal.tables import BaseTable

class SimpleListView(GuessFieldsMixin,FormatClassNameMixin,View):
    """
    | A View class that can be used as a view function by calling SimpleListView.as_view()
    | This view will be rendered as a searchable table
    | The objects to be displayed will be determined by:
    | calling the get_object_list(self,sort_by,filter_dict,user) method
    | which by default will call get_list_data(user,**kwargs) of the model class or get all data of the model class
    | The fields of the model objects to be listed will be determined by:
    | (1) 'fields' attribute
    | (2) calling model class's "get_table_fields" method
    | (3) arbitrarily choosing some fields
    | Every element in the 'fields' list can either be an attribute name or a method name
    | The title of the table will be determined by:
    | (1) 'title' attribute
    | (2) model class name + "List"
    | The table will have edit button displayed if 'enable_staff_edit' is set to True provided the user is staff
    | As for how the url for edit is obtained, refer to appglobal.tables documentation
    | The table will have delete button displayed if 'enable_staff_delete' is set to True provided the user is staff
    | As for how the url for delete is obtained, refer to appglobal.tables documentation
    | The template to be used will be determined by
    | (1) 'template' attribute
    | If 'search' is set to True, the table will have a search bar and also sorting function
    | The fields for searching is determined by 'search_fields' attribute, if it's not set, it will be obtained by calling model's get_search_fields() method, which should return a list of string
    | The factor for sorting is determined by 'sort_fields' attribute, if it's not set, it will be obtained by calling model class's get_sort_fields()
    | The element in the list will be used directly as parameters for django's model.object.filter(..) method
    | You can also put content before the table, by overriding the get_extra_content() method, all the arguments to the view can be accessed by self.kwargs
    """
    model=None
    template="appglobal/simple-list.html"
    items_per_page=8
    table_class=BaseTable
    title=None
    enable_staff_edit=True
    enable_staff_delete=True
    enable_search=True
    search_fields=[]
    sort_fields=[]

    def get(self, request, *args, **kwargs):
        self.kwargs=kwargs
        self.get_data=request.GET
        self.request=request
        self.request_user=request.user
        if not self.model:
            raise Exception("SimpleListView needs a 'model' specified!")
        title=self.get_title()
        # get data list
        self.filter_dict=self._get_filter_dict(self.get_data)
        self.data_list=self.get_object_list(sort_by=self.get_data.get("sort_by"),filter_dict=self.filter_dict,user=self.request_user)
        # get search info
        search_info_dict=self._get_search_info()
        # get sort info
        sort_tuple_list=self._get_sort_tuples()
        # do pagination
        self.paginated_data=self._get_paginated_data()
        # generate table
        table=self._get_table_html()
        return render(request,self.kwargs.get("template",self.template),{"table":table,"title":title,
                                        'paginated_data':self.paginated_data,"search_tuple_list":search_info_dict["search_tuple_list"],
                                        "search_word":search_info_dict["search_word"],"search_by":search_info_dict["search_by"],
                                        "extra_content":self.get_extra_content(),"sort_tuple_list":sort_tuple_list})

    def get_fields(self):
        return self._guess_field_names(object_list=self.data_list)

    def get_object_list(self,sort_by,filter_dict,user):
        if (hasattr(self.model,"get_list_data")):
            data_list=getattr(self.model,"get_list_data")(self.request_user,sort_by,**self.filter_dict)
        else:
            data_list=self.model.objects.filter(**self.filter_dict).order_by(sort_by) if sort_by else list(reversed(self.model.objects.filter(**self.filter_dict)))
        return data_list

    def get_title(self):
        # if title is specified, use it
        if self.title:
            return self.title
        # else, infer a title
        return self.format_class_name_to_title(self.model.__name__) + " List"

    def get_attr_method_args(self):
        return {}

    def get_extra_content(self):
        return None

    def _get_sort_tuples(self):
        return [(a,self.format_underscored_to_titled(a)) for a in self.get_sort_fields()]

    def _get_search_info(self):
        if (not self.enable_search):
            return {"search_word":None,"search_by":None,"search_tuple_list":None}
        search_word=self.filter_dict[self.filter_dict.keys()[0]] if self.filter_dict else ""
        search_by=""
        for key in self.get_data.keys():
            search_by=key if key!="page" else ""
        # --------------------------get filtering fields-------------------------
        search_fields=self.get_search_fields()
        # tuple of (value,display_name)
        search_tuple_list=[(a,self.format_underscored_to_titled(a)) for a in search_fields] if search_fields else []
        return {"search_word":search_word,"search_by":search_by,"search_tuple_list":search_tuple_list}

    def get_search_fields(self):
        return self.get_fields()

    def get_sort_fields(self):
        return self.get_search_fields()

    def _get_paginated_data(self):
        paginator = Paginator(self.data_list, self.items_per_page)
        page = self.get_data.get('page')
        try:
            paginated_data = paginator.page(page)
        except PageNotAnInteger:
            paginated_data = paginator.page(1)
        except EmptyPage:
            paginated_data = paginator.page(paginator.num_pages)
        return paginated_data

    def _get_table_html(self):
        table="<h3>No data</h3>"
        if (len(self.paginated_data)>0):
            table_maker=self.table_class(self.request_user,object_list=self.paginated_data,
                                   enable_edit=self.enable_staff_edit if is_staff(self.request_user) else False,
                                   field_names=self.get_fields(),
                                   enable_delete=self.enable_staff_delete if is_staff(self.request_user) else False
                                   )
            table_maker.set_attr_method_args(self.get_attr_method_args())
            table=table_maker.generate_table_html()
        return table

    def _get_filter_dict(self,get_dict):
        filter_dict={}
        for key in get_dict.keys():
            if (key!="page" and key!="sort_by"):
                filter_dict[key+"__icontains"]=get_dict[key]
        return filter_dict


class GroupDeleteView(RedirectUtilMixin,View):
    """
    | A View class that can be used as a view function by calling GroupDeleteView.as_view()
    | This view will simply delete a list of objects and redirect to another view
    | Necessary parameters:
    """
    model=None

    def post(self,request,*args,**kwargs):
        self.kwargs=kwargs
        ids_to_delete=request.POST.getlist("delete")
        if (not self.model):
            raise Exception("GroupDeleteView requires a model specified!")
        all_successful=True
        redirect_url=self.get_redirect_url()
        for id in ids_to_delete:
            try:
                item=self.model.objects.get(id=int(id))
                self.delete_item(item=item)
            except:
                all_successful=False
                messages.info(request,"Error in doing deletion!")
        if (all_successful):
            messages.info(request,"Deletion is successful!")
        return HttpResponseRedirect(redirect_url)

    def delete_item(self,item):
        if (hasattr(item,'clean_up')):
            getattr(item,'clean_up')()
        item.delete()

    def get_redirect_url(self):
        return self.guess_redirect_url(object=self.model)

    @method_decorator(csrf_exempt)
    @method_decorator(transaction.atomic)
    def dispatch(self, *args, **kwargs):
        return super(GroupDeleteView, self).dispatch(*args, **kwargs)

class SimpleEditView(RedirectUtilMixin,FormatClassNameMixin,EditViewMixin,View):
    """
    | A View class that can be used as a view function by calling SimpleEditView.as_view()
    | This view will show an edit page and save changes upon user submission
    """
    template="appglobal/simple-edit.html"
    model=None
    form_class=None
    title=None
    go_back_to_url_name=None
    custom_js_paths=[]
    custom_css_paths=[]
    show_wait_modal=True

    def get(self,request,*args,**kwargs):
        self.kwargs=kwargs
        object_id=kwargs.get("object_id",None)
        if (not self.model):
            raise  Exception("SimpleEdit needs model specified!")
        if (not self.form_class):
            raise  Exception("SimpleEdit needs form_class specified!")
        object=self.get_object(object_id=object_id,model_class=self.model) if object_id else None
        form=self.form_class(instance=object)
        # get the title
        if (not self.title):
            self.title="Edit " + self.format_class_name_to_title(self.model._meta.model_name)
            if (object):
                self.title= "Edit " + str(object)
        return render(request,self.template,{'form':form,"title":self.title,"go_back_url":self.go_back_to_url_name,"custom_js_list":self.custom_js_paths,'custom_css_list':self.custom_css_paths,'show_wait_modal':self.show_wait_modal})

    def post(self,request,*args,**kwargs):
        object_id=kwargs.get("object_id")
        object=self.get_object(object_id=object_id,model_class=self.model) if object_id else None
        form=self.form_class(request.POST,request.FILES,instance=object)
        if (form.is_valid()):
            object=form.save()
            self.post_save(item=object)
            redirect_to_url=self.get_redirect_url(object=object)
            messages.info(request,str(object) + " is successfully editted!")
            return HttpResponseRedirect(redirect_to_url)

    def post_save(self,item):
        pass

    def get_redirect_url(self,object):
        return self._get_redirect_to_url(object=object)

    @method_decorator(csrf_exempt)
    @method_decorator(transaction.atomic)
    def dispatch(self, *args, **kwargs):
        return super(SimpleEditView, self).dispatch(*args, **kwargs)
