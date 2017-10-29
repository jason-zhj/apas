# response
from django.shortcuts import render,get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth import login,logout
from django.contrib.auth import authenticate
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group
# decorator
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from appglobal import save_uploaded_file,generate_unique_file_name,get_summary
from assignment.models import AssignmentSubmission
from onlinetest.models import OnlineTestSubmission

from account.forms import *
from account.helper import is_staff
from account.settings import USER_DATA_UPLOAD_PATH
from account.importer import StudentImporter

@csrf_exempt
def user_login(request):
    message=''
    if (request.method=="POST"):
        username=request.POST['username']
        password=request.POST['password']
        # authenticate the user
        user=authenticate(username=username,password=password)
        if (not user):
            # authentication failed
            message='Either the username or password is not correct'
        else:
            # authentication is okay
            new_assignment_submission_ids=None
            new_test_submission_ids=None
            if (is_staff(user)):
                new_assignment_submission_ids=[a.id for a in AssignmentSubmission.objects.filter(submission_time__gte=user.last_login) if a.is_completed]
                new_test_submission_ids=[a.id for a in OnlineTestSubmission.objects.filter(submission_time__gte=user.last_login)]
            login(request, user)
            request.session["new_assignment_submission_ids"]=new_assignment_submission_ids
            request.session["new_test_submission_ids"]=new_test_submission_ids
            if (request.GET.get("next")):
                return HttpResponseRedirect(request.GET.get("next"))
            else:
                return  HttpResponseRedirect('/home')

    return render(request, "account/login.html",{'message':message})


def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('user_login'))

def add_student_group(object):
    group = Group.objects.get(name='student')
    object.groups.add(group)


@transaction.atomic
@csrf_exempt
def profile_edit(request,user_id):
    object=None
    form=ProfileForm()

    profile=get_object_or_404(StudentUserProfile,id=user_id)
    user=profile.user
    form=ProfileForm(instance=profile)

    if (request.POST):
        form=ProfileForm(request.POST,instance=profile)
        if (form.is_valid()):
            profile=form.save(commit=False)
            profile.user=user
            profile.save()
            form.save_m2m()
            messages.info(request,str(profile) + " is successfully created!")
            return HttpResponseRedirect(reverse("student_user_profile_list"))

    return render(request, "account/class-studentuserprofile/edit.html",{'form':form,'student_user':user})

@csrf_exempt
def group_member_list(request,group_id):
    group=get_object_or_404(StudentGroup,id=group_id)
    if (request.POST):
        ids_to_add=request.POST['students_to_add'].split(",")
        ids_to_remove=request.POST['students_to_remove'].split(",")
        group.add_students_by_ids(ids_to_add)
        group.remove_students_by_ids(ids_to_remove)
        messages.info(request,"Adding/Removing students has been done!")

    # get a list of students in the group
    students_in_group=group.get_students_in_group()
    # get a list of students not in the group
    students_not_in_group=group.get_students_not_in_group()
    # return it
    group_summary=get_summary(source=group,fields=["name","course","get_number_of_members"])
    return render(request, "account/class-studentgroup/member-list.html",{'group_summary':group_summary,'students_in_group':students_in_group,'students_not_in_group':students_not_in_group})

@transaction.atomic
@csrf_exempt
def data_import(request,type='user'):
    #TODO: currently only support importing users, later can support importing groups
    if (request.FILES):
        file_path=save_uploaded_file(request.FILES['file'],filename=generate_unique_file_name(extension="csv"),filedir=USER_DATA_UPLOAD_PATH)
        im=StudentImporter(source=open(file_path))
        successful,result=im.import_to_database()
        success_message="The import is NOT successful, no data is imported!"
        if (successful):
            success_message= "The import is successful!\n" +result
        messages.info(request,success_message)
        return HttpResponseRedirect(reverse("student_user_profile_list"))
    return render(request,
                  "appglobal/import-data.html",{'type':type,'fields_required':"username,password,email,matric_number,fullname,groups"})

@transaction.atomic
@csrf_exempt
def change_password(request):
    """
    view for changing user's password
    """
    form=ChangePasswordForm(request.POST or None)
    if (form.is_valid()):
        old_password=form.cleaned_data['old_password']
        u=authenticate(username=request.user.username,password=old_password)
        if (u):
            u.set_password(form.cleaned_data['new_password'])
            u.save()
            messages.info(request,"Password is set successfully")
            return HttpResponseRedirect(reverse("home"))
        else:
            messages.info(request,"Old password is not correct")

    return render(request,
                  'account/change-password.html',{'form':form})


def reset_password(request,object_id):
    # automatically reset a password for user
    profile=get_object_or_404(StudentUserProfile,id=object_id)
    user=profile.user
    import string
    import random
    password_length=6
    new_password=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(password_length))
    user.set_password(new_password)
    user.save()
    return render(request,'account/reset-password.html',{'username':user.username,'password':new_password,'redirect_url':reverse("student_user_profile_list")})