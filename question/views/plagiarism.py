from django.shortcuts import get_object_or_404,render

from appglobal import get_summary
from question.plagiarism import create_plagiarism_checker
from question.models import Question,QuestionSubmission

MATRICES = 'matrices'
QUESTION_SUBMISSIONS='question_submissions'
PLAGIARISMS = 'plagiarisms'
QUESTIONS='questions'

def task_submission_plagiarism_check(request,object_slug,model_class):
    """
    :param request:
    :param object_slug: the slug for the model_class
    :param model_class: the instance of this class needs have two methods get_submitted_questions(), get_question_submissions(question_id)
    :return:
    """
    task=get_object_or_404(model_class,slug=object_slug)
    questions=task.get_submitted_questions()
    question_tuple_list=[]
    # initialize session data
    request.session[PLAGIARISMS]=[]
    request.session[MATRICES]=[]
    request.session[QUESTION_SUBMISSIONS]=[]
    request.session[QUESTIONS]=[question.id for question in questions]
    plagiarism_found=[False for x in range(len(questions))]
    for i in range(len(questions)):
        if (question_submission_plagiarism_check(request.session,task,questions[i])):
            plagiarism_found[i]=True
        question_tuple_list.append((questions[i],plagiarism_found[i]))

    return render(request,"app-question/plagiarism-result-overall.html",{"question_tuples":question_tuple_list})


# helper method for plagiarism checking
def question_submission_plagiarism_check(session,task,question):
    """
    :param session:
    :param assignment:
    :param question:
    :return: true if plagiarism is found among the submissions for the question
    """
    question_submissions=task.get_question_submissions(question=question)
    m_length=len(question_submissions)
    matrix = [[None for x in range(m_length)] for x in range(m_length)]  # for recording the result of plagiarism checking
    plagiarism_record=[[] for x in range(m_length)]
    has_plagiarism=False

    # do plagiarism checking
    for i in range(m_length):
        for j in range(m_length):
            if (i==j):
                # avoid comparing the submission to itself
                continue
            if (matrix[i][j] is None):
                checker=create_plagiarism_checker(question_submissions[i].get_source_code(),question_submissions[j].get_source_code(),question.required_language)
                report=checker.get_report()
                matrix[i][j]=report
                matrix[j][i]=report
                if (checker.isPlagiarised()):
                    has_plagiarism=True
                    plagiarism_record[i].append(j)
                    plagiarism_record[j].append(i)

    session[PLAGIARISMS].append(plagiarism_record)
    session[MATRICES].append(matrix)
    session[QUESTION_SUBMISSIONS].append([question_submission.id for question_submission in question_submissions])

    return has_plagiarism

# view for plagiarism checking
def question_submission_plagiarism_check_result(request,question_slug):
    index=0
    question=get_object_or_404(Question,slug=question_slug)
    question_summary=get_summary(source=question,fields=["title","content","required_language"])
    question_ids=request.session[QUESTIONS]
    for i in range(len(question_ids)):
        if (question_ids[i]==question.id):
            index=i
            break

    plagiarism_record=request.session[PLAGIARISMS][index]
    matrix=request.session[MATRICES][index]
    question_submission_ids=request.session[QUESTION_SUBMISSIONS][index]
    # pack the data into a nested list for ease of displaying the data
    packed_data=get_plagiarism_result_data(plagiarism_record=plagiarism_record,matrix=matrix,question_submission_ids=question_submission_ids)
    return render(request,"app-question/plagiarism-result.html",{'question_summary':question_summary,'data':packed_data})

# packed the computed data into a list
def get_plagiarism_result_data(plagiarism_record,matrix,question_submission_ids):
    """
    pack the plagiarism checking data into a list
    :param plagiarism_record:
    :param matrix:
    :param question_submission_ids:
    :return: a list of tuples
    """
    packed_data=[]

    for i in range(len(question_submission_ids)):
        question_submission_A=QuestionSubmission.objects.get(id=question_submission_ids[i])
        evidence=[]

        if (len(plagiarism_record[i])==0):
            continue

        for index in plagiarism_record[i]:
            # get the other submission
            submission_B_id=question_submission_ids[index]
            question_submission_B=QuestionSubmission.objects.get(id=submission_B_id)
            evidence.append(
                (question_submission_B,matrix[i][index])
            )

        packed_data.append(
            (question_submission_A,evidence)
        )

    return packed_data
