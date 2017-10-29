from machine import *
from extractstring import StringConstantExtractor

__all__=('get_tokenization_result','remove_comment',)

tokenizer_to_use=HalsteadTokenizerMachine

def get_tokenization_result(code,required_language,code_template=""):
    machine=HalsteadTokenizerMachine()
    return machine.get_tokenization_result(code=code,language=required_language,code_template=code_template)

def remove_comment(code,required_language):
    remove_comment_util=CleanCodeUtils()
    return remove_comment_util.remove_comment(code=code,language=required_language)

def strip_string_literals(code):
    cleaned_code=code
    extractor=StringConstantExtractor(code=code)
    literal_list=extractor.get_string_constant_list()
    for literal in literal_list:
        cleaned_code=cleaned_code.replace(literal,'')
    return cleaned_code
