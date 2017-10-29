import os
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator,MaxValueValidator
from django.template.defaultfilters import slugify
from appglobal.helper import get_summary,get_or_none
from question.models import QuestionSubmission,Question,TestCaseResult
from account.models import StudentGroup,AttemptRecord
from account.helper import is_staff
from apassite.settings import INSTRUCTION_FILE_RELATIVE_PATH
# Create your models here.
class Assignment(models.Model):
    RUN_TEST_AUTO_OPTION=0
    RUN_TEST_MANUAL_OPTION=1
    RUN_TEST_OPTIONS=(
        (RUN_TEST_AUTO_OPTION,'Run test automatically upon student submission'),
        (RUN_TEST_MANUAL_OPTION,'Run tests when required by the staff')
    )
    title=models.CharField(max_length=200,unique=True)
    description=models.TextField()
    start_submission_time=models.DateTimeField()
    end_submission_time=models.DateTimeField()
    instruction_file=models.FileField(upload_to=INSTRUCTION_FILE_RELATIVE_PATH["assignment"],null=True,blank=True)
    groups=models.ManyToManyField(StudentGroup,null=True,blank=True)#groups to receive this assignment
    run_test_option=models.IntegerField(choices=RUN_TEST_OPTIONS,default=RUN_TEST_MANUAL_OPTION)
    max_number_of_attempts=models.IntegerField(default=3,
        validators=[
            MaxValueValidator(100),
            MinValueValidator(1)
        ])
    slug=models.SlugField(default="",unique=True)

    def __unicode__(self):
        return "[Assignment]"+self.title

#-----------------------------crud---------------------------
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Assignment,self).save(*args, **kwargs)

    @staticmethod
    def clear_submissions():
        assignments=Assignment.objects.all()
        for assignment in assignments:
            a_submissions=assignment.assignmentsubmission_set.all()
            assignment.assignmentattemptrecord_set.all().delete()
            for a_submission in a_submissions:
                a_submission.clean_up()
                a_submission.delete()

#-------------------------attribute methods------------------------
    @staticmethod
    def get_student_can_submit(user,sort_by,**kwargs):
        can_submit_assignments=[]
        assignments=Assignment.objects.filter(**kwargs).order_by(sort_by) if sort_by else Assignment.objects.filter(**kwargs)
        # filtering by groups
        groups=StudentGroup.get_student_group_for_user(user)
        return [a for a in assignments if a.is_for_groups(groups) and a.is_in_submission_period() and a.get_number_of_attempts_remaining(user=user)>0]

    def get_receiver_groups(self):
        group_names=[group.name for group in self.groups.all()]
        return " , ".join(group_names)

    def get_run_test_option(self):
        return self.RUN_TEST_OPTIONS[self.run_test_option][1]

    def is_auto_run_test(self):
        return self.run_test_option!=self.RUN_TEST_MANUAL_OPTION

    def has_ungraded_submission(self):
        if (self.run_test_option!=self.RUN_TEST_MANUAL_OPTION):
            return False
        return len([a for a in self.assignmentsubmission_set.all() if (not a.is_grading_finished())])>0

    def has_submission(self):
        return len([a for a in self.assignmentsubmission_set.all()])>0

    def questions(self):
        return [a.question for a in AssignmentQuestion.objects.filter(assignment=self)]

    def get_submitted_questions(self):
        a_submissions=self.assignmentsubmission_set.all()
        questions=[a.question_submission.question for submission in a_submissions for a in submission.assignmentquestionsubmission_set.all()]
        return list(set(questions))

    # used in finding strange code
    def get_question_submissions(self,question=None):
        a_submissions=self.assignmentsubmission_set.all()
        all_question_submissions=[a.question_submission for submission in a_submissions for a in submission.assignmentquestionsubmission_set.all()]
        return [q for q in all_question_submissions if q.question==question or not question]

    def is_in_submission_period(self):
        current_time=timezone.now()
        return  (current_time>self.start_submission_time and current_time<self.end_submission_time)

    def is_for_groups(self,groups):
        return len([a for a in groups if (a in self.groups.all())])>0

    def get_number_of_attempts_remaining(self,user):
        record=get_or_none(AssignmentAttemptRecord,assignment=self,record__user=user)
        return self.max_number_of_attempts-record.get_number_of_attempts() if record else self.max_number_of_attempts

    def get_question_weightage(self,question):
        try:
            return AssignmentQuestion.objects.get(assignment=self,question=question).weightage
        except:
            return 0

    def get_submission_link(self):
        url=reverse('assignment_submission_list_staff',args=[self.slug])
        html="""<a href="{}">Submissions</a>""".format(url)
        return html

    def get_instruction_file_link(self):
        if (not self.instruction_file):
            return "NIL"
        file_name=os.path.basename(self.instruction_file.url)
        url=reverse("assignment_file_download",args=[file_name])
        html="""<a href="{}" target="_blank">
                   <span class="badge">{}</span></a>""".format(url,"Download")
        return html

    def get_start_submission(self):
        url=reverse('assignment_submission_create_student',args=[self.slug])
        html="""<a href="{}"><i class='fa fa-edit'></a>""".format(url)
        return html


