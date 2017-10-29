from account.models import StudentUserProfile
from appglobal import get_or_none

# for returning user's fullname correctly
def user_fullname(request):
    try:
        user=request.user
        profile=get_or_none(StudentUserProfile,user=user)
        fullname=profile.fullname if profile else user.get_full_name()
        return {'fullname':fullname}
    except:
        return {'fullname':''}