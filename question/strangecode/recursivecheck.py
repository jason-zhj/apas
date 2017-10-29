import re

class RecursiveCodeChecker(object):
    MAIN_FUNCTION_NOT_FOUND="Main function not found"
    RECURSIVE_FUNCTION_NOT_IN_MAIN="The specified recursive function call is not found in main function"
    RECURSIVE_DECLARATION_NOT_FOUND="The declaration of the specified recursive function call is not found"
    RECURSIVE_FUNCTION_CORRECT="The specified recursive function is correctly implemented in the recursive way"
    RECURSIVE_FUNCTION_NOT_RECURSIVE="The specified recursive function is NOT correctly implemented in a recursive way"

    def check_recursive(self,code,function_name,num_of_params=None):
        """
        :param code: clean code to check,'clean' means all comments and string literals are removed
        :param function_name: specified recursive function name
        :param num_of_params: number of parameters in the function prototype, if left None, then system will not check it
        :return: (is_recursive:bool,message:str)
        """
        main_found,main_start,main_end=self._locate_function(code=code,function_name="main",num_of_params=None)
        if (not main_found):
            return {False,self.MAIN_FUNCTION_NOT_FOUND}
        if (not self._has_function_call(code=code[main_start:main_end],function_name=function_name,num_of_params=num_of_params)):
            return {False,self.RECURSIVE_FUNCTION_NOT_IN_MAIN}
        recursive_func_found,func_start,func_end=self._locate_function(code=code,function_name=function_name,num_of_params=num_of_params)
        if (not recursive_func_found):
            return {False,self.RECURSIVE_DECLARATION_NOT_FOUND}
        if (self._has_function_call(code=code[func_start:func_end],function_name=function_name,num_of_params=num_of_params)):
            return {True,self.RECURSIVE_FUNCTION_CORRECT}
        else:
            return {False,self.RECURSIVE_FUNCTION_NOT_RECURSIVE}

    def _locate_function(self,code,function_name,num_of_params):
        """
        :return: (function_found:boolean,start_index:int,end_index:int), start_index is the index of the opening curly brace
        """
        # find the function header
        pattern_str=r'\s+' + function_name + r'\s*' + r'\('
        if (num_of_params):
            param_pattern_list=[r'[^,)(]+' for i in range(num_of_params)]
            pattern_str += ','.join(param_pattern_list)
        else:
            pattern_str += r'[^)(]*'
        pattern_str += r'\s*' + r'\)' + r'\s*\{'
        pattern=re.compile(pattern_str)
        match=pattern.search(code)
        if (not match):
            return False,-1,-1
        # find the function body
        i=body_start=match.end()
        brace_counter=0
        while(brace_counter!=-1 and i<len(code)):
            if (code[i]=="{"):
                brace_counter +=1
            if (code[i]=="}"):
                brace_counter -=1
            i +=1
        if (brace_counter!=-1):
            return False,-1,-1
        else:
            return True,body_start,i-2


    def _has_function_call(self,code,function_name,num_of_params):
        """
        :return: (function_call_found:boolean)
        """
        pattern_str=r'[^a-zA-Z0-9_]' + function_name + r'\s*' + r'\('
        if (num_of_params):
            param_pattern_list=[r'[^,)(]+' for i in range(num_of_params)]
            pattern_str += ','.join(param_pattern_list)
        else:
            pattern_str += r'[^)(]*'
        pattern_str += r'\s*' + r'\)'
        pattern=re.compile(pattern_str)
        match=pattern.search(code)
        return True if match else False