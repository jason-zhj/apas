from django.contrib.auth.models import User,Group

from appglobal import CsvImporter
from account.models import StudentUserProfile

class StudentImporter(CsvImporter):

    group_to_add=Group.objects.get(name='student')
    group_name_splitter=","
    field_names = ["username","password","email",
                          "matric_number","fullname","groups"]

    def _handle_row(self,row):
        if (not self._is_row_valid(row)):
            return self._FAILED

        username=row["username"]
        if (self._is_username_exist(username)):
            if (self._do_update(row)):
                return self._UPDATED
            else:
                return self._FAILED
        else:
            if (self._do_save(row)):
                return self._CREATED
            else:
                return self._FAILED

    def _is_username_exist(self,username):
        return len(User.objects.filter(username=username))>0

    def _is_row_valid(self,row):
        for item in self.field_names:
            if (len(row[item])==0):
                return False
        return True

    def _do_save(self,row):
        # save user
        u=User()
        try:
            u=User.objects.create_user(username=row["username"],
                        password=row["password"],
                        email=row["email"])
            u.groups.add(self.group_to_add)
            u.save()
        except:
            return False
        # save profile
        try:
            p=StudentUserProfile.objects.create(user=u,
                                              fullname=row["fullname"],
                                              matric_number=row["matric_number"],
                                              )

            p.add_groups_by_names(row["groups"].strip().split(self.group_name_splitter))
            p.save()
        except:
            u.delete()
            return False

        return True

    def _do_update(self,row):
        # update user
        try:
            user=User.objects.get(username=row["username"])
            user.set_password(row["password"])
            user.email=row["email"]
            user.save()
        except:
            return False
        # update profile
        try:
            profile=StudentUserProfile.objects.get(user=user)
            profile.first_name=row["first_name"]
            profile.last_name=row["last_name"]
            profile.matric_number=row["matric_number"]
            # update group
            profile.add_groups_by_names(row["groups"].strip())
            profile.save()
        except:
            return False
        return True


