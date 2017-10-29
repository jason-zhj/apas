from abc import ABCMeta,abstractmethod
import subprocess,threading
import os

from constants import EXECUTER_PATH,JAVA_LANGUAGE_NAME

class BaseProgramTester(object):
    __metaclass__=ABCMeta

    def __init__(self,program_path,output_analyzer):
        """
        :param program_path: complete path of the program file
        :param output_analyzer: an instance of OutputAnalyzer
        """
        self.program_path=program_path
        self.output_analyzer=output_analyzer

    def run_testcase(self,testcase):
        """
        :param testcase: question.models.TestCase
        :return: {pass:boolean,score:int,result:str}
        """
        from constants import RUN_PROGRAM_TIME_LIMIT
        command=Command(self.get_execution_command())
        return_code=command.run(stdin=testcase.test_inputs+"\n",timeout=RUN_PROGRAM_TIME_LIMIT) # the "\n" is to make sure the input is entered

        return self.output_analyzer.analyze_output(correct_output=testcase.expected_outputs_list,program_output=command.output,output_mark_allocation=testcase.output_mark_allocation_list)

    @abstractmethod
    def get_execution_command(self):
        """
        :return a list of strings as a command
        """
        return []


class CProgramTester(BaseProgramTester):
    def get_execution_command(self):
        """
        :return a list of strings as a command
        """
        return [self.program_path]

class JavaProgramTester(BaseProgramTester):
    def get_execution_command(self):
        """
        :return a list of strings as a command
        """
        file_name=os.path.basename(self.program_path)
        working_path=os.path.dirname(self.program_path)
        # strip off the ".class" extension
        pos=file_name.find(".class")
        if (pos!=-1):
            file_name=file_name[:pos]
        return [EXECUTER_PATH[JAVA_LANGUAGE_NAME],'-cp',working_path,file_name]

# simple object modified from online to check output and terminate when timed out
class Command(object):
    #TODO: maybe add in cwd parameter
    """
    Attribute: output is the output from the process
    """
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None
        self.output = ""

    def run(self, stdin, timeout):
        """
        :param stdin: input to the process
        :param timeout: the time beyond which the process will be terminated
        :return:  return code of the process
        """
        self.output = ""  # clear output first

        def target():
            self.process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            self.output,err = self.process.communicate(input=stdin)

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            self.process.terminate()
            thread.join()

        return self.process.returncode