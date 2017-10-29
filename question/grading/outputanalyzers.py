__author__ = 'Administrator'
from abc import ABCMeta,abstractmethod


class OutputAnalyzer(object):
    __metaclass__=ABCMeta

    def __init__(self,output_ignore_list=None):
        self.output_ignore_list=output_ignore_list

    def analyze_output(self,correct_output,program_output,output_mark_allocation):
        """
        :param correct_output: a list of correct outputs
        :param program_output: string
        :param output_mark_allocation: a list of integers
        :return:{score:int,result:str}
        """
        overall_score=0
        overall_result=""
        start_match_pos=0 # position to start output matching
        # remove strings to ignore
        if (self.output_ignore_list):
            for output_item in self.output_ignore_list:
                program_output=program_output.replace(output_item,"")
                correct_output=[a.replace(output_item,"") for a in correct_output]
        # start output checking
        for i in range(len(correct_output)):
            expected_output=correct_output[i]
            success,new_match_pos,result=self.output_match(expected_output=expected_output,student_output=program_output,start_match_pos=start_match_pos)
            start_match_pos=new_match_pos
            overall_result += result
            if (success):
                overall_score +=output_mark_allocation[i]
                overall_result += "  ( " + str(output_mark_allocation[i]) + " marks scored )\n"
            else:
                overall_result += "  ( 0 mark scored )\n"

        return {"pass":overall_score==100,"score":overall_score,"result":overall_result}

    @abstractmethod
    def output_match(self,expected_output,student_output,start_match_pos):
        """
        :return success,new_match_pos,result
        """
        pass


class EqualityOutputAnalyzer(OutputAnalyzer):

    def output_match(self,expected_output,student_output,start_match_pos):
        expected_lines=expected_output.split("\n")
        actual_lines=student_output[start_match_pos:].split("\n")
        success=True
        new_match_pos=start_match_pos
        result=""
        i=0
        while (i<min(len(expected_lines),len(actual_lines))):
            new_match_pos += len(actual_lines[i]) + 1
            result+="Expected output : " + expected_lines[i] + " ; Actual output : " + actual_lines[i] +"\n"
            try:
                if (expected_lines[i].strip()==actual_lines[i].strip()):
                    result +="Output Correct" + "\n"
                else:
                    success=False
                    result +="Output Wrong" + "\n"
            except:
                success=False
                result +="Output Wrong" + "\n"
            i +=1

        for j in range(i,len(expected_lines)):
            success=False
            result += "Expected output : " + expected_lines[j] + " is missing\n"

        return success,new_match_pos,result[:-1]


class KeyMatchOutputAnalyzer(OutputAnalyzer):

    def output_match(self,expected_output,student_output,start_match_pos):
        expected_keys=[a.strip() for a in expected_output.split("\n")]
        actual_output=student_output[start_match_pos:]
        success=True
        result=""
        new_match_pos=start_match_pos
        for key in expected_keys:
            try:
                pos = actual_output.find(key)
                if pos == -1:
                    success=False
                    result += "Expected Output: %s is missing \n" % key
                else:
                    actual_output = actual_output[pos+len(key):]
                    new_match_pos += pos+len(key)
                    result += "Expected Output: %s is found \n" % key
            except:
                success=False
                result += "Expected Output: %s is missing \n" % key

        return success,new_match_pos,result[:-1]


