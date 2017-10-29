import os
from datetime import datetime,timedelta

from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator,MaxValueValidator

from appglobal.helper import get_or_none
from question.models import QuestionSubmission,QuestionPool
from account.models import StudentGroup,AttemptRecord
from account.helper import is_staff
from apassite.settings import INSTRUCTION_FILE_RELATIVE_PATH

class OnlineTest(models.Model):
    RUN_TEST_AUTO_OPTION=0
    RUN_TEST_MANUAL_OPTION=1
    RUN_TEST_OPTIONS=(
        (RUN_TEST_AUTO_OPTION,'Run test automatically upon student submission'),
        (RUN_TEST_MANUAL_OPTION,'Run tests when required by the staff')
    )
    title=models.CharField(max_length=200,unique=True)
    description=models.TextField()
    start_test_time=models.DateTimeField(verbose_name="Time from when students can start doing the test") # when to enable submission of the test
    end_test_time=models.DateTimeField(verbose_name="Deadline for students to start the test")
    time_limit=models.IntegerField(default=10,verbose_name="Time Limit (in minutes)") # time limit for the test in minutes
    instruction_file=models.FileField(upload_to=INSTRUCTION_FILE_RELATIVE_PATH["onlinetest"],null=True,blank=True)
    slug=models.SlugField(unique=True)
    groups=models.ManyToManyField(StudentGroup,null=True,blank=True)
    run_test_option=models.IntegerField(choices=RUN_TEST_OPTIONS,default=RUN_TEST_MANUAL_OPTION)
    max_number_of_attempts=models.IntegerField(default=3,
        validators=[
            MaxValueValidator(100),
            MinValueValidator(1)
        ])

    def __unicode__(self):
        return "[OnlineTest]"+self.title

#----------------------------crud----------------------------------
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(OnlineTest,self).save(*args, **kwargs)

    @staticmethod
    def clear_submissions():
        tests=OnlineTest.objects.all()
        for test in tests:
            t_submissions=test.onlinetestsubmission_set.all()
            test.onlinetestattemptrecord_set.all().delete()
            for t_submission in t_submissions:
                t_submission.clean_up()
                t_submission.delete()

#----------attribute methods---------------------
    def get_number_of_attempts_remaining(self,user):
        record=get_or_none(OnlineTestAttemptRecord,onlinetest=self,record__user=user)
        return self.max_number_of_attempts-record.get_number_of_attempts() if record else self.max_number_of_attempts

    def pools(self):
        return [a.question_pool for a in self.onlinetestquestionpool_set.all()]

    def is_auto_run_test(self):
        return (self.run_test_option!=self.RUN_TEST_MANUAL_OPTION)

    def get_randomly_selected_questions(self):
        """
        :return a list of tuples (question,weightage:int,question_pool)
        """
        ot_pools=self.onlinetestquestionpool_set.all()
        selected_questions=[]
        #-----------get selections----------
        for ot_pool in ot_pools:
            questions_from_pool=ot_pool.question_pool.get_random_questions(ot_pool.number_to_select)
            selected_questions.extend([(q,ot_pool.weightage,ot_pool.question_pool) for q in questions_from_pool])
        #-------shuffle the selections-------
        import random
        random.shuffle(selected_questions)
        return selected_questions

    def get_instruction_file_name(self):
        return os.path.basename(self.instruction_file.url) if self.instruction_file else ""

    def has_ungraded_submission(self):
        if (self.run_test_option!=self.RUN_TEST_MANUAL_OPTION):
            return False
        return len([a for a in self.onlinetestsubmission_set.all() if (not a.is_grading_finished())])>0

    def has_submission(self):
        return len([a for a in self.onlinetestsubmission_set.all()])>0

    def get_question_submissions(self,question=None):
        ot_submissions=self.onlinetestsubmission_set.all()
        otq_submissions=[]
        for ot_submission in ot_submissions:
            otq_submissions.extend(ot_submission.onlinetestquestionsubmission_set.all())
        return [a.question_submission for a in otq_submissions if ((not question) or a.question_submission.question==question)]

    def get_submitted_questions(self):
        # return list of questions that have submissions
        ot_submissions=self.onlinetestsubmission_set.all()
        questions=[a.question_submission.question for ot_submission in ot_submissions for a in ot_submission.onlinetestquestionsubmission_set.all()]
        return list(set(questions))

    def is_for_groups(self,groups):
        return len([a for a in self.groups.all() if a in groups])>0

    def has_been_submitted_by(self,user):
        return len(self.onlinetestsubmission_set.filter(submitted_by=user,is_completed=True))>0

    def is_in_submission_period(self):
        current_time=timezone.now()
        return True if  (current_time>self.start_test_time and current_time<self.end_test_time) else False


    def get_start_test_link(self):
        url=reverse('online_test_submission_create',args=[self.slug])
        html="""<a href="{}" onclick="return confirm('Once you start the test, you will not be able to access other sections in the system.Are you sure to start the test?');"><i class="fa fa-pencil-square-o"></i></a>""".format(url)
        return html

    def get_submissions_link(self):
        url=reverse('online_test_submission_list',args=[self.slug])
        html="""<a href="{}">Submissions</a>""".format(url)
        return html

#------------------------methods for summary----------------------------
    def get_instruction_file_link(self):
        if (not self.instruction_file):
            return "NIL"
        file_name=os.path.basename(self.instruction_file.url)
        url=reverse("onlinetest_file_download",args=[file_name])
        html="""<a href="{}" target="_blank">
                   <span class="badge">{}</span></a>""".format(url,"Download")
        return html

