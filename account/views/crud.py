from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group

from appglobal.views import SimpleEditView,SimpleListView,GroupDeleteView

from account.models import StudentUserProfile,StudentGroup
from account.forms import UserForm,UserGroupForm


class StudentUserProfileListView(SimpleListView):
    model=StudentUserProfile

    def get_fields(self):
        return ['get_username','fullname','get_group_name','get_reset_password']

    def get_search_fields(self):
        return ["fullname","user__username","matric_number"]

class StudentUserProfileEditView(SimpleEditView):
    model=StudentUserProfile
    form_class=UserForm
    show_wait_modal=False

    def post_save(self,item):
        group = Group.objects.get(name='student')
        item.groups.add(group)

    def get_redirect_url(self,object):
        return reverse("student_user_profile_create",args=[object.id])

class StudentUserProfileDeleteSelectedView(GroupDeleteView):
    model=StudentUserProfile

    def get_redirect_url(self):
        return reverse("student_user_profile_list")

class StudentGroupListView(SimpleListView):
    model=StudentGroup

    def get_fields(self):
        return ["name","course","get_members_link"]

    def get_search_fields(self):
        return ["name","course"]


class StudentGroupEditView(SimpleEditView):
    model=StudentGroup
    form_class=UserGroupForm

class StudentGroupDeleteSelectedView(GroupDeleteView):
    model=StudentGroup

    def get_redirect_url(self):
        return reverse("student_group_list")