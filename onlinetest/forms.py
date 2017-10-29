from django import forms
from .models import OnlineTest



class OnlineTestForm(forms.ModelForm):
    class Meta:
        model=OnlineTest
        exclude=('id','slug')
        widgets = {
            'start_test_time': forms.TextInput(attrs={'role':'datatime_trigger'}),
            'end_test_time': forms.TextInput(attrs={'role':'datatime_trigger'}),
        }
    #
    # def clean(self):
    #     cleaned_data = super(OnlineTestForm, self).clean()
    #     title=cleaned_data.get('title')
    #     if (len(OnlineTest.objects.filter(title=title))>0):
    #         raise forms.ValidationError("The title already exists!")