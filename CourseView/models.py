from django.db import models
from mdeditor.fields import MDTextField
import markdown


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


colors = [
    ['#2f90b9', '#2f2f35'],
    ['#525288', '#983680'],
    ['#36292f', '#d2568c'],
    ['#621624', '#ee4866'],
    ['#132c33', '#2c9678'],
    ['#5b4913', '#fbc82f'],
    ['#862617', '#dc9123'],
    ['#482522', '#f43e06']
]


class Course(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    index = models.IntegerField(primary_key=True)
    heading = models.CharField(null=False, default='未知章节', max_length=30)
    subheading = models.CharField(default='快来学习吧！', max_length=50)
    brief = models.TextField(default='点击开始学习')
    content = MDTextField(null=False)

    def as_brief_dict(self) -> dict:
        d = {'font_color': colors[self.index % len(colors)][1], 'block_color': colors[self.index % len(colors)][0],
             'heading': self.heading, 'subheading': self.subheading, 'index': self.index}
        if self.heading[0] != '第' and self.heading[0] != '期':
            d['graph_text'] = self.heading[0]
        else:
            d['graph_text'] = self.heading[1]
        d['brief'] = self.brief
        return d

    def as_content_dict(self) -> dict:
        con = markdown.markdown(self.content)

        return {
            'heading': self.heading,
            'content': con,
            'time': self.time
        }
