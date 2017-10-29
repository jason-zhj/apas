from django.shortcuts import render,get_object_or_404
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from question.models import QuestionPool
from question.views import task_find_strange_submission,task_validate_submissions_against_requirement
from appglobal.tables import BaseTable
from appglobal.views import csv_response
from onlinetest.models import OnlineTest,OnlineTestQuestionPool
from onlinetest.forms import OnlineTestForm
from onlinetest.handler import OnlineTestHandler


@csrf_exempt
def online_test_edit(request,online_test_slug=None):
        # prepare data to display
    available_pools=QuestionPool.objects.all()
    online_test=None
    test_pools=None
    if (online_test_slug):
        online_test=get_object_or_404(OnlineTest,slug=online_test_slug)
        form=OnlineTestForm(instance=online_test)
        test_pools=online_test.onlinetestquestionpool_set.all()
    else:
        form=OnlineTestForm()

    # process form submission
    if (request.POST):
        form=OnlineTestForm(request.POST,request.FILES,instance=online_test)
        if (form.is_valid()):
            online_test=form.save()
            _save_onlinetest_pool(request.POST,online_test)
            messages.info(request, 'Online Test is successfully editted')
            return HttpResponseRedirect(reverse('online_test_list'))

    return render(request,'app-onlinetest/class-onlinetest/edit.html',{'form':form,'pools':available_pools,'test_pools':test_pools,'online_test':online_test})



# the view to start the online test
@csrf_exempt
def online_test_submission_create(request,object_slug):
    test=get_object_or_404(OnlineTest,slug=object_slug)
    test_hanlder=OnlineTestHandler(request=request,onlinetest=test)
    # authentication
    if (not test_hanlder.is_submission_open()):
        messages.info(request,"The online test " + test.title + " is not open for submission to you now!")
        return HttpResponseRedirect(reverse("home"))
    if (request.POST):
        created,test_submission=test_hanlder.create_or_update_test_submission()
        if (not created):
            messages.info(request,"The new submission you created scores lower than the old submission, so the new submission is discarded!")
        attempts_remaining=test.get_number_of_attempts_remaining(user=request.user)
        messages.info(request,"Online test has been successfully submitted")
        table_maker=BaseTable(object_list=test_submission.onlinetestquestionsubmission_set.all(), enable_edit=False,
                               enable_delete=False,
                           field_names=["get_question_title","weightage","get_score"])
        if(test_hanlder.is_submission_open()):
            return render(request,"app-onlinetest/class-onlinetestsubmission/after-create.html",{"test_submission":test_submission,"ot_question_submission_table":table_maker.generate_table_html(),"end_time_list":test_hanlder.get_end_time_list(),'attempts_remaining':attempts_remaining})
        else:
            return onlinetest_submission_end(request,object_slug)
    else:
        auto_submit_upon_timeout=not test.has_been_submitted_by(request.user)
        test_hanlder.setup_test_session()
        return render(request,"app-onlinetest/class-onlinetestsubmission/create.html",{"test":test,"questions":test_hanlder.get_test_questions(),"end_time_list":test_hanlder.get_end_time_list(),"auto_submit_upon_timeout":auto_submit_upon_timeout,"onlinetest":test})


def onlinetest_submission_end(request,object_slug):
    test=get_object_or_404(OnlineTest,slug=object_slug)
    test_hanlder=OnlineTestHandler(request=request,onlinetest=test)
    test_hanlder.clear_test_session()
    return HttpResponseRedirect(reverse("online_test_submission_list_student"))


def _save_onlinetest_pool(post_data,onlinetest):
    # clear old data before inserting new data
    onlinetest.onlinetestquestionpool_set.all().delete()
    records=[a for a in post_data["m2m_record"].split(";") if len(a)>0]
    for record in records:
        item_ls=record.split(",")
        pool_id=int(item_ls[0])
        weightage=int(item_ls[1])
        num_to_select=int(item_ls[2])
        otqp=OnlineTestQuestionPool.objects.create(
                online_test=onlinetest,question_pool=get_object_or_404(QuestionPool,id=pool_id),
                weightage=weightage,number_to_select=num_to_select
            )
        otqp.save()

#--------------------for finding invalid/ strange code----------------
def online_test_submission_find_strange_code(request,object_slug):
    test=get_object_or_404(OnlineTest,slug=object_slug)
    return task_find_strange_submission(request,test)


def online_test_submission_validate_requirement(request,object_slug):
    test=get_object_or_404(OnlineTest,slug=object_slug)
    return task_validate_submissions_against_requirement(request,test.get_question_submissions())

#-----------------------for creating submission data sheets--------------------------
def online_test_submission_create_result_sheet(request,object_slug):
    from onlinetest.resultstatistic import TestResultTableGenerator
    return online_test_submission_create_data_sheet(request,object_slug,table_generator_cls=TestResultTableGenerator,file_postfix="score-sheet")

def online_test_submission_create_question_sheet(request,object_slug):
    from onlinetest.resultstatistic import AttemptedQuestionTableGenerator
    return online_test_submission_create_data_sheet(request,object_slug,table_generator_cls=AttemptedQuestionTableGenerator,file_postfix="question-sheet")

def online_test_submission_create_data_sheet(request,object_slug,table_generator_cls,file_postfix):
    test=get_object_or_404(OnlineTest,slug=object_slug)
    generator=table_generator_cls(test=test)
    result_table=generator.get_result_table()
    return csv_response(request,data_table=result_table,file_name="online-test-" + test.title + "-" +file_postfix)
