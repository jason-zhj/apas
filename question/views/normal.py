import  json
from datetime import datetime

import os
from django.shortcuts import render,get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db import transaction
from appglobal.helper import generate_unique_file_name,save_uploaded_file,get_class_from_string,get_summary
from appglobal.tables import BaseTable
from account.helper import is_staff
from question.models import Remarking,TestCaseSetResult
from question.views.forms import *
from question.utils import *
from question.views.tables import *
from question.models import TestCaseSet,Question,QuestionSubmission,TestCase,TestCaseResult
from question.codestore.storage import CodeStorer,CodeStorerException,clean_dir,get_relative_work_dir,remove_code_file,get_temp_code_store_dir,get_relative_code_path_from_abspath
from question.grading import do_compilation
from question.strangecode import check_recursive


@transaction.atomic
@csrf_exempt
def test_case_set_edit(request,question_slug=None,object_id=None):
    form=TestCaseSetForm()
    object=None
    q=None
    testcases=None
    if (question_slug):
        # create new Test case set
        q=get_object_or_404(Question,slug=question_slug)
    elif (object_id):
        object=get_object_or_404(TestCaseSet,pk=object_id)
        form=TestCaseSetForm(instance=object)
        q=object.question
        testcases=object.testcase_set.all()

    if (request.POST):
        form=TestCaseSetForm(request.POST,instance=object)

        if (form.is_valid()):
            #-------save test case set-----------
            object=form.save(commit=False)
            object.question=q
            object.save()
            #---------save test case--------------
            handle_test_cases(post_data=request.POST,testcase_set=object)
            messages.info(request,str(object) + " is successfully editted!")
            return HttpResponseRedirect(reverse("test_case_set_list",args=[q.slug]))

    return render(request,"app-question/class-testcaseset/edit.html",{'form':form,'question':q,'test_cases':testcases})

def handle_test_cases(post_data,testcase_set):
    test_inputs=post_data.getlist("test_inputs")
    expected_outputs=post_data.getlist("expected_outputs")
    output_mark_allocations=post_data.getlist("output_mark_allocation")
    ids=post_data.getlist("id")
    #---------------clear test cases-----------
    testcase_set.testcase_set.all().delete()
    #----------recreate---------------
    for i in range(len(ids)):
        t=TestCase.quick_save(test_inputs=test_inputs[i],expected_outputs=expected_outputs[i],testcase_set=testcase_set,output_mark_allocation=output_mark_allocations[i])

@csrf_exempt
@transaction.atomic
def test_case_create(request,question_slug):
    question=get_object_or_404(Question,slug=question_slug)
    set_form=TestCaseSetSimpleForm()
    test_case_form=TestCaseForm()
    go_back_url=reverse("test_case_set_list",args=[question.slug])
    if (request.POST):
        set_form=TestCaseSetSimpleForm(request.POST)
        test_case_form=TestCaseForm(request.POST)
        if (set_form.is_valid() and test_case_form.is_valid()):
            test_case_set=set_form.save(commit=False)
            test_case=test_case_form.save(commit=False)
            test_case_set.question=question
            test_case_set.grading_method=TestCaseSet.PICK_MINIMUM_MARK
            test_case_set.save()
            test_case.testcase_set=test_case_set
            test_case.save()
            messages.info(request,str(test_case_set) + " is successfully editted!")

            return HttpResponseRedirect(go_back_url)

    return render(request,"app-question/class-testcaseset/single-edit.html",{"set_form":set_form,"test_case_form":test_case_form,"title":"Create Simple Test Case","go_back_url":go_back_url})


# view for viewing question submission result
@csrf_exempt
@transaction.atomic
def question_submission_view_student(request,object_id):
    question_submission=get_object_or_404(QuestionSubmission,id=object_id)
    # block access when grading is not finished
    assoc_submission=get_question_associated_submission(question_submission)
    if (not is_staff(request.user) and not assoc_submission.allow_detail_access_for_student()):
        messages.info(request,"You are allowed to view question submission detail yet!")
        return HttpResponseRedirect(reverse("home"))
    remarking_records=question_submission.remarking_set.all()

    # Changing Score Form Processing
    form=ChangeScoreForm()
    if (request.POST):
        form=ChangeScoreForm(request.POST)
        if (form.is_valid()):
            # process the form
            new_score=form.cleaned_data['new_score']
            old_score=question_submission.score
            question_submission.score=new_score
            question_submission.save()
            Remarking.quick_save(old_score=old_score,new_score=new_score,modifier=request.user,comment=form.cleaned_data['comment'],question_submission=question_submission)
            messages.info(request,"Score has been successfully changed!")
            form=ChangeScoreForm()
        else:
            messages.info(request,"Your form submission is not valid, please check!")
    # get relevant info about the submission
    question=question_submission.question
    # get the test case results
    test_case_set_results=TestCaseSetResult.objects.filter(question_submission=question_submission)
    question_submission_summary=get_summary(source=question_submission,fields=['get_score','submission_time','get_compilation_status'])
    return render(request,
                  'app-question/class-questionsubmission/detail.html',
                  {'question_submission':question_submission,'question_submission_summary':question_submission_summary,
                   'question':question,'test_results':test_case_set_results,'change_score_form':form,'changing_score_records':remarking_records})



