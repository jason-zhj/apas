from django.http import HttpResponseRedirect
from apassite.settings import LOGIN_URL,LOGIN_EXEMPT_URLNAMES,STAFF_EXEMPT_URLNAMES,URLS_ALLOWED_IN_TEST
from django.core.urlresolvers import resolve,reverse
from django.contrib import messages
from onlinetest.settings import IN_TEST

STUDENT_VIEW_PATTERN="_student"

class LoginRequiredMiddleware:
    """
    This middleware prevents unauthorized users to access pages that require authentication
    """
    def process_request(self, request):
        if (not self._is_admin_url(request.path_info)):
            return self.process_nonadmin_request(request)


    def process_nonadmin_request(self,request):
        url_name = resolve(request.path_info).url_name
        if not request.user.is_authenticated():
            if (not (url_name in LOGIN_EXEMPT_URLNAMES)):
                return HttpResponseRedirect(LOGIN_URL + "?next=" +request.path_info)
        else:
            # first check whether he is in test
            if (IN_TEST in request.session.keys() and request.session[IN_TEST] and (not url_name in URLS_ALLOWED_IN_TEST)):
                messages.info(request,"Students are not allowed to access other pages when doing online test")
                return HttpResponseRedirect(reverse("home"))
            # then check whether this is a staff-required page
            if (not request.user.groups.filter(name="staff").exists()):
                if ((url_name.find(STUDENT_VIEW_PATTERN)==-1) and (not url_name in LOGIN_EXEMPT_URLNAMES) and (not url_name in STAFF_EXEMPT_URLNAMES)):
                    return HttpResponseRedirect(LOGIN_URL + "?next=" +request.path_info)

    def _is_admin_url(self,url):
        return url.find("/admin")==0