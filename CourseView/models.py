from django.db import models


# Create your models here.
class User(models.Model):
    TEACHER = 'TE'
    STUDENT = 'ST'
    ADMIN = "AD"
    ROLE_CHOICE = [
        (TEACHER, 'Teacher'),
        (STUDENT, 'Student'),
        (ADMIN, 'Admin')
    ]

    ID = models.IntegerField(primary_key=True, null=False)
    pwd = models.TextField()
    real_name = models.CharField(
        max_length=20,
        default='同济大学的'
    )
    role = models.CharField(
        max_length=2,
        choices=ROLE_CHOICE,
        default=STUDENT
    )
