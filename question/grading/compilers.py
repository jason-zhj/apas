from abc import ABCMeta,abstractmethod
import subprocess
import os

from constants import COMPILER_PATH

def normalize_error_message(err,file_name):
    error_lines=err.strip("\n").split('\n')#strip off redundant newline character
    formatted_lines=[]
    for line in error_lines:
        line = unicode(line, 'ascii', 'ignore')
        pos=line.find(file_name)
        if (pos!=-1):
            formatted_lines.append(line[pos+len(file_name)+1:])
        else:
            formatted_lines.append(line)

    error_msg = "<br>".join(formatted_lines)
    return error_msg

class BaseCompiler(object):
    __metaclass__=ABCMeta

    def __init__(self,code_file_path):
        """
        :param code_filename: complete path of the file
        :return:
        """
        self.code_file_path=code_file_path

    def do_compilation(self):
        """
        :return: a dict {is_successful:boolean,error_message:String,executable_path:String or None}
        """
        file_name=os.path.basename(self.code_file_path)
        directory_name=os.path.dirname(self.code_file_path)
        # do compilation
        proc=subprocess.Popen(self._get_compilation_command(filename=file_name),stderr=subprocess.PIPE,stdout=subprocess.PIPE,stdin=subprocess.PIPE,cwd=directory_name)
        out,err=proc.communicate()
        # prepare return message
        is_compilation_successful=True
        err_message=""
        executable_path=None
        if (err):
            err_message=normalize_error_message(err=err,file_name=file_name)
            is_compilation_successful=False
        else:
            executable_path=self._get_executable_path()

        return {'is_successful':is_compilation_successful,'error_message':err_message,'executable_path':executable_path}

    @abstractmethod
    def _get_compilation_command(self,filename):
        """
        :param filename: the filename without directory
        :return:  a list of strings as commands for executing compiler
        """
        return []

    @abstractmethod
    def _get_executable_path(self):
        """
        :return: the complete path of the executable, if the compilation is successful
        """
        return ""

class CCompiler(BaseCompiler):
    def _get_compilation_command(self,filename):
        return [COMPILER_PATH['C'],"-w",filename]

    def _get_executable_path(self):
        directory_name=os.path.dirname(self.code_file_path)
        return os.path.join(directory_name,"a.exe")

class JavaCompiler(BaseCompiler):
    def _get_compilation_command(self,filename):
        return [COMPILER_PATH['Java'],filename]

    def _get_executable_path(self):
        path_without_ext,ext=os.path.splitext(self.code_file_path)
        # here assume the source file is correctly named
        return path_without_ext+".class"