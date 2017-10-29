
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from appglobal.helper import get_summary
from appglobal.views import SimpleListView,GroupDeleteView
from account.models import StudentGroup
from account.helper import is_staff

from onlinetest.models import OnlineTest,OnlineTestSubmission,OnlineTestQuestionSubmission

class OnlineTestStaffListView(SimpleListView):
    model=OnlineTest

    def get_fields(self):
        return ["title","description","time_limit","get_submissions_link"]

    def get_search_fields(self):
        return ["title","description","time_limit"]

class OnlineTestStudentListView(SimpleListView):
    model = OnlineTest
    title="Submit Online Tests"

    def get_object_list(self,sort_by,filter_dict,user):
        ordered_data=OnlineTest.objects.filter(**filter_dict).order_by(sort_by) if sort_by else OnlineTest.objects.filter(**filter_dict)
        student_groups=StudentGroup.get_student_group_for_user(user)
        return [a for a in ordered_data if (a.is_in_submission_period()
                                                          and a.is_for_groups(student_groups) and not a.has_been_submitted_by(user))]

    def get_fields(self):
        return ["title","description","time_limit","get_start_test_link"]

    def get_search_fields(self):
        return ["title","description","time_limit"]

class OnlineTestDeleteSelectedView(GroupDeleteView):
    model=OnlineTest

    def get_redirect_url(self):
        return reverse("online_test_list")

class OnlineTestSubmissionStudentListView(SimpleListView):
    model=OnlineTestSubmission

    def get_fields(self):
        return ["get_test_title","submission_time","get_score","get_detail_link"]

    def get_search_fields(self):
        return ['title','submission_time']

    def get_object_list(self,sort_by,filter_dict,user):
        return OnlineTestSubmission.objects.filter(submitted_by=user)

class OnlineTestSubmissionStaffListView(SimpleListView):
    model = OnlineTestSubmission
    enable_staff_edit = False

    def get_fields(self):
        return ["get_submittor_name","submission_time","get_score","get_detail_link"]

    def get_search_fields(self):
        return ['submitted_by__username','submission_time']

    def get_object_list(self,sort_by,filter_dict,user):
        test=get_object_or_404(OnlineTest,slug=self.kwargs.get('object_slug'))
        submission_set=test.onlinetestsubmission_set
        if (is_staff(user)):
            return submission_set.filter(**filter_dict).order_by(sort_by) if sort_by else submission_set.filter(**filter_dict)
        else:
            return submission_set.filter(submitted_by=user,**filter_dict).order_by(sort_by) if sort_by else submission_set.filter(**filter_dict)

    def get_extra_content(self):
        test=get_object_or_404(OnlineTest,slug=self.kwargs.get('object_slug'))
        test_summary=get_summary(source=test,fields=["title","description","time_limit"])
        return render_to_string("app-onlinetest/class-onlinetestsubmission/list-staff.html",{'test':test,'test_summary':test_summary})

class OnlineTestSubmissionDeleteSelectedView(GroupDeleteView):
    model=OnlineTestSubmission

    def get_redirect_url(self):
        return reverse("online_test_list")

class OnlineTestQuestionSubmissionListView(SimpleListView):
    model = OnlineTestQuestionSubmission
    enable_staff_edit = False
    enable_staff_delete = False
    enable_search = False

    def get_object_list(self,sort_by,filter_dict,user):
        return self.get_test_submission().onlinetestquestionsubmission_set.all()

    def get_fields(self):
        if (is_staff(self.request_user)):
            return ["get_question_title","weightage","get_score","get_detail_link"]
        else:
            return ["get_question_title","weightage","get_score","get_detail_link_for_student"]

    def get_extra_content(self):
        return get_summary(source=self.get_test_submission(),fields=["get_score","submission_time"])

    def get_test_submission(self):
        object_id=self.kwargs.get("object_id",None)
        return get_object_or_404(OnlineTestSubmission,id=object_id)