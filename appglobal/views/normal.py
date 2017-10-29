import os

from django.http import HttpResponseRedirect,Http404
from django.db import transaction
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render,get_object_or_404
from django.views.static import serve
from django.core.urlresolvers import reverse

from apassite.settings import INSTRUCTION_FILE_RELATIVE_PATH,MEDIA_ROOT
from account.helper import is_staff
from assignment.models import AssignmentSubmission
from onlinetest.models import OnlineTestSubmission
from appglobal.views.forms import ConfigurationForm


def index(request):
    if (request.user.is_authenticated()):
        return HttpResponseRedirect(reverse("home"))
    else:
        return HttpResponseRedirect(reverse("user_login"))

def home(request):
    if (is_staff(request.user)):
        new_assignment_submissions=[]
        new_test_submissions=[]
        try:
            new_assignment_submissions=[get_object_or_404(AssignmentSubmission,id=a) for a in request.session["new_assignment_submission_ids"]]
            new_test_submissions=[get_object_or_404(OnlineTestSubmission,id=a) for a in request.session["new_test_submission_ids"]]
        except:
            pass
        return render(request, 'appglobal/home.html',{'new_assignment_submissions':new_assignment_submissions,'new_test_submissions':new_test_submissions})
    else:
        return render(request, 'appglobal/home.html')

def about(request):
    return render(request, 'appglobal/about.html')



@transaction.atomic
def simple_clear_submissions(request,model_class):
    """
    :param request:
    :param model_class: this model class should have a method clear_submissions()
    :return:
    """
    objects=model_class.objects.all()
    try:
        for object in objects:
            object.clear_submissions()
        messages.info(request,"Submission data have been cleared")
    except:
        messages.info(request,"Error occurred in clearing submission data")
    return HttpResponseRedirect(reverse("home"))

@csrf_exempt
def system_configuration(request):
    form=ConfigurationForm()
    if (request.POST):
        form=ConfigurationForm(request.POST)
        if(form.is_valid()):
            form.save_configuration()
            messages.info(request,"Configurations have been successfully saved!")
            return HttpResponseRedirect(reverse("home"))
    return render(request, "appglobal/configuration.html",{'form':form})



def file_download(request,file_name,type):
    """
    handle downloading of assignment/question instruction files
    :param request:
    :param file_name:
    :return: django's serve response
    """
    #TODO: check whether the file exists
    if (type in INSTRUCTION_FILE_RELATIVE_PATH.keys()):
        file_path=os.path.join(MEDIA_ROOT,INSTRUCTION_FILE_RELATIVE_PATH[type],file_name)
        return serve(request, os.path.basename(file_path), os.path.dirname(file_path))
    else:
        return Http404("No such download type: " + type)


import csv
from django.http import HttpResponse

def csv_response(request,data_table,file_name="new_csv"):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(file_name)
    writer = csv.writer(response)
    for row in data_table:
        writer.writerow(row)
    return response