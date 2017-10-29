from datetime import datetime

from django.shortcuts import render,get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db import transaction

from appglobal.helper import *
from appglobal.views import csv_response
from assignment.models import AssignmentQuestionSubmission,AssignmentSubmission,AssignmentQuestion,AssignmentAttemptRecord
from question.models import Question
from question import task_find_strange_submission,create_question_submissions_from_code,grade_question_submission_and_save_result
from question.views import task_validate_submissions_against_requirement
from assignment.forms import *

@transaction.atomic
@csrf_exempt
def assignment_edit(request,assignment_slug=None):
    # prepare data to display
    available_questions=Question.objects.all()
    assignment=None
    assignment_questions=None
    if (assignment_slug):
        assignment=get_object_or_404(Assignment,slug=assignment_slug)
        form=AssignmentEditForm(instance=assignment)
        assignment_questions=assignment.assignmentquestion_set.all()
    else:
        form=AssignmentEditForm()

    # process form submission
    if (request.POST):
        form=AssignmentEditForm(request.POST,request.FILES,instance=assignment)
        if (form.is_valid()):
            assignment=form.save()
            mark_allocation_string=request.POST['m2m_record']
            _save_assignment_question(mark_allocation_string,assignment)
            messages.info(request, 'Assignment is successfully editted')
            return HttpResponseRedirect(reverse('assignment_list'))

    return render(request,'app-assignment/class-assignment/edit.html',{'form':form,'questions':available_questions,'assignment_questions':assignment_questions,'assignment':assignment})

def _save_assignment_question(allocation_str,assignment):
    # clear old data before inserting new data
    assignment.assignmentquestion_set.all().delete()
    str_list=allocation_str.split(";")
    for i in range(0,len(str_list)):
        # find the comma
        seperator_index=str_list[i].find(',')
        if (seperator_index==-1):
            continue
        # get question id
        question_id=str_list[i][:seperator_index]
        # add to the 'questions' query set
        question=get_or_none(Question,slug=question_id)
        weightage=str_list[i][seperator_index+1:].strip()

        if (question and weightage.isdigit()):
            new_assignment_question=AssignmentQuestion.objects.create(assignment=assignment,question=question,weightage=(int)(weightage))
            new_assignment_question.save()


def assignment_submission_report(request,assignment_slug,assignment_submission_id):
    a_submission=get_object_or_404(AssignmentSubmission,id=assignment_submission_id)
    if (not a_submission.is_grading_finished()):
        messages.info(request,"Grading for the submission is not finished, the report is not available now")
        return HttpResponseRedirect(reverse("assignment_submission_list",args=[assignment_slug]))
    # generate report
    assignment_summary=get_summary(source=a_submission.assignment,fields=["title","description"])
    a_submission_summary=get_summary(source=a_submission,fields=["submission_time","get_score"])
    aq_submissions=a_submission.assignmentquestionsubmission_set.all()
    q_submission_reports=[a.question_submission.get_analysis_report() for a in aq_submissions]
    return render(request,"app-assignment/class-assignmentsubmission/report_template.html",{
        'assignment_summary':assignment_summary,
        'assignment_submission_summary':a_submission_summary,
        'question_submission_reports':q_submission_reports
    })

def assignment_submission_find_strange_code(request,object_slug):
    assignment=get_object_or_404(Assignment,slug=object_slug)
    return task_find_strange_submission(request,assignment)

@csrf_exempt
def assignment_submission_create(request,object_slug):
    assignment=get_object_or_404(Assignment,slug=object_slug)
    questions=assignment.questions()
    assignment_summary=get_summary(source=assignment,fields=["title","description","end_submission_time","get_instruction_file_link"])
    if (assignment.get_number_of_attempts_remaining(user=request.user)<=0):
        messages.info(request,"Attempts for"+assignment+" have been used up!")
        return HttpResponseRedirect(reverse("home"))
    if (request.POST):
        code_list=request.POST.getlist("code")
        preprocess_assignment_submission(assignment=assignment,user=request.user)
        # create assignment submission
        a_submission=AssignmentSubmission.objects.create(submitted_by=request.user,
                                            submission_time=datetime.now(),
                                            assignment=assignment)
        # store the code and create question submissions
        q_submissions=create_question_submissions_from_code(question_list=questions,code_list=code_list,task=assignment,user=request.user)
        # create assignment question submission
        for q_submission in q_submissions:
            aq_submission=AssignmentQuestionSubmission.objects.create(assignment_submission=a_submission,
                                                        question_submission=q_submission,
                                                        weightage=assignment.get_question_weightage(question=q_submission.question))
            aq_submission.save()
        # 5. run test if required
        if (assignment.is_auto_run_test()):
            for q_s in q_submissions:
                grade_question_submission_and_save_result(q_s)
        postprocess_assignment_submission(assignment=assignment,user=request.user)
        # 6. return a page
        messages.info(request,"Assignment has been successfully submitted")
        return HttpResponseRedirect(reverse('assignment_submission_view',args=[a_submission.id]))
    else:
        if (len(AssignmentAttemptRecord.objects.filter(assignment=assignment,record__user=request.user))>0):
            messages.info(request,"You have already submitted for this assignment. Please note that old submission will be discarded once new submission is made!")
    return render(request,"app-assignment/class-assignmentsubmission/create.html",{"assignment_summary":assignment_summary,"questions":questions})

def preprocess_assignment_submission(assignment,user):
    assignment.assignmentsubmission_set.filter(submitted_by=user).delete()

def postprocess_assignment_submission(assignment,user):
    try:
        ass_attempt_record=AssignmentAttemptRecord.objects.get(assignment=assignment,
                                        record__user=user)
        ass_attempt_record.increment_number_of_attempts()
    except:
        AssignmentAttemptRecord.create_and_save_initial_record(assignment=assignment,user=user)

#-----------------------for creating submission data sheets--------------------------
def assignment_submission_create_result_sheet(request,object_slug):
    from assignment.resultstatistic import AssignmentResultTableGenerator
    return assignment_submission_create_data_sheet(request,object_slug,table_generator_cls=AssignmentResultTableGenerator,file_postfix="score-sheet")

def assignment_submission_create_data_sheet(request,object_slug,table_generator_cls,file_postfix):
    assignment=get_object_or_404(Assignment,slug=object_slug)
    generator=table_generator_cls(assignment=assignment)
    result_table=generator.get_result_table()
    return csv_response(request,data_table=result_table,file_name="assignment-" + assignment.title + "-" +file_postfix)

#-----------------------------spot invalid code--------------------------------------------
def assignment_submission_validate_requirement(request,object_slug):
    assignment=get_object_or_404(Assignment,slug=object_slug)
    return task_validate_submissions_against_requirement(request,assignment.get_question_submissions())