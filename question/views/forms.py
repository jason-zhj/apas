from django import forms
from question.models import Question,QuestionTopic,TestCaseSet,QuestionPool,TestCase,QuestionRequirement

def get_evenly_assigned_allocation(expected_outputs):
    sum=100
    allocation=[]
    mark_per_output=int(100.0/len(expected_outputs.split("\n")))
    for i in range (len(expected_outputs.split("\n"))-1):
        allocation.append(str(mark_per_output))
        sum -=mark_per_output
    allocation.append(str(sum))
    return "\n".join(allocation)

def get_normalized_allocation(mark_allocation):
    allocation_list=mark_allocation.split("\n")
    allocation_list=[a.strip() for a in allocation_list]
    current_sum=0
    for i in range(len(allocation_list)):
        if (not allocation_list[i].isdigit()):
            raise forms.ValidationError("Mark allocation must be integer numbers!")
        current_sum +=int(allocation_list[i])
    if (current_sum!=100):
        multiply_factor=100.0/current_sum
        normalized_sum=0
        for i in range(len(allocation_list)-1):
            normalized_val=int(int(allocation_list[i])*multiply_factor)
            allocation_list[i]=str(normalized_val)
            normalized_sum+=normalized_val
        allocation_list[len(allocation_list)-1]=str(100-normalized_sum)
    return "\n".join(allocation_list)

class QuestionEditForm(forms.ModelForm):
    NONE='none'
    ITERATIVE=QuestionRequirement.ITERATIVE
    RECURSIVE=QuestionRequirement.RECURSIVE
    function_requirement_choice=(
        (NONE,NONE),
        (RECURSIVE,RECURSIVE),
        (ITERATIVE,ITERATIVE),
    )
    required_function_type=forms.ChoiceField(choices=function_requirement_choice,required=False)
    required_function_name=forms.CharField(max_length=250,required=False)
    number_of_parameters=forms.IntegerField(required=False,help_text="Leave this blank if it's unrestricted")

    class Meta:
        model=Question
        exclude=('id','slug')

    def __init__(self,*args,**kwargs):
        question=kwargs.get('instance')
        if (question and question.get_requirement()):
            requirement=question.get_requirement()
            initial = kwargs.get('initial', {})
            initial['required_function_type'] = requirement.required_function_type
            initial['required_function_name'] = requirement.required_function_name
            initial['number_of_parameters'] = requirement.number_of_parameters
            kwargs['initial'] = initial
        super(QuestionEditForm, self).__init__(*args, **kwargs)


    def clean(self):
        cleaned_data=super(QuestionEditForm, self).clean()
        sf_requirement=cleaned_data.get("required_function_type")
        if (sf_requirement!=self.NONE):
            function_name=cleaned_data.get("required_function_name")
            if (not function_name):
                raise forms.ValidationError("Required function name needs to be provided!")

    def save(self, commit=True):
        question=super(QuestionEditForm,self).save(commit=commit)
        func_requirement=self.cleaned_data['required_function_type']
        if (question.get_requirement()):
            # update question requirement
            requirement=question.get_requirement()
            if (func_requirement==self.NONE):
                requirement.delete()
            else:
                requirement.__dict__.update(self.cleaned_data)
                requirement.save()
        else:
            # save question requirement
            if (func_requirement!=self.NONE):
                required_function_name=self.cleaned_data['required_function_name']
                number_of_parameters=self.cleaned_data['number_of_parameters']
                q_requirement=QuestionRequirement.objects.create(
                    question=question,
                    required_function_type=func_requirement,
                    required_function_name=required_function_name,
                    number_of_parameters=number_of_parameters
                )
                q_requirement.save()
        return question

class QuestionTopicForm(forms.ModelForm):
    class Meta:
        model=QuestionTopic
        exclude=('id',)

class TestCaseSetForm(forms.ModelForm):
    class Meta:
        model=TestCaseSet
        exclude=('question',)

class TestCaseSetSimpleForm(forms.ModelForm):
    class Meta:
        model=TestCaseSet
        exclude=('question','grading_method',)


class TestCaseForm(forms.ModelForm):
    class Meta:
        model=TestCase
        exclude=('testcase_set',)
        labels = {
            'output_mark_allocation': 'Output Mark Allocation (assumed to be even allocation if left blank)',
        }

    def clean(self):
        cleaned_data=super(TestCaseForm, self).clean()
        mark_allocation=cleaned_data.get("output_mark_allocation")
        expected_outputs=cleaned_data.get("expected_outputs")
        len_mark_allocation=len(mark_allocation.split("\n"))
        len_expected_outputs=len(expected_outputs.split("\n"))
        if (len(mark_allocation)==0):
            mark_allocation=get_evenly_assigned_allocation(expected_outputs)
        elif (len_mark_allocation!=len_expected_outputs):
            raise forms.ValidationError("There are " + str(len_mark_allocation) + " lines of output, but there are " + str(len_expected_outputs)  + " mark allocations")
        else:
            mark_allocation=get_normalized_allocation(mark_allocation)

        cleaned_data['output_mark_allocation']=mark_allocation


class QuestionPoolForm(forms.ModelForm):
    class Meta:
        model=QuestionPool
        exclude=('slug',)


class ChangeScoreForm(forms.Form):
    new_score=forms.CharField(label="Change Score to:")
    comment=forms.CharField(widget=forms.Textarea,label="Comment:")

    def clean(self):
        """
        Validate the score to change to
        """
        cleaned_data = super(ChangeScoreForm, self).clean()
        new_score=cleaned_data.get('new_score')
        try:
            s=int(new_score)
        except:
            raise forms.ValidationError("Score must be an integer!")

        if (s<0 or s>100):
            raise forms.ValidationError("Score should be in the range of 0 to 100!")