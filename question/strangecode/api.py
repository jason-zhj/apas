from question.tokenizer import remove_comment,strip_string_literals

from recursivecheck import RecursiveCodeChecker
from checkers import *

__all__=('check_recursive','get_strange_code_checker',)

def check_recursive(code,required_language,function_name,num_of_params=None):
    checker=RecursiveCodeChecker()
    cleaned_code=strip_string_literals(
        code=remove_comment(code=code,required_language=required_language)
    )
    return checker.check_recursive(code=cleaned_code,function_name=function_name,num_of_params=num_of_params)


checker_to_use=HalsteadStrangeCodeChecker

def get_strange_code_checker(suggested_code,language,code_template=""):
    return checker_to_use(suggested_code=suggested_code,language=language,code_template=code_template)