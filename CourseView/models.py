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


class Courses(models.Model):
    time = models.TimeField(auto_now=True)
    index = models.IntegerField(primary_key=True)
    heading = models.CharField(null=False, default='未知章节', max_length=30)
    subheading = models.CharField(default='快来学习吧！', max_length=50)
    brief = models.TextField(default='点击开始学习')
    content = MDTextField(null=False)

    @staticmethod
    def as_brief_dict(index: int) -> dict:
        course = Courses.objects.get(index=index)
        d = {
            "heading": "错误文章",
            "subheading": "请检查",
            "content": "",
            "graph_text": "0",
            "block_color": "black",
            "font_color": "red"
        }
        if course:
            d['font_color'] = colors[index % len(colors)][0]
            d['block_color'] = colors[index % len(colors)][1]
            d['heading'] = course.heading
            d['subheading'] = course.subheading
            if course.heading[0] != '第' or course.heading[0] != '期':
                d['graph_text'] = course.heading[0]
            else:
                d['graph_text'] = course.heading[1]
            d['content'] = course.brief
        return d
