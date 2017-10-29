
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

class FormatClassNameMixin(object):
    def format_class_name_to_title(self,class_name):
        formatted=class_name[0]
        for i in range(1,len(class_name)):
            if (class_name[i].isupper()):
                formatted+=" "
            formatted+=class_name[i]
        return formatted

    def format_class_name_to_underscored(self,class_name):
        formatted=class_name[0].lower()
        for i in range (1,len(class_name)):
            if (class_name[i].isupper()):
                formatted +="_"
            formatted +=class_name[i].lower()
        return formatted

    def format_underscored_to_titled(self,name):
        in_underscore=False
        formatted=""
        for character in name:
            if not in_underscore:
                if (character=="_"):
                    formatted+=" "
                    in_underscore=True
                else:
                    formatted+=character
            else:
                if (character!="_"):
                    in_underscore=False
                    formatted+=character
        return formatted.title()



class RedirectUtilMixin(FormatClassNameMixin,object):
    DEFAULT_REDIRECT_URL_NAME="home"

    def _get_redirect_to_url(self,object,redirect_to_param=None):
        """
        :param object: a django.db.models.Model object
        :param redirect_to_param: string
        :return: string of url, determined by: (1) if redirect_to_param is not empty, the url will be obtained by trying to reverse it without parameters, then with object's slug as parameter, then with object's id as parameter
        (2) if redirect_to_param is empty, the url will be obtained by calling get_redirect_url() method of the object, then the object's class name(underscored) + "_list"
        """
        redirect_to=""
        if (not redirect_to_param):
            if (hasattr(object,"get_redirect_url")):
                redirect_to=getattr(object,"get_redirect_url")()
            else:
                redirect_to=self.guess_redirect_url(object)
        else:
            try:
                redirect_to=reverse(redirect_to_param)
            except:
                if (hasattr(object,"slug")):
                    redirect_to=reverse(redirect_to_param,args=[object.slug])
                else:
                    redirect_to=reverse(redirect_to_param,args=[object.id])

        return redirect_to

    def guess_redirect_url(self,object):
        """
        :param object: it can be an object or a class
        :return:
        """
        if (not object):
            return reverse(self.DEFAULT_REDIRECT_URL_NAME)
        if (hasattr(object,"__call__")):
            object=object()
        class_name=object.__class__.__name__
        return reverse(self.format_class_name_to_underscored(class_name) + "_list")


class EditViewMixin(object):
    def get_object(self,object_id,model_class):
        try:
            object=get_object_or_404(model_class,slug=object_id)
        except:
            object=get_object_or_404(model_class,id=object_id)
        return object

class GuessFieldsMixin(object):
    default_number_of_columns=3
    exclude_field_types=['AutoField','SlugField','ManyToManyField','OneToOneField']
    def _guess_field_names(self,object_list):
        field_names=[]
        if (len(object_list)==0):
            return []
        item=object_list[0]
        # otherwise, randomly guess
        all_fields=item.__class__._meta.fields
        number_of_data_column=0
        i=0
        while (number_of_data_column<self.default_number_of_columns and i<len(all_fields)):
            if (all_fields[i].__class__.__name__ in self.exclude_field_types):
                i +=1
                continue
            field_names.append(all_fields[i].name)
            i+=1
            number_of_data_column +=1
        return field_names