from django import forms
from apassite.settings import BASE_DIR
import  os,importlib

ENV_FILE_NAME=".env"

class ConfigurationForm(forms.Form):
    max_acceptable_diff_percentage=forms.IntegerField(min_value=0,max_value=100,
                                                      label="Max metrics difference percentage to not be recognized as strange code",
                                                      help_text="This is used for finding strange code. For example, if this is set to 20, then a student's code will be recognized as strange code if his Halstead metrics is more than 20% different from that of the suggested solution")
    min_score_to_check_strange_code=forms.IntegerField(min_value=0,max_value=100,
                                                       label="Min score for a submission to be checked for strange code",
                                                       help_text="This is used for finding strange code. For example, if this is set to 50, then the system will only check the submissions that get a score above or equal to 50")
    run_program_time_limit=forms.IntegerField(min_value=1,
                                              label="Max time (in seconds) for a student program to run",
                                              help_text="This is used for program testing. For example, if this is set to 1, then when the testing a student's program, the system will terminate it if it doesn't finish within 1 second")
    similarity_threshold=forms.IntegerField(min_value=1,max_value=99,
                                            label="Minimum metrics similarity percentage to be recognized as plagiarised",
                                            help_text="This is used for plagiarism checking. For example, if this is set to 20, then two student's code will be reported as plagiarised if the Halstead metrics of their code has a difference of less than 20%")

    def __init__(self,*args,**kwargs):
        super(ConfigurationForm,self).__init__(*args,**kwargs)
        for key in self.fields.keys():
            self.fields[key].initial=get_question_setting(key)


    def save_configuration(self):
        # read env file
        env_path=os.path.join(BASE_DIR,ENV_FILE_NAME)
        f=open(env_path)
        lines=[a for a in f.readlines() if a[0]!="#" and a.find("=")!=-1]
        comment_lines=[a for a in f.readlines() if a[0]=="#"]
        pairs={a.split("=")[0]:a.split("=")[1] for a in lines}
        # change settings
        for key in self.cleaned_data.keys():
            save_key=key.upper()
            value=self.cleaned_data[key]
            change_setting(save_key,value)
            pairs[save_key]=str(value) if type(value)==type(1) else "'" + str(value) +"'"
        # save back to env file
        f=open(env_path,mode="w")
        f.writelines([key+"="+value+"\n" for key,value in pairs.iteritems()])
        f.writelines(a+"\n" for a in comment_lines)
        f.close()


def get_question_setting(key):
    module = importlib.import_module("question.settings")
    upper_key=key.upper()
    if (hasattr(module,upper_key)):
        return getattr(module,upper_key)

def change_setting(key,value):
    module=importlib.import_module("question.settings")
    if (hasattr(module,key)):
        setattr(module,key,value)