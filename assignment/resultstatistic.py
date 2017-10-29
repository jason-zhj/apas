from abc import ABCMeta,abstractmethod

class AssignmentDataTableGenerator(object):
    __metaclass__=ABCMeta

    def __init__(self,assignment):
        self.assignment=assignment

    def get_result_table(self):
        assignment=self.assignment
        results=[] #overall table
        ass_submissions=[a for a in assignment.assignmentsubmission_set.all() if a.is_grading_finished()]
        ass_questions=assignment.assignmentquestion_set.all()
        # create title row
        results.append(self._get_title_row(ass_questions=ass_questions))
        # create data rows
        self._populate_data_rows(rows=results, ass_submissions=ass_submissions, ass_questions=ass_questions)
        return results

    @abstractmethod
    def _populate_data_rows(self,rows,ass_submissions,ass_questions):
        pass

    def _get_title_row(self,ass_questions):
        result=['username','full name','total score']
        for ass_q in ass_questions:
            result.append(ass_q.get_question_title()+" ( "+str(ass_q.weightage)+"% )")
        return result


class AssignmentResultTableGenerator(AssignmentDataTableGenerator):
    def _populate_data_rows(self,rows,ass_submissions,ass_questions):
        for submission in ass_submissions:
            new_result=[]
            new_result.append(submission.submitted_by.username)
            new_result.append(submission.submitted_by.studentuserprofile.get_full_name())
            new_result.append(submission.score)
            new_result.extend(self._get_question_score(ass_questions=ass_questions, ass_submission=submission))
            rows.append(new_result)
        rows.append(self._get_summary_row(data_rows=rows[1:],start_summary_at=2))

    def _get_question_score(self,ass_submission,ass_questions):
        result=[]
        for ass_q in ass_questions:
            result.append(ass_submission.get_score_by_question(ass_q.question))
        return result

    def _get_summary_row(self,data_rows,start_summary_at):
        result=[]
        for i in range(start_summary_at):
            result.append('')
        for i in range(start_summary_at,len(data_rows[0])):
            scores=[float(a[i]) for a in data_rows if self._is_valid_number(a[i])]
            avg=sum(scores) / float(len(scores))
            result.append("Average: " + str(avg))
        return result

    def _is_valid_number(self,number):
        try:
            a=float(number)
            return True
        except:
            return False