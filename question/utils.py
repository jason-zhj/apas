from assignment.models import AssignmentQuestionSubmission
from onlinetest.models import OnlineTestQuestionSubmission

def get_question_associated_submission(question_submission):
    try:
        assoc_submission=AssignmentQuestionSubmission.objects.get(question_submission=question_submission)
    except:
        assoc_submission=OnlineTestQuestionSubmission.objects.get(question_submission=question_submission)
    return assoc_submission