@transaction.atomic
def question_submission_grade(request,object_slug,model_class,redirect_to="home"):
    """
    :param request:
    :param object_slug:
    :param model_class: this class's instance should have a get_question_submissions() method
    :return: redirect to reverse(redirect_to) or reverse(redirect_to,args=[object_slug])
    """
    task=get_object_or_404(model_class,slug=object_slug)
    q_submissions=task.get_question_submissions()
    #------------do grading------------------
    for q_submission in q_submissions:
        if (not q_submission.is_grading_finished):
            grade_question_submission_and_save_result(q_submission)
    messages.info(request,"Grading of question submissions done!")
    #-------------redirecting------------------
    try:
        target_url=reverse(request)
    except:
        target_url=reverse(redirect_to,args=[object_slug])
    return HttpResponseRedirect(target_url)


QUESTION_ID_LIST_NAME="question_list"
SOLUTION_METRIC_LIST_NAME="solution_metric_list"
SUBMISSION_DATA_LIST_NAME="strange_submission_list"

def task_find_strange_submission(request,task):
    """
    :param request:
    :param task: it needs to have two methods: get_submitted_questions() and get_question_submissions(question)
    :return:
    """
    from question.strangecode import get_strange_code_checker
    from question.settings import MIN_SCORE_TO_CHECK_STRANGE_CODE
    questions=[a for a in task.get_submitted_questions() if len(a.suggested_solution)>0]
    request.session[QUESTION_ID_LIST_NAME]=[a.id for a in questions]
    request.session[SOLUTION_METRIC_LIST_NAME]=["" for i in range(len(questions))]
    request.session[SUBMISSION_DATA_LIST_NAME]=[[] for i in range(len(questions))]
    for i in range(len(questions)):
        question=questions[i]
        checker=get_strange_code_checker(suggested_code=question.suggested_solution,language=question.required_language,code_template=question.code_template)
        request.session[SOLUTION_METRIC_LIST_NAME][i]=checker.get_solution_metrics_report()
        q_submissions=[a for a in task.get_question_submissions(question=question) if a.score>=MIN_SCORE_TO_CHECK_STRANGE_CODE and a.is_grading_finished]
        for q_submission in q_submissions:
            check_result=checker.check_code(code=q_submission.get_source_code())
            if (check_result['is_strange']):
                request.session[SUBMISSION_DATA_LIST_NAME][i].append((q_submission.id,check_result['report']))
    zipped_data=zip(questions,request.session[SUBMISSION_DATA_LIST_NAME])
    return render(request,"app-question/class-questionsubmission/find-strange-code-overall.html",{"zipped_data":zipped_data})

def strange_question_submission_detail(request,index):
    index=int(index)
    question=get_object_or_404(Question,id=request.session[QUESTION_ID_LIST_NAME][index])
    question_summary=get_summary(source=question,fields=['title','content','required_language'])
    solution_metric_report=request.session[SOLUTION_METRIC_LIST_NAME][index]
    submission_data=request.session[SUBMISSION_DATA_LIST_NAME][index] # a list of (submission,metrics) tuples
    formatted_submission_data=[(get_object_or_404(QuestionSubmission,id=a),b) for a,b in submission_data]
    return render(request,"app-question/class-questionsubmission/find-strange-code-detail.html",{"question":question,"question_summary":question_summary,"solution_report":solution_metric_report,"submission_data":formatted_submission_data})


# for ajax request only, for student to test compilation during online test
@csrf_exempt
def test_compilation(request):
    required_language=request.POST['required_language']
    code=request.POST['code']
    work_dir=get_temp_code_store_dir(user_id=request.user.id)
    storer=CodeStorer(work_dir=work_dir,is_abs=True)
    code_path=""
    try:
        code_path=storer.save_code(code=code,language=required_language)
    except CodeStorerException as e:
        return HttpResponse(json.dumps({"sucess":False,"message":e.message}), content_type="application/json")

    compilation_result=do_compilation(code_file_path=code_path,language=required_language)
    # remove the file
    clean_dir(work_dir)
    return HttpResponse(json.dumps({"success":compilation_result["is_successful"],"message":compilation_result["error_message"]}), content_type="application/json")


