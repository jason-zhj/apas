from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse

from account.helper import is_staff
from appglobal.views import SimpleListView,GroupDeleteView
from appglobal import get_summary

from assignment.models import AssignmentQuestionSubmission,AssignmentSubmission,Assignment

class AssignmentQuestionSubmissionListView(SimpleListView):
    model=AssignmentQuestionSubmission
    enable_search = False
    enable_staff_edit = False
    enable_staff_delete = False

    def get_object_list(self,sort_by,filter_dict,user):
        a_submission=self.get_assignment_submission()
        aq_submissions=a_submission.assignmentquestionsubmission_set.filter(**filter_dict)
        aq_submissions=aq_submissions.order_by(sort_by) if sort_by else aq_submissions
        return aq_submissions

    def get_extra_content(self):
        a_submission=self.get_assignment_submission()
        submission_summary=get_summary(source=a_submission,fields=["get_title","get_score","submission_time"])
        return render_to_string("app-assignment/class-assignmentsubmission/detail.html",{'assignment_submission':a_submission,"summary":submission_summary})

    def get_fields(self):
        if (is_staff(self.request_user)):
            return ["get_question_title","weightage","get_score","get_detail_link"]
        else:
            return ["get_question_title","weightage","get_score","get_detail_link_for_student"]

    def get_assignment_submission(self):
        a_submission_id=self.kwargs.get("assignment_submission_id")
        return get_object_or_404(AssignmentSubmission,id=a_submission_id)

#-----------------------AssignmentSubmission----------------------------

class AssignmentSubmissionStaffListView(SimpleListView):
    model=AssignmentSubmission
    enable_staff_edit = False

    def get_object_list(self,sort_by,filter_dict,user):
        assignment=self.get_assignment()
        a_submissions=assignment.assignmentsubmission_set.filter(**filter_dict)
        a_submissions=a_submissions.order_by(sort_by) if sort_by else a_submissions
        return a_submissions

    def get_extra_content(self):
        assignment=self.get_assignment()
        assignment_summary=get_summary(source=assignment,fields=["title","description","get_receiver_groups","get_run_test_option","get_instruction_file_link"])
        return render_to_string("app-assignment/class-assignmentsubmission/list-staff.html",{'assignment':assignment,"assignment_summary":assignment_summary})

    def get_search_fields(self):
        return ["submission_time","submitted_by__username","assignment__title"]

    def get_assignment(self):
        assignment_slug=self.kwargs.get("assignment_slug")
        return get_object_or_404(Assignment,slug=assignment_slug)

    def get_fields(self):
        return ["submitted_by","submission_time","get_score","get_detail_link"]

class AssignmentSubmissionStudentListView(SimpleListView):
    model=AssignmentSubmission
    enable_search = False

    def get_fields(self):
        return ["get_title","submission_time","get_score","get_detail_link"]

    def get_object_list(self,sort_by,filter_dict,user):
        a_submissions=AssignmentSubmission.objects.filter(submitted_by=user,**filter_dict)
        return a_submissions

class AssignmentSubmissionDeleteSelectedView(GroupDeleteView):
    model=AssignmentSubmission

    def get_redirect_url(self):
        return reverse("assignment_list")

#-----------------------Assignment--------------------------------

class AssignmentListView(SimpleListView):
    model=Assignment

    def get_fields(self):
        if (not is_staff(self.request_user)):
            return ["title","description","end_submission_time","get_number_of_attempts_remaining","get_start_submission"]
        else:
            return ["title","description","start_submission_time","get_submission_link"]

    def get_object_list(self,sort_by,filter_dict,user):
        if (is_staff(user)):
            assignments=Assignment.objects.filter(**filter_dict)
            return assignments.order_by(sort_by) if sort_by else assignments
        else:
            return Assignment.get_student_can_submit(sort_by=sort_by,user=user,**filter_dict)

    def get_search_fields(self):
        return ["title","start_submission_time","end_submission_time"]

    def get_attr_method_args(self):
        return {"get_number_of_attempts_remaining":self.request_user}

class AssignmentDeleteSelectedView(GroupDeleteView):
    model = Assignment

    def get_redirect_url(self):
        return reverse("assignment_list")