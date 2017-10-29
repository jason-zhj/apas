def is_staff(user):
    return user.groups.filter(name='staff').exists()

def is_student(user):
    return user.groups.filter(name='student').exists()
