from abc import ABCMeta,abstractmethod

class BaseStangeCodeChecker(object):
    __metaclass__=ABCMeta

    def __init__(self,suggested_code,language,code_template=""):
        self.suggested_code=suggested_code
        self.language=language
        self.code_template=code_template


    @abstractmethod
    def check_code(self,code):
        """
        :param code: string
        :return: a dict {'report','is_strange'}
        """
        pass

    @abstractmethod
    def get_solution_metrics_report(self):
        """
        :return: a report on metrics of the solution code
        """
        pass

class HalsteadStrangeCodeChecker(BaseStangeCodeChecker):

    def _get_code_metrics(self,code):
        from question import tokenizer
        return tokenizer.get_tokenization_result(code=code,required_language=self.language,code_template=self.code_template)['values']

    def get_solution_metrics_report(self):
        if (not hasattr(self,"solution_metrics")):
            self.solution_metrics=self._get_code_metrics(code=self.suggested_code)
        return self._get_halstead_metrics_text(metrics_list=self.solution_metrics)

    def check_code(self,code):
        import math
        from constants import MAX_VALID_HALSTEAD_METRICS_PERCENTAGE_DIFFERENCE
        # get two metrics
        student_code_metrics=self._get_code_metrics(code=code)
        if (hasattr(self,'solution_metrics')):
            solution_code_metrics=self.solution_metrics
        else:
            solution_code_metrics=self._get_code_metrics(code=self.suggested_code)
            self.solution_metrics=solution_code_metrics
        # compare difference
        avg_diff=0.0 # not in percentage
        number_of_metrics=len(student_code_metrics)
        for i in range(number_of_metrics):
            if (student_code_metrics[i]!=0 or solution_code_metrics[i]!=0):
                avg_diff +=math.fabs(student_code_metrics[i]-solution_code_metrics[i])/(max(solution_code_metrics[i],student_code_metrics[i])*number_of_metrics)
        # generate report
        report=self._get_halstead_metrics_text(metrics_list=student_code_metrics)+"\n"
        report +="Metrics value difference from the solution: " + str(avg_diff * 100) + " %"

        return {'report':report,'is_strange':True}  if (avg_diff*100 > MAX_VALID_HALSTEAD_METRICS_PERCENTAGE_DIFFERENCE) else {'report':report,'is_strange':False}


    def _get_halstead_metrics_text(self,metrics_list):
        report=""
        report+="Number of operands: "+str(metrics_list[0]) + "\n"
        report+="Number of unique operands: "+str(metrics_list[1]) + "\n"
        report+="Number of operators: "+str(metrics_list[2]) + "\n"
        report+="Number of unique operators: "+str(metrics_list[3])
        return report