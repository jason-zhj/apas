from checkers import *

__all__=('create_plagiarism_checker')

checker_class_to_use=HalsteadChecker

def create_plagiarism_checker(code1,code2,language):
    """
    :param code1:
    :param code2:
    :param language:
    :return: a plagiarism checker according to the DEFAULT_PLAGIARISM_CHECKER
    """
    return checker_class_to_use(code1,code2,language)