from django import forms
from .models import Assignment

# class BootstrapCheckbox(forms.CheckboxInput):
#     def render(self, name, value, attrs=None):
#         original_html=super(BootstrapCheckbox, self).render(name, value, attrs)
#         modified_html="""
#                 <div class="bootstrap-switch bootstrap-switch-wrapper bootstrap-switch-id-switch-state bootstrap-switch-animate bootstrap-switch-on" style="width: 108px;"><div class="bootstrap-switch-container" style="width: 159px; margin-left: 0px;"><span class="bootstrap-switch-handle-on bootstrap-switch-primary" style="width: 53px;">ON</span><span class="bootstrap-switch-label" style="width: 53px;">&nbsp;</span><span class="bootstrap-switch-handle-off bootstrap-switch-default" style="width: 53px;">OFF</span>{}</div></div>
#                         """.format(original_html)
#         return modified_html

class AssignmentEditForm(forms.ModelForm):
    class Meta:
        model=Assignment
        exclude=('questions','mark_allocation_string','slug')
        labels = {
            'groups': 'Groups to receive this assignment',
        }
        widgets = {
            'start_submission_time': forms.TextInput(attrs={'role':'datatime_trigger'}),
            'end_submission_time': forms.TextInput(attrs={'role':'datatime_trigger'}),
        }


