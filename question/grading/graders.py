from abc import ABCMeta,abstractmethod

from appglobal import normalize_score

def create_testcase_result(**kwargs):
    return kwargs

def create_testcase_set_result(**kwargs):
    return kwargs

class BaseGrader(object):
    """
    Class for grading one program
    """

    __metaclass__=ABCMeta
    def __init__(self,testcase_data,program_tester):
        """
        :param testcase_data: a list of question.Models.TestCase or question.Models.TestCaseSet
        :param program_file_path: complete path of the program file
        :param language:a string indicating the required language
        :param output_checking_choice: an int indicating the checking method
        :exception if output_checking_choice or language is not valid
        """
        self.testcase_data=testcase_data
        self.program_tester=program_tester

    def do_grading(self):
        """
        :return: {test_results: list of question.models.TestcaseResult(questionsubmission not set), score : int}
        """
        overall_score,test_results=self.run_test_cases(program_tester=self.program_tester)

        # processing after running
        self.post_testing()
        # return message
        return {"score":overall_score,"test_results":test_results}

    def post_testing(self):
        pass

    @abstractmethod
    def run_test_cases(self,program_tester):
        """
        :param program_tester:
        :return: overall_score and test results
        """
        return 0,[]

class IndividualTestCaseGrader(BaseGrader):
    """
    Used when the testcase_data is a list of TestCase
    """
    def run_test_cases(self,program_tester):
        overall_score=0
        testcase_results=[]
        for testcase in self.testcase_data:
            test_feedback=program_tester.run_testcase(testcase)
            overall_score += testcase.get_weighted_score(test_feedback['score'])
            new_testcase_result=create_testcase_result(is_pass=test_feedback['pass'],score=test_feedback['score'],result_brief=test_feedback['result'],test_case=testcase)
            testcase_results.append(new_testcase_result)
        return overall_score,testcase_results

class TestCaseSetGrader(BaseGrader):
    """
    Used when the testcase_data is a list of TestCaseSet
    """
    def run_test_cases(self,program_tester):
        test_results=[]
        testcase_sets=self.testcase_data
        overall_score=0
        for testcase_set in testcase_sets:
            testcases=testcase_set.testcase_set.all()
            scores=[]
            testcase_results=[]
            #-------run testcases in the set
            for testcase in testcases:
                test_feedback=program_tester.run_testcase(testcase)
                #-----------save testcaseresult
                new_testcase_result=create_testcase_result(is_pass=test_feedback['pass'],score=test_feedback['score'],result_detail=test_feedback['result'],test_case=testcase)
                testcase_results.append(new_testcase_result)
                #-----------record score-----------
                scores.append(test_feedback['score'])
            #---------------compute score for the set
            if (testcase_set.is_pick_minimum_mark()):
                tsr=create_testcase_set_result(score=min(scores),test_case_set=testcase_set)
                test_results.append((tsr,testcase_results))
                overall_score+=testcase_set.get_weighted_score(min(scores))
            else:
                # score for each test case passed
                score_for_set=0
                weight_per_testcase=100.0/len(scores)
                for score in scores:
                    score_for_set += normalize_score(weight_per_testcase * score / 100.0)
                overall_score +=testcase_set.get_weighted_score(score_for_set)
                tsr=create_testcase_set_result(score=score_for_set,test_case_set=testcase_set)
                test_results.append((tsr,testcase_results))

        return overall_score,test_results