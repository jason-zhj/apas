from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.contrib import messages

from appglobal.views import SimpleListView,SimpleEditView,GroupDeleteView
from appglobal.helper import get_summary

from question.models import Question,QuestionPool,QuestionTopic,TestCaseSet
from question.views.forms import QuestionTopicForm,QuestionEditForm,QuestionPoolForm
from question.views.tables import TestCaseSetTable

class QuestionListView(SimpleListView):
    model = Question

    def get_fields(self):
        return ["title","required_language","question_topic__title","get_configure_tests"]

class QuestionEditView(SimpleEditView):
    model=Question
    form_class = QuestionEditForm

class QuestionDeleteSelectedView(GroupDeleteView):
    model=Question

    def get_redirect_url(self):
        return reverse("question_list")

class QuestionTopicListView(SimpleListView):
    model=QuestionTopic

    def get_fields(self):
        return ["title","description","subject"]

class QuestionTopicEditView(SimpleEditView):
    model=QuestionTopic
    form_class = QuestionTopicForm

class QuestionTopicDeleteSelectedView(GroupDeleteView):
    model=QuestionTopic

    def get_redirect_url(self):
        return reverse("question_topic_list")

class QuestionPoolListView(SimpleListView):
    model=QuestionPool

    def get_search_fields(self):
        return ['title','description']

class QuestionPoolEditView(SimpleEditView):
    model=QuestionPool
    form_class = QuestionPoolForm


class QuestionPoolDeleteSelectedView(GroupDeleteView):
    model=QuestionPool

    def get_redirect_url(self):
        return reverse("question_pool_list")

class TestCaseSetListView(SimpleListView):
    model = TestCaseSet
    table_class = TestCaseSetTable

    def get_object_list(self,sort_by,filter_dict,user):
        question=get_object_or_404(Question,slug=self.kwargs.get("question_slug"))
        if (not question.is_test_case_set_weightage_valid()):
            messages.info(self.request,"The weightage of the test case sets don't add up to 100 so far!\n please make sure that they add up to 100!")
        return question.testcaseset_set.filter(**filter_dict).order_by(sort_by) if sort_by else question.testcaseset_set.filter(**filter_dict)

    def get_extra_content(self):
        question=get_object_or_404(Question,slug=self.kwargs.get("question_slug"))
        question_summary=get_summary(source=question,fields=['title','content','get_difficulty','required_language','get_instruction_file_link'])
        return render_to_string("app-question/class-testcaseset/list.html",{'question':question,'question_summary':question_summary})

    def get_fields(self):
        return ['title','description','weightage']


class TestCaseSetDeleteSelectedView(GroupDeleteView):
    model = TestCaseSet

    def get_redirect_url(self):
        return reverse("test_case_set_list",args=self.kwargs.get("question_slug"))