class OnlineTestQuestionPool(models.Model):
    online_test=models.ForeignKey(OnlineTest)
    question_pool=models.ForeignKey(QuestionPool)
    weightage=models.IntegerField() # weightage per question selected from the pool
    number_to_select=models.IntegerField(default=1) # number of questions to be selected from the pool

    def max_number_to_select(self):
        return len(self.question_pool.questions.all())

    def get_pool_name(self):
        return self.question_pool.title

class OnlineTestSubmission(models.Model):
    submitted_by=models.ForeignKey(User)
    submission_time=models.DateTimeField() # namely end test time
    online_test=models.ForeignKey(OnlineTest)
    # so far this is just a dummy field
    is_completed=models.BooleanField(default=True) # coz online test is finished on one go

    def __unicode__(self):
        return self.submitted_by.username
#-------------------for data listing-----------------------------
    @staticmethod
    def get_list_data(user,sort_by,**kwargs):
        if (is_staff(user)):
            return OnlineTestSubmission.objects.filter(**kwargs).order_by(sort_by) if sort_by else OnlineTestSubmission.objects.filter(**kwargs).order_by(sort_by)
        return OnlineTestSubmission.objects.filter(submitted_by=user,is_completed=True,**kwargs).order_by(sort_by) if sort_by else OnlineTestSubmission.objects.filter(submitted_by=user,is_completed=True,**kwargs)

#--------------------attribute methods----------------------------------
    def _get_score(self):
        scores=[a.get_weighted_score() for a in self.onlinetestquestionsubmission_set.all()]
        return sum(scores)

    score=property(_get_score)

    def get_scores_by_pool(self,q_pool):
        otq_submissions=self.onlinetestquestionsubmission_set.filter(question_pool=q_pool)
        return [a.get_score() for a in otq_submissions]

    @staticmethod
    def get_submissions_by_student(user):
        return OnlineTestSubmission.objects.filter(submitted_by=user,is_completed=True)

    def get_test_title(self):
        return self.online_test.title

    def get_questions_by_pool(self,pool):
        try:
            otq_submissions=OnlineTestQuestionSubmission.objects.filter(online_test_submission=self,question_pool=pool)
            return [a.question_submission.question for a in otq_submissions]
        except:
            return []

    def is_grading_finished(self):
        finished=True
        finished_status=[a.question_submission.is_grading_finished for a in self.onlinetestquestionsubmission_set.all()]
        return not (False in finished_status)

    def get_submittor_name(self):
        return self.submitted_by.username

#-------------------data manipulation methods=======================

    def clean_up(self,**kwargs):
        otq_submissions=self.onlinetestquestionsubmission_set.all()
        if (not kwargs.get('keep_attempt_record',False)):
            self.online_test.onlinetestattemptrecord_set.all().delete()
        for otq_submission in otq_submissions:
            # delete submitted files
            keep_files=kwargs.get("keep_files",False)
            otq_submission.question_submission.clean_up(keep_files=keep_files)
            otq_submission.delete()


#-----------------methods for table and summary--------------------------
    def get_detail_link(self):
        url=reverse('online_test_submission_view_student',args=[self.id])
        html="""<a href="{}"><i class="fa fa-eye"></i></a>""".format(url)
        return html

    def get_redirect_url(self):
        return reverse("online_test_submission_list",args=[self.online_test.slug])

    def get_score(self):
        return self.score if self.is_grading_finished() else "Grading not finished"

class OnlineTestQuestionSubmission(models.Model):
    online_test_submission=models.ForeignKey(OnlineTestSubmission)
    question_submission=models.OneToOneField(QuestionSubmission)
    question_pool=models.ForeignKey(QuestionPool,on_delete=models.SET_NULL,null=True) # which pool is the question selected from
    weightage=models.IntegerField(default=0) # the weightage of this submission for the score of the overall submission

    def get_weighted_score(self):
        return int(self.weightage * self.question_submission.score / 100.0)

    def delete(self, *args, **kwargs):
        self.question_submission.delete()
        return super(self.__class__, self).delete(*args, **kwargs)

    def update_score(self):
        self.online_test_submission.update_score()

    #----------------methods for tables---------------------
    def get_question_title(self):
        return self.question_submission.question.title

    def get_score(self):
        return self.question_submission.score if self.question_submission.is_grading_finished else "Grading not finished"

    def get_detail_link(self):
        url=reverse('question_submission_view_student',args=[self.question_submission.id])
        html="""<a href="{}"><i class="fa fa-eye"></i></a>""".format(url)
        return html if self.question_submission.is_grading_finished else "Grading not finished"

    def allow_detail_access_for_student(self):
        online_test=self.online_test_submission.online_test
        return datetime.utcnow()>online_test.end_test_time.replace(tzinfo=None)+timedelta(minutes=online_test.time_limit)\
            and self.question_submission.is_grading_finished

    def get_detail_link_for_student(self):
        if (self.allow_detail_access_for_student()):
            return self.get_detail_link()
        else:
            return "Not accessible now"

class OnlineTestAttemptRecord(models.Model):
    record=models.OneToOneField(AttemptRecord)
    onlinetest=models.ForeignKey(OnlineTest)

#------------------attribute methods--------------
    def increment_number_of_attempts(self):
        record=self.record
        record.number_of_attempts=record.number_of_attempts+1
        record.save()

    def get_number_of_attempts(self):
        return self.record.number_of_attempts

#------------------------crud----------------------
    @staticmethod
    def create_and_save_initial_record(user,onlinetest):
        record=AttemptRecord.objects.create(user=user,
                                     number_of_attempts=1)
        record.save()
        aa_record=OnlineTestAttemptRecord.objects.create(
            onlinetest=onlinetest,
            record=record
        )
        aa_record.save()
        return aa_record