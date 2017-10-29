from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

class StudentGroup(models.Model):
    name=models.CharField(max_length=200,unique=True)
    course=models.CharField(max_length=200,blank=True,null=True)

    def __unicode__(self):
        return self.name
#-----------------------attribute methods------------------------
    def get_number_of_members(self):
        return len(self.studentuserprofile_set.all())

    def add_students_by_ids(self,id_list):
        for id in id_list:
            if (id.isdigit()):
                p=StudentUserProfile.objects.get(id=id)
                p.groups.add(self)

    def remove_students_by_ids(self,id_list):
        for id in id_list:
            if (id.isdigit()):
                p=StudentUserProfile.objects.get(id=id)
                p.groups.remove(self)

    def get_students_in_group(self):
        """
        :return: list of StudentProfile
        """
        return self.studentuserprofile_set.all()

    def get_students_not_in_group(self):
        """
        :return: list of StudentProfile
        """
        return [p for p in StudentUserProfile.objects.all() if (p not in self.studentuserprofile_set.all())]

    @staticmethod
    def get_student_group_for_user(user):
        """
        :param user:
        :return: list of groups that include the given user
        """
        profile=StudentUserProfile.objects.get(user=user)
        return profile.groups.all()


    def get_members_link(self):
        return """<a href="{}">Members</a>""".format(reverse("group_member_list",args=[self.id]))


class StudentUserProfile(models.Model):
    user=models.OneToOneField(User)
    fullname=models.CharField(max_length=200)
    #last_name=models.CharField(max_length=500)
    matric_number=models.CharField(max_length=100,null=True,blank=True)
    groups=models.ManyToManyField(StudentGroup)

    class Meta:
        ordering=['user']
#----------------------attribute methods-----------------------------
    def _get_edit_url(self):
        return reverse("student_user_profile_edit",args=[self.user.id])

    edit_url=property(_get_edit_url)

    def get_full_name(self):
        return self.fullname

    def get_username(self):
        return self.user.username

    def get_email(self):
        return self.user.email

    def get_reset_password(self):
        return """<a href="{}">Reset</a>""".format(reverse("reset_password",args=[self.id]))

    def get_group_id_list(self):
        groups=self.groups.all()
        return [group.id for group in groups]

    def get_group_name(self):
        group_names=[group.name for group in self.groups.all()]
        return " , ".join(group_names)

#---------------------data manipulation methods--------------------
    def add_groups_by_names(self,group_names):
        # group names is a list
        for name in group_names:
            group=StudentGroup.objects.filter(name=name)[0]
            self.groups.add(group.id)

    def clean_up(self):
        self.user.delete()


class AttemptRecord(models.Model):
    user=models.ForeignKey(User)
    number_of_attempts=models.IntegerField(default=0)
