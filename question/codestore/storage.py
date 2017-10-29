from question.constants import C_LANGUAGE_NAME,JAVA_LANGUAGE_NAME
from constants import *
import os
import re

class CodeStorer(object):
    def __init__(self,work_dir,is_abs=False):
        """
        :param work_dir: a string of a directory relative to CODE ROOT
        :param is_abs: indicate whether the work_dir is relative to CODE_PATH or not
        """
        self.work_dir=os.path.join(CODE_ROOT,work_dir) if not is_abs else work_dir

    def save_code(self,code,language,clean_directory=True,filename=""):
        """
        :param text: string of content
        :param file_name:
        :return: the file path of the file saved
        :exception if the file is java file, but the class name cannot be found, or any other error occurred in saving
        """
        #TODO: uuid is just temporary solution, should employ better ones
        import uuid
        work_dir=os.path.join(self.work_dir,str(uuid.uuid4()))
        # if (clean_directory):
        #     clean_dir(self.work_dir)
        # 1 check code type
        if (language==JAVA_LANGUAGE_NAME):
            # 1-1 get class name
            class_name=get_java_class_name(code=code)
            if (class_name):
                file_name=class_name + ".java"
            else:
                raise CodeStorerException("Java class name is not found")
        elif(language==C_LANGUAGE_NAME):
            file_name=filename or DEFAULT_C_FILE_NAME
        else:
            raise CodeStorerException("The code type is not supported")
        #2 save the main code file
        file_abs_path=os.path.join(work_dir,file_name)
        if (not os.path.exists(work_dir)):
            os.makedirs(work_dir)
        try:
            with open(file_abs_path,mode='w') as f:
                f.write(code)
            return file_abs_path
        except Exception as e:
            raise CodeStorerException("Error occurred in saving the source code file")

class CodeStorerException(Exception):
    pass

def clean_dir(path):
    """
    delete all files under path
    :param path:
    """
    import os
    if (not os.path.exists(path)):
        return
    filelist = [ f for f in os.listdir(path)]
    for f in filelist:
        try:
            os.remove(os.path.join(path,f))
        except:
            continue

def get_java_class_name(code):
    """
    :param code:
    :return: java class name in string
    """
    pattern=re.compile('\s+class\s+(.+){')
    if (pattern.search(code)):
        class_name=pattern.search(code).groups()[0]
        return class_name.strip()
    else:
        return None

def save_uploaded_files(save_path,support_files):
    """
    :param save_path:
    :param support_files:
    save support_files to save_path
    """
    file_name_list=[]
    if (not support_files):
        return
    for f in support_files:
        path=os.path.join(save_path,f.name)
        # write the file
        try:
            with open(path, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)
            # record the path
            file_name_list.append(path)
        except:
            raise CodeStorerException("Error in saving support code files")
    return file_name_list

def get_relative_work_dir(task_name,task_id,question_id,user_id):
    """
    Create a directory according to the given info

    :return: directory to work in (string)
    """
    folder_relative_path=os.path.join(task_name,str(task_id),"question",str(question_id),"submissions",str(user_id))
    work_dir=os.path.join(CODE_ROOT,folder_relative_path)
    if not os.path.exists(work_dir):
         os.makedirs(work_dir)
    return folder_relative_path

def remove_code_file(relative_path):
    file_path=os.path.join(CODE_ROOT,relative_path)
    if os.path.exists(file_path):
        os.remove(file_path)

def read_code_file(relative_path):
    file_path=os.path.join(CODE_ROOT,relative_path)
    return open(file_path,mode='r').read()

def get_temp_code_store_dir(user_id):
    return os.path.join(TEMP_CODE_ROOT,str(user_id))

def get_relative_code_path_from_abspath(abspath):
    return abspath[len(CODE_ROOT)+1:]

def get_abs_code_path_from_relativepath(relative_path):
    return os.path.join(CODE_ROOT,relative_path)