def create_question_submissions_from_code(code_list,question_list,task,user):
    """
    :param code_list: list of code
    :param question_list:  list of Question
    :param task:  Assignment or OnlineTest instance
    :param user: request.user
    :return: a list of created question_submissions
    """
    q_submission_list=[]
    for i in range(len(code_list)):
        code=code_list[i]
        question=question_list[i]
        # 1. store the code = > get the source file name
        relative_work_dir=get_relative_work_dir(str(task),task.id,question.id, user.id)
        storer=CodeStorer(work_dir=relative_work_dir)
        code_path=""
        try:
            code_path=storer.save_code(code=code,language=question.required_language)
        except CodeStorerException as e:
            raise Exception("Error in storing code : " +e.message)
        # 2. compile the file
        compilation_result=do_compilation(code_file_path=code_path,language=question.required_language)
        # 3. store the question submission
        q_submission=QuestionSubmission.objects.create(
            src_file_path=get_relative_code_path_from_abspath(code_path),
            exe_file_path=get_relative_code_path_from_abspath(compilation_result["executable_path"])if compilation_result["executable_path"] else "",
            submission_time=datetime.now(),
            question=question,
            submitted_by=user,
            compilation_okay=compilation_result["is_successful"]
        )
        q_submission.save()
        q_submission_list.append(q_submission)

    return q_submission_list

def grade_question_submission_and_save_result(q_submission):
    from question.grading import grade_question_submission
    grading_result=grade_question_submission(q_submission=q_submission)
    # save q_submission
    q_submission.is_grading_finished=True
    q_submission.score=grading_result['score']
    exe_file_path=q_submission.exe_file_path
    q_submission.exe_file_path=None
    q_submission.save()
    # delete executable
    if (q_submission.compilation_okay):
        remove_code_file(exe_file_path)
    # save test case result
    test_results=grading_result['test_results']
    for test_result in test_results:
        # save test case set results
        test_case_set_result_dict=test_result[0]
        set_result=TestCaseSetResult.objects.create(question_submission=q_submission,**test_case_set_result_dict)
        set_result.question_submission=q_submission
        set_result.save()
        # save test case results
        test_case_results=test_result[1]
        for test_case_result_dict in test_case_results:
            case_result=TestCaseResult.objects.create(test_case_set_result=set_result,**test_case_result_dict)
            case_result.test_case_set_result=set_result
            case_result.save()

def task_validate_submissions_against_requirement(request,q_submissions):
    invalid_submissions=[]
    for submission in q_submissions:
        if (submission.question.get_requirement()):
            if (submission.requirement_checked):
                # if submission already checked, append it if it's invalid
                if (not submission.requirement_met):
                    invalid_submissions.append(submission)
            else:
                # if submission hasn't been checked, check it
                requirement_met,updated_submission=check_question_submission_against_requirement(submission)
                if (not requirement_met):
                    invalid_submissions.append(updated_submission)
    if (invalid_submissions):
        table=BaseTable(object_list=invalid_submissions,enable_edit=False,enable_delete=False,
              field_names=['get_question_title','get_submitted_by','get_previous_score','get_detail_link'])
        table_html=table.generate_table_html()
    else:
        table_html="No invalid submissions found"
    return render(request,"app-question/class-questionsubmission/checkrequirement.html",{'table':table_html})


def check_question_submission_against_requirement(q_submission):
    """
    :return: (is_requirement_met:bool,updated_q_submission)
    """
    requirement=q_submission.question.get_requirement()
    q_submission.requirement_checked=True
    if (not requirement):
        q_submission.requirement_met=True
        q_submission.save()
        return True,q_submission
    if (requirement.required_function_type==QuestionRequirement.RECURSIVE):
        is_recursive,msg=check_recursive(code=q_submission.get_source_code(),function_name=requirement.required_function_name,num_of_params=requirement.number_of_parameters,required_language=q_submission.question.required_language)
        if (not is_recursive):
            # recursive requirement violated, degrade score to 0
            q_submission.requirement_met=False
            q_submission.requirement_violation_msg=msg
            q_submission.remark_with_record(new_score=0,comment=msg)
            return False,q_submission

    #TODO: check for iterative or other requirement
    q_submission.requirement_met=True
    q_submission.save()
    return True,q_submission