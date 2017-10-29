from datetime import datetime,timedelta
from django.utils import timezone
from django.shortcuts import get_object_or_404

from question.models import Question,QuestionPool
from question import create_question_submissions_from_code,grade_question_submission_and_save_result

from .models import OnlineTestSubmission,OnlineTestQuestionSubmission,OnlineTestAttemptRecord
from .settings import IN_TEST

QUESTION_ID_LIST_NAME="question_ids"
WEIGHTAGE_LIST_NAME="weightages"
POOL_ID_LIST="pool_ids"
END_TEST_TIME_NAME="end_test_time"

RESPONSE_TIME_MARGIN=3 #in seconds

class OnlineTestHandler(object):
    onlinetest=None
    request=None
    current_time=None



    def __init__(self,onlinetest,request):
        self.onlinetest=onlinetest
        self.request=request
        self.current_time=datetime.now()
        self.current_time_with_tz=timezone.now()

    def is_submission_open(self):
        if (END_TEST_TIME_NAME in self.request.session.keys()):
            # in test period now
            if (self.current_time-timedelta(seconds=RESPONSE_TIME_MARGIN) < self.construct_datetime_from_list(self.request.session[END_TEST_TIME_NAME])
                and self.onlinetest.get_number_of_attempts_remaining(user=self.request.user)>0):
                return True
            else:
                # remove the end_test_time key
                self.request.session.pop(END_TEST_TIME_NAME,None)
        else:
            # not in test period
            if (not self.onlinetest.has_been_submitted_by(user=self.request.user) and self.current_time_with_tz<self.onlinetest.end_test_time):
                return True
        return False

    def setup_test_session(self):
        session_keys=self.request.session.keys()
        if (QUESTION_ID_LIST_NAME in session_keys and WEIGHTAGE_LIST_NAME in session_keys and POOL_ID_LIST in session_keys and END_TEST_TIME_NAME in session_keys):
            return # if session already contains those things, no need to compute again
        test=self.onlinetest
        request=self.request
        test_question_info_list=test.get_randomly_selected_questions()
        test_questions=[q[0] for q in test_question_info_list]
        # store essential session info
        request.session[QUESTION_ID_LIST_NAME]=[q.id for q in test_questions]
        request.session[WEIGHTAGE_LIST_NAME]=[q[1] for q in test_question_info_list]
        request.session[POOL_ID_LIST]=[q[2].id for q in test_question_info_list]
        # store end submission time
        request.session[END_TEST_TIME_NAME]=self.get_end_time_list()
        request.session[IN_TEST]=True

    def create_or_update_test_submission(self):
        """
        :return: boolean,submission
        the boolean is to indicate whether the new submission is saved or not,
        if not, the new submission's score is lower than the old one
        """

        request=self.request
        test=self.onlinetest
        # prepare old submissions
        old_test_submissions=test.onlinetestsubmission_set.filter(submitted_by=request.user)
        old_submission=old_test_submissions[0] if old_test_submissions else None
        # create new submission
        code_list=request.POST.getlist("code")
        question_list=[get_object_or_404(Question,id=q) for q in request.session[QUESTION_ID_LIST_NAME]]
        # store submission time
        ot_submission=OnlineTestSubmission.objects.create(
            submitted_by=self.request.user,
            submission_time=datetime.now(),
            online_test=self.onlinetest
        )
        ot_submission.save()
        q_submission_list=create_question_submissions_from_code(code_list=code_list,question_list=question_list,task=test,user=request.user)
        for i in range(len(q_submission_list)):
            q_submission=q_submission_list[i]
            # 4. store onlinetestquestionsubmission
            otq_submission=OnlineTestQuestionSubmission.objects.create(
                online_test_submission=ot_submission,
                question_submission=q_submission,
                question_pool=get_object_or_404(QuestionPool,id=request.session[POOL_ID_LIST][i]),
                weightage=request.session[WEIGHTAGE_LIST_NAME][i]
            )
            otq_submission.save()

        self.record_user_attempt()

        # 5. run test if required
        if (test.is_auto_run_test()):
            for q_s in q_submission_list:
                grade_question_submission_and_save_result(q_s)
            if (old_submission and ot_submission.score < old_submission.score):
                ot_submission.clean_up(keep_attempt_record=True,keep_files=True)
                ot_submission.delete()
                return False,old_submission
            else:
                if (old_submission):
                    old_submission.clean_up(keep_attempt_record=True,keep_files=True)
                    old_submission.delete()
                return True,ot_submission
        else:
            # delete old one straightaway
            if (old_submission):
                old_submission.clean_up(keep_attempt_record=True,keep_files=True)
                old_submission.delete()
            return True,ot_submission


    def get_test_questions(self):
        return [get_object_or_404(Question,id=a) for a in self.request.session[QUESTION_ID_LIST_NAME]]

    def get_end_time_list(self):
        try:
            return self.request.session[END_TEST_TIME_NAME]
        except:
            end_test_time=datetime.now() +timedelta(minutes = self.onlinetest.time_limit)
            return [end_test_time.year,end_test_time.month,end_test_time.day,end_test_time.hour,end_test_time.minute,end_test_time.second]


    def construct_datetime_from_list(self,time_list):
        return datetime(time_list[0],time_list[1],time_list[2],time_list[3],time_list[4],time_list[5],0)

    def clear_test_session(self):
        self.request.session.pop(END_TEST_TIME_NAME,None)
        self.request.session.pop(QUESTION_ID_LIST_NAME,None)
        self.request.session.pop(WEIGHTAGE_LIST_NAME,None)
        self.request.session.pop(POOL_ID_LIST,None)
        self.request.session.pop(IN_TEST,None)


    def record_user_attempt(self):
        try:
            attempt_record=self.onlinetest.onlinetestattemptrecord_set.get(record__user=self.request.user)
            attempt_record.increment_number_of_attempts()
        except:
            OnlineTestAttemptRecord.create_and_save_initial_record(onlinetest=self.onlinetest,user=self.request.user)