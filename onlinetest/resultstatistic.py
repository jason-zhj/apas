from abc import ABCMeta,abstractmethod

class TestDataTableGenerator(object):
    __metaclass__=ABCMeta

    def __init__(self,test):
        self.test=test

    def get_result_table(self):
        test=self.test
        results=[] #overall table
        o_submissions=[a for a in test.onlinetestsubmission_set.all() if a.is_grading_finished]
        otq_pools=test.onlinetestquestionpool_set.all()
        # create title row
        results.append(self._get_title_row(otq_pools=otq_pools))
        # create data rows
        self._populate_data_rows(rows=results,o_submissions=o_submissions, otq_pools=otq_pools)
        return results

    @abstractmethod
    def _populate_data_rows(self,rows,o_submissions,otq_pools):
        pass

    def _get_title_row(self,otq_pools):
        result=['username','full name','total score']
        for ot_pool in otq_pools:
            for i in range(ot_pool.number_to_select):
                result.append(ot_pool.get_pool_name()+" ( "+str(ot_pool.weightage)+"% )")
        return result


class TestResultTableGenerator(TestDataTableGenerator):
    def _populate_data_rows(self,rows,o_submissions,otq_pools):
        for submission in o_submissions:
            new_result=[]
            new_result.append(submission.submitted_by.username)
            new_result.append(submission.submitted_by.studentuserprofile.get_full_name())
            new_result.append(submission.score)
            new_result.extend(self._get_question_score_by_pool_sequence(otq_pools=otq_pools,ot_submission=submission))
            rows.append(new_result)
        rows.append(self._get_summary_row(data_rows=rows[1:],start_summary_at=2))

    def _get_question_score_by_pool_sequence(self,ot_submission,otq_pools):
        result=[]
        for ot_pool in otq_pools:
            result.extend(ot_submission.get_scores_by_pool(ot_pool.question_pool))
        return result

    def _get_summary_row(self,data_rows,start_summary_at):
        result=[]
        for i in range(start_summary_at):
            result.append('')
        for i in range(start_summary_at,len(data_rows[0])):
            scores=[a[i] for a in data_rows]
            avg=sum(scores) / float(len(scores))
            result.append("Average: " + str(avg))
        return result

class AttemptedQuestionTableGenerator(TestDataTableGenerator):
    def _populate_data_rows(self,rows,o_submissions,otq_pools):
        for submission in o_submissions:
            new_result=[]
            new_result.append(submission.submitted_by.username)
            new_result.append(submission.submitted_by.studentuserprofile.get_full_name())
            new_result.append(submission.score)
            new_result.extend(self._get_question_title_by_pool_sequence(otq_pools=otq_pools,ot_submission=submission))
            rows.append(new_result)

    def _get_question_title_by_pool_sequence(self,otq_pools,ot_submission):
        questions=[]
        for otq_pool in otq_pools:
            questions.extend(ot_submission.get_questions_by_pool(pool=otq_pool.question_pool))
        return [a.title if a else "N.A." for a in questions]
