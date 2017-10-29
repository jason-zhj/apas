import os
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from question.constants import C_LANGUAGE_NAME,JAVA_LANGUAGE_NAME
from apassite.settings import INSTRUCTION_FILE_RELATIVE_PATH
from question.outputconvert import output_from_list_to_str,output_from_str_to_list
from question.codestore import read_code_file

class QuestionTopic(models.Model):
    SUBJECT_CHOICES=(('Data Structure','Data Structure'),
                     ('Intro to C Programming','Intro to C Programming'),
                     ('Intro to Python Programming','Intro to Python Programming'),
                     ('Intro to Java Programming','Intro to Java Programming'),)
    title=models.CharField(max_length=200,unique=True)
    description=models.TextField()
    subject=models.CharField(max_length=200,choices=SUBJECT_CHOICES)

    def __unicode__(self):
        return self.title


class Question(models.Model):
    ACE_EDITOR_LANGUAGE_NAME={C_LANGUAGE_NAME:"c_cpp",JAVA_LANGUAGE_NAME:"java"}

    QUESTION_LANGUAGE_CHOICES=(
        (JAVA_LANGUAGE_NAME,JAVA_LANGUAGE_NAME),
        (C_LANGUAGE_NAME,C_LANGUAGE_NAME),
    )

    DIFFICULTY_CHOICES=(
        (0,'very easy'),
        (1,'easy'),
        (2,'normal'),
        (3,'difficult'),
        (4,'very difficult'),
    )

    IGNORE_STRING_CONSTANTS_CHOICES=(
        (0,'No'),
        (1,'Yes')
    )

    OUTPUT_CHECKING_METHODS=[
    (0,'Partial Output string matching'),
    (1,'Exact Output string matching')
    ]
    title=models.CharField(max_length=200,unique=True)
    content=models.TextField()
    difficulty=models.IntegerField(choices=DIFFICULTY_CHOICES,default=2)
    required_language=models.CharField(max_length=50,choices=QUESTION_LANGUAGE_CHOICES,default=C_LANGUAGE_NAME)
    question_topic=models.ForeignKey(QuestionTopic,null=True,blank=True,on_delete=models.SET_NULL)
    instruction_file=models.FileField(upload_to=INSTRUCTION_FILE_RELATIVE_PATH["question"],null=True,blank=True)
    output_checking_method=models.IntegerField(default=0,choices=OUTPUT_CHECKING_METHODS)
    ignore_string_constants_in_output=models.IntegerField(default=0,choices=IGNORE_STRING_CONSTANTS_CHOICES)
    code_template=models.TextField(blank=True)
    suggested_solution=models.TextField(blank=True)
    slug=models.SlugField(default="",unique=True)

    def __unicode__(self):
        return self.title

#-----------attribute method------------------
    def get_output_checking_method(self):
        return self.OUTPUT_CHECKING_METHODS[self.output_checking_method][1]

    def get_requirement(self):
        try:
            return self.questionrequirement
        except:
            return None

    def is_ignore_string_constants_in_output(self):
        return self.ignore_string_constants_in_output==1

    def is_use_partial_output_matching(self):
        return self.output_checking_method==0

    def get_test_case_data(self):
        return self.testcaseset_set.all()

    def get_configure_tests(self):
        test_edit_url=reverse("test_case_set_list",args=[self.slug])
        html="""<a href="{}">
                  Sets <span class="badge">{}</span>""".format(test_edit_url,self.number_of_test_case_sets())
        return html

    def is_test_case_set_weightage_valid(self):
        testcase_sets=self.testcaseset_set.all()
        sum=0
        for testcase_set in testcase_sets:
            sum +=testcase_set.weightage
        if (abs(sum-100)<0.0001):
            return True
        else:
            return False

    def get_redirect_url(self):
        return reverse("test_case_set_list",args=[self.slug])

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Question,self).save(*args, **kwargs)

    def number_of_test_case_sets(self):
        return len(self.testcaseset_set.all())

    def get_instruction_file_name(self):
        return os.path.basename(self.instruction_file.url) if (self.instruction_file) else None

    def get_difficulty(self):
        """
        :return: the string repr of difficulty
        """
        return self.DIFFICULTY_CHOICES[self.difficulty][1]

    def has_been_submitted_by(self,user):
        submissions=QuestionSubmission.objects.filter(question=self,submitted_by=user)
        return len(submissions)>0

    def get_instruction_file_link(self):
        if (not self.instruction_file):
            return "NIL"
        file_name=os.path.basename(self.instruction_file.url)
        url=reverse("question_file_download",args=[file_name])
        html="""<a href="{}" target="_blank">
                   <span class="badge">{}</span></a>""".format(url,"Download")
        return html

    def get_summary_brief(self):
        from appglobal import get_summary
        return get_summary(source=self,fields=['title','content'])