class AssignmentQuestion(models.Model):
    """
    This is an association class for building m2m relationship between Assignment and Question
    """
    assignment=models.ForeignKey(Assignment)
    question=models.ForeignKey(Question)
    weightage=models.IntegerField()

    def get_question_title(self):
        return self.question.title

    @staticmethod
    def get_question_weightage(assignment,question):
        a_qs=AssignmentQuestion.objects.filter(assignment=assignment,question=question)
        if (len(a_qs)>0):
            return a_qs[0].weightage


class AssignmentSubmission(models.Model):
    submitted_by=models.ForeignKey(User)
    submission_time=models.DateTimeField(auto_now=True)
    assignment=models.ForeignKey(Assignment)


    def __unicode__(self):
        return self.assignment.title

#------------------------crud----------------------------
    def clean_up(self):
        aq_submissions=self.assignmentquestionsubmission_set.all()
        self.assignment.assignmentattemptrecord_set.all().delete()
        for aq_submission in aq_submissions:
            aq_submission.delete()
        AssignmentAttemptRecord.objects.filter(assignment=self.assignment,record__user=self.submitted_by).delete()

#-------------------attribute methods---------------------------
    def _get_score(self):
        scores=[a.get_weighted_score() for a in self.assignmentquestionsubmission_set.all()]
        return sum(scores)
    score=property(_get_score)

    def get_score(self):
        return self.score if self.is_grading_finished() else "Grading not finished"

    def get_submitted_by(self):
        return self.submitted_by.username

    def get_question_submissions(self):
        assignment_question_submissions=self.assignmentquestionsubmission_set.all()
        return [q.question_submission for q in assignment_question_submissions]

    def get_score_by_question(self,question):
        asq_set=self.assignmentquestionsubmission_set.filter(question_submission__question=question)
        return asq_set[0].get_score() if asq_set else "N.A."

    def is_completed(self):
        # check whether the number of question submissions is the same as the number of questions
        # if yes, assume it's completed
        question_submissions=AssignmentQuestionSubmission.objects.filter(assignment_submission=self)
        questions=self.assignment.questions()
        return len(question_submissions)==len(questions)

    is_completed=property(is_completed)

    def is_grading_finished(self):
        aq_submissions=AssignmentQuestionSubmission.objects.filter(assignment_submission=self)
        for aq_submission in aq_submissions:
            if (not aq_submission.question_submission.is_grading_finished):
                return  False
        return True

    def get_number_of_question_submissions(self):
        return len(self.assignmentquestionsubmission_set.all())

    def get_redirect_url(self):
        return reverse("assignment_submission_list_staff",args=[self.assignment.slug])

    def get_title(self):
        return self.assignment.title

    def get_detail_link(self):
        url=reverse('assignment_submission_view',args=[self.id])
        html="""<a href="{}"><i class="fa fa-eye"></i></a>""".format(url)
        return html

    def get_analysis_report(self):
        """
        :return: a html string
        """
        aq_submissions=self.assignmentquestionsubmission_set.all()
        q_submission_reports=[a.question_submission.get_analysis_report() for a in aq_submissions]
        return render_to_string("app-assignment/class-assignmentsubmission/report_template.html",{
            'assignment':self.assignment,
            'assignment_submission':self,
            'question_submission_reports':q_submission_reports
        })




class AssignmentQuestionSubmission(models.Model):
    assignment_submission=models.ForeignKey(AssignmentSubmission)
    question_submission=models.OneToOneField(QuestionSubmission)
    weightage=models.IntegerField()


#---------------------crud----------------------------
    def delete(self, *args, **kwargs):
        self.question_submission.delete()
        return super(self.__class__, self).delete(*args, **kwargs)

#-----------------attribute methods------------------------------------

    def get_question_title(self):
        return self.question_submission.question.title

    def get_score(self):
        return self.question_submission.get_score()

    def get_weighted_score(self):
        return int(self.weightage * self.question_submission.score / 100.0)

    def get_detail_link(self):
        url=reverse('question_submission_view_student',args=[self.question_submission.id])
        html="""<a href="{}"><i class="fa fa-eye"></i></a>""".format(url)
        return html

    def get_detail_link_for_student(self):
        if (self.allow_detail_access_for_student()):
            return self.get_detail_link()
        else:
            return "Not accessible now"

    def allow_detail_access_for_student(self):
        return datetime.utcnow()>self.assignment_submission.assignment.end_submission_time.replace(tzinfo=None)\
            and self.question_submission.is_grading_finished


class AssignmentAttemptRecord(models.Model):
    record=models.OneToOneField(AttemptRecord)
    assignment=models.ForeignKey(Assignment)

#------------------attribute methods--------------
    def increment_number_of_attempts(self):
        record=self.record
        record.number_of_attempts=record.number_of_attempts+1
        record.save()

    def get_number_of_attempts(self):
        return self.record.number_of_attempts

#------------------------crud----------------------
    @staticmethod
    def create_and_save_initial_record(user,assignment):
        record=AttemptRecord.objects.create(user=user,
                                     number_of_attempts=1)
        record.save()
        aa_record=AssignmentAttemptRecord.objects.create(
            assignment=assignment,
            record=record
        )
        aa_record.save()
        return aa_record