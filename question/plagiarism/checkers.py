from abc import ABCMeta,abstractmethod
from question import tokenizer


class PlagiarismChecker(object):
    """
    Abstract class for creating plagiarism checker
    """
    __metaclass__=ABCMeta

    def __init__(self,code1,code2,language):
        self.code1=code1
        self.code2=code2
        self.language=language

    @abstractmethod
    def get_report(self):
        """
        :return: a plagiarism checking report in string
        """
        return "report"

    @abstractmethod
    def isPlagiarised(self):
        return False

class HalsteadChecker(PlagiarismChecker):
    """
    Plagiarism checker using Halstead Complexity Measures
    """
    def isPlagiarised(self):
        from constants import SIMILARITY_THRESHOLD
        diff_list=self.get_diff_percentage()
        for item in diff_list:
            if item<SIMILARITY_THRESHOLD:
                return True
        return False

    def get_diff_percentage(self):
        """
        :return: a list: difference percentage for the 4 measures
        """
        if hasattr(self,'diff_list'):
            return self.diff_list

        result1=tokenizer.get_tokenization_result(code=self.code1,required_language=self.language)['values']
        result2=tokenizer.get_tokenization_result(code=self.code2,required_language=self.language)['values']
        diff_list=[abs(result1[i]-result2[i])*100.0/max(result1[i],result2[i]) if max(result1[i],result2[i])!=0 else 0
                   for i in range(len(result1))]
        self.diff_list=diff_list
        return diff_list

    def get_report(self):
        diff_list=self.get_diff_percentage()
        name_list=["Number of operands","Number of unique operands","Number of operators","Number of unique operators"]
        report_items=["Difference in %s : "%name_list[i] + "%4d"%(diff_list[i]) + "%" for i in range(len(diff_list))]
        report="\n".join(report_items)
        return report + "\nSuspect Plagiarised" if self.isPlagiarised() else report +"\nNot likely to be plagiarised"