#-------------for html web code editor--------------------------
    def get_editor_language_name(self):
        # for ace web code editor
        return self.ACE_EDITOR_LANGUAGE_NAME[self.required_language]


class QuestionPool(models.Model):
    # for picking random questions in online test
    title=models.CharField(max_length=200,unique=True)
    description=models.TextField(blank=True)
    questions=models.ManyToManyField(Question)
    slug=models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(QuestionPool,self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title

    def max_number_to_select(self):
        return len(self.questions.all())

#-------------attribute methods-------------
    def get_random_questions(self,number_of_questions):
        all_questions=self.questions.all()
        import random
        return random.sample(all_questions,number_of_questions)

class QuestionSubmission(models.Model):
    src_file_path=models.TextField() # should only store the relative path
    exe_file_path=models.TextField(null=True) # this field will be used if testing is not run automatically
    is_grading_finished=models.BooleanField(default=False) # indicate whether test has been run
    score=models.IntegerField(default=0)
    question=models.ForeignKey(Question)
    submission_time=models.DateTimeField(auto_created=True)
    submitted_by=models.ForeignKey(User)
    compilation_okay=models.BooleanField(default=True) # whether the source code can be compiled
    requirement_met=models.BooleanField(default=True) # refer to QuestionRequirement
    requirement_violation_msg=models.TextField(null=True)
    requirement_checked=models.BooleanField(default=False)

    def __unicode__(self):
        return self.question.title

    def clean_up(self,keep_files=False):
        if (not keep_files):
            self.delete_submitted_files()

    def delete_submitted_files(self):
        from codestore import remove_code_file
        remove_code_file(self.src_file_path)
        if (self.exe_file_path):
            remove_code_file(self.exe_file_path)

    def remark_with_record(self,new_score,comment):
        remarking=Remarking.quick_save(old_score=self.score,new_score=new_score,modifier=None,comment=comment,question_submission=self)
        self.score=new_score
        self.save()

#-------------------attribute methods---------------------------
    def get_score(self):
        return self.score if (self.is_grading_finished) else "Grading not finished"

    def get_previous_score(self):
        remarkings=self.remarking_set.all()
        if (not remarkings):
            return "No previous score"
        else:
            last_remarking=remarkings.order_by("-time_stamp")[0]
            return last_remarking.initial_score

    def get_requirement_checking_result(self):
        if (self.requirement_checked):
            return "Okay" if self.requirement_met else self.requirement_violation_msg
        else:
            return "Not checked yet"

    def get_source_code(self):
        return read_code_file(relative_path=self.src_file_path)

    def get_compilation_status(self):
        return "Compilable" if self.compilation_okay else "Not Compilable, Test cases cannot be run"

    def get_question_title(self):
        return self.question.title

    def get_submitted_by(self):
        return self.submitted_by.username

    def get_detail_link(self):
        url=reverse("question_submission_view_student",args=[self.id])
        html="""<a href="{}"><i class="fa fa-eye"></i></a>""".format(url)
        return html

#-----------------methods for making reports-----------------------------
    def get_code_analysis_report(self):
        # probably by comparing the suggested code with the submitted code
        return "Code analysis report(to be built)"

    def get_analysis_report(self):
        test_case_set_results=self.testcasesetresult_set.all()
        return render_to_string("app-question/class-questionsubmission/report_template.html",{
            'question_submission':self,
            'test_case_set_results':test_case_set_results
        })


class TestCaseSet(models.Model):
    PICK_MINIMUM_MARK=0
    SCORE_FOR_EACH_PASS_METHOD=1
    GRADING_METHODS=[
        (PICK_MINIMUM_MARK,'Choose the lowest scored'),
        (SCORE_FOR_EACH_PASS_METHOD,'Give mark for every test case passed')
    ]
    title=models.CharField(max_length=200)
    description=models.TextField(null=True,blank=True)
    question=models.ForeignKey(Question)
    weightage=models.DecimalField(decimal_places=2,max_digits=5)
    grading_method=models.IntegerField(choices=GRADING_METHODS,default=PICK_MINIMUM_MARK)

    def __unicode__(self):
        return self.title

#--------------------------attribute methods------------------------------------
    def get_grading_method(self):
        return self.GRADING_METHODS[0][1] if (self.grading_method==self.PICK_MINIMUM_MARK) else self.GRADING_METHODS[1][1]

    def is_pick_minimum_mark(self):
        return self.GRADING_METHODS==self.PICK_MINIMUM_MARK

    def get_weighted_score(self,score):
        """
        :param score: int
        :return: score in double
        """
        return 1.0 * float(self.weightage) * score / 100.0

    def clean_up(self):
        pass


class TestCaseSetResult(models.Model):
    test_case_set=models.ForeignKey(TestCaseSet)
    question_submission=models.ForeignKey(QuestionSubmission)
    score=models.IntegerField(default=0)

    def get_report(self):
        test_case_results=self.testcaseresult_set.all()
        return render_to_string("app-question/class-testcaseset/report_template.html",{'testcase_set_result':self,'test_case_results':test_case_results})


class TestCase(models.Model):
    test_inputs=models.TextField()
    testcase_set=models.ForeignKey(TestCaseSet)
    # link to a set of testcase result

#------------------attribute methods----------------------------------
    def _get_expected_outputs_str(self):
        outputs=[a.expected_outputs for a in self.expectedoutput_set.all()]
        return output_from_list_to_str(outputs)

    expected_outputs_str=property(_get_expected_outputs_str) # expected outputs in string

    def _get_output_mark_allocation_str(self):
        allocations=[str(a.weightage) for a in self.expectedoutput_set.all()]
        return "\n".join(allocations)

    output_mark_allocation_str=property(_get_output_mark_allocation_str) # output mark allocation in string

    def _get_expected_outputs_list(self):
        return [a.expected_outputs for a in self.expectedoutput_set.all()]

    expected_outputs_list=property(_get_expected_outputs_list)

    def _get_output_mark_allocation_list(self):
        return [a.weightage for a in self.expectedoutput_set.all()]

    output_mark_allocation_list=property(_get_output_mark_allocation_list)
#----------------------------data manipulation methods for view to use--------------
    def clean_up(self):
        #TODO: clean up relevant info before deleting
        pass

    @staticmethod
    def quick_save(test_inputs,expected_outputs,testcase_set,output_mark_allocation):
        # create test case
        test_case=TestCase.objects.create(test_inputs=test_inputs,testcase_set=testcase_set)
        test_case.save()
        # create expected outputs
        ExpectedOutput.quick_save_list(expected_outputs=expected_outputs,output_mark_allocation=output_mark_allocation,test_case=test_case)


class ExpectedOutput(models.Model):
    expected_outputs=models.TextField()
    test_case=models.ForeignKey(TestCase)
    weightage=models.IntegerField()
    sequence=models.IntegerField() # starting from 1, to keep the order the expected outputs

    class Meta:
        ordering = ['sequence']

    def __unicode__(self):
        return self.expected_outputs

    @staticmethod
    def quick_save_list(expected_outputs,output_mark_allocation,test_case):
        new_object_list=[]
        allocation_list=output_mark_allocation.splitlines()
        output_list=output_from_str_to_list(expected_outputs)
        if (len(output_list)!=len(allocation_list)):
            raise Exception("Number of allocations doesn't match with number of outputs")
        for i in range(len(output_list)):
            new_object=ExpectedOutput.quick_save(expected_outputs=output_list[i],
                                      weightage=int(allocation_list[i].strip()),
                                      test_case=test_case,
                                      output_seq=i+1)
            new_object_list.append(new_object)

        return new_object_list


    @staticmethod
    def quick_save(expected_outputs,weightage,output_seq,test_case):
        new_ex=ExpectedOutput.objects.create(test_case=test_case,weightage=weightage,expected_outputs=expected_outputs,sequence=output_seq)
        new_ex.save()
        return new_ex

class TestCaseResult(models.Model):
    is_pass=models.BooleanField(default=False)
    score=models.IntegerField(null=True,blank=True)
    result_brief=models.TextField(null=True,blank=True) # dummy field, can be removed
    result_detail=models.TextField()
    test_case=models.ForeignKey(TestCase)
    test_case_set_result=models.ForeignKey(TestCaseSetResult)

class Remarking(models.Model):
    # either of the following should not be null
    question_submission=models.ForeignKey(QuestionSubmission)
    initial_score=models.IntegerField()
    result_score=models.IntegerField()
    comment=models.TextField() # reason for remarking
    remarker=models.ForeignKey(User,null=True)
    time_stamp=models.DateTimeField(auto_created=True)

    @staticmethod
    def quick_save(old_score,new_score,modifier,comment,question_submission):
        """
        create a new Remarking record and save it
        :param old_score:
        :param new_score:
        :param modifier:
        :param comment:
        :param question_submission:
        :return: the Remarking object that's created
        """
        new_remarking=Remarking.objects.create(initial_score=old_score,
                                 result_score=new_score,
                                 comment=comment,
                                 remarker=modifier,
                                 question_submission=question_submission,
                                 time_stamp=datetime.now()
                                 )

        new_remarking.save()
        return new_remarking


class QuestionRequirement(models.Model):
    ITERATIVE='Iterative'
    RECURSIVE='Recursive'
    function_requirement_choice=(
        (RECURSIVE,RECURSIVE),
        (ITERATIVE,ITERATIVE),
    )
    question=models.OneToOneField(Question)
    required_function_type=models.CharField(choices=function_requirement_choice,max_length=250)
    required_function_name=models.CharField(max_length=250)
    number_of_parameters=models.IntegerField(blank=True,null=True)
