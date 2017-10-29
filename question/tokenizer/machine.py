from state import *
from question.constants import JAVA_LANGUAGE_NAME,C_LANGUAGE_NAME

"""
This machine assumes the code doesn't contain syntax error (e.g. no unclosed quotes)
"""


class CleanCodeUtils(object):
    single_line_comment_prefix={
        C_LANGUAGE_NAME:"//",
        JAVA_LANGUAGE_NAME:"//"
    }
    multi_line_comment_prefix={
        C_LANGUAGE_NAME:"/*",
        JAVA_LANGUAGE_NAME:"*/"
    }
    multi_line_comment_post_fix={
        C_LANGUAGE_NAME:"*/",
        JAVA_LANGUAGE_NAME:"*/"
    }

    def remove_comment(self,code,language):
        new_code_list=[]
        NORMAL_STATE=0
        SINGLE_COMMENT_STATE=1
        MULTI_COMMENT_STATE=2
        state=NORMAL_STATE
        i=0

        single_line_prefix=self.single_line_comment_prefix[language]
        multi_line_prefix=self.multi_line_comment_prefix[language]
        multi_line_postfix=self.multi_line_comment_post_fix[language]

        while(i<len(code)):
            if (state==NORMAL_STATE):
                if (code.find(single_line_prefix,i)==i):
                    state=SINGLE_COMMENT_STATE
                    i+=2
                elif(code.find(multi_line_prefix,i)==i):
                    state=MULTI_COMMENT_STATE
                    i+=2
                else:
                    new_code_list.append(code[i])
                    i+=1
            elif(state==SINGLE_COMMENT_STATE):
                if (code[i]=='\n'):
                    state=NORMAL_STATE
                i+=1
            else:
                # multi comment state
                if (code.find(multi_line_postfix,i)==i):
                    state=NORMAL_STATE
                    i+=2
                else:
                    i+=1

        return ''.join(new_code_list)

    def strip_code_template(self,original_code,template_to_remove):
        # remove the string_to_remove from original string
        lines_to_remove=template_to_remove.splitlines()
        result_string=original_code
        for line in lines_to_remove:
            pos=result_string.find(line)
            if (pos!=-1):
                result_string=result_string[:pos] + result_string[pos+len(line):]
        return result_string


class BaseTokenizerMachine(object):
    """
    Abstract class for creating Tokenizer Machine
    """
    __metaclass__=ABCMeta

    @abstractmethod
    def get_tokenization_result(self,code,language,code_template=""):
        """
        :param code:
        :return: a dict {'values','tokens'}, types depend on implementation
        """
        pass


class HalsteadTokenizerMachine(CleanCodeUtils,BaseTokenizerMachine):

    keywords={
        C_LANGUAGE_NAME:['return','int','double','float','break','continue','include','define'],
        JAVA_LANGUAGE_NAME:['return','int','double','float','break','continue','import','class','public','protected','private']
    }

    def __init__(self):
        self.quote_state=QuoteState(self)
        self.alphanumeric_state=AlphaNumbericState(self)
        self.whitespace_state=WhiteSpaceState(self)
        self.operand_state=OperandState(self)
        self.current_state=self.whitespace_state
        self.operand_list=[]
        self.operator_list=[]
        self.temp_str=""

    def get_tokenization_result(self,code,language,code_template=""):
        """
        :param code:
        :return: number of operand, number of unique operand, number of operator, number of unique operator
        """
        self.clean_up()
        self.keyword_list=self.keywords[language]
        code_without_comment=self.remove_comment(code=code,language=language)
        cleaned_code=code_without_comment
        #cleaned_code=self.strip_code_template(original_code=code_without_comment,template_to_remove=code_template)
        for i in range(len(cleaned_code)):
            self.current_state.process_input(cleaned_code[i])
        # get number of unique operands and operators
        unique_operand_list=list(set(self.operand_list))
        unique_operator_list=list(set(self.operator_list))
        tokenization_result_values=[len(self.operand_list),
                len(unique_operand_list),
                len(self.operator_list),
                len(unique_operator_list)]

        return {'values':tokenization_result_values,'tokens':[]}

    def clean_up(self):
        self.current_state=self.whitespace_state
        self.operand_list=[]
        self.operator_list=[]
        self.temp_str=""

    def add_operand(self,operand):
        self.operand_list.append(operand)

    def add_operator(self,operator):
        self.operator_list.append(operator)

    def set_current_state(self,state):
        self.current_state=state

    def set_temp(self,temp):
        self.temp_str = temp

    def get_temp(self):
        return self.temp_str

    def get_operand_character_list(self):
        special_char_list=['-','/','*','+','=','(',')','[',']','<','>']
        return special_char_list

    def get_keyword_list(self):
        return self.keyword_list



