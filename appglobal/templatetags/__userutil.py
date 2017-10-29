import urllib
from django import template
from django.contrib.auth.models import Group

from appglobal import get_summary

register = template.Library() 

@register.filter(name='has_group') 
def has_group(user, group_name): 
	group = Group.objects.get(name=group_name) 
	return True if group in user.groups.all() else False 

@register.simple_tag(takes_context=True)
def paginated_url(context,page_number):
    request=context["request"]
    get_params_copy=request.GET.copy()
    get_params_copy["page"]=page_number
    return request.path + "?"+ urllib.urlencode(get_params_copy)

@register.filter(name='decorate_list_item')
def decorate_list_item(item):
    try:
        item_str=item.encode("utf-8")
    except:
        item_str=str(item)
    if (len(item_str.splitlines())>1 and not is_anchor_tag(item)):
        return "<pre>" + item + "</pre>"
    else:
        return item

def is_anchor_tag(item):
    striped=item.strip()
    if striped.find('<a')==0:
        return True
    else:
        return False

