from django.db import models
from CourseView.models import colors
from django.forms import forms
from django.template.defaultfilters import filesizeformat

from CourseView.models import User

# Create your models here.


class Task(models.Model):
    FILE_TYPES = [
        ('IMAGE', "图片"),
        ('COMPRESS', "压缩包"),
        ('TEXT', "文本"),
        ('AUDIO', "音频"),
        ('OTHER', "其他")
    ]

    TASK_TYPES = [
        ('1', "通知"),
        ('2', "翻转课"),
        ('3', "作业"),
        ('4', "任务")
    ]

    index = models.IntegerField(primary_key=True)
    title = models.CharField(null=False, default='新任务', max_length=30)
    task_type = models.CharField(null=False, choices=TASK_TYPES, max_length=10, default='1')
    content = models.TextField(null=False, default='发布了新的任务')
    brief = models.TextField(default='任务描述')
    allow_files = models.BooleanField(default=True)
    file_type = models.CharField(max_length=30, choices=FILE_TYPES, default='TEXT')
    due_time = models.DateField(null=True, default=None)

    def as_brief_dict(self) -> dict:
        return {
            'font_color': colors[self.index % len(colors)][1],
            'block_color': colors[self.index % len(colors)][0],
            'heading': str(self.title),
            'subheading': self.get_task_type_display(),
            'index': self.index,
            'graph_text': self.title[0],
            'brief': self.brief,
            'allow_file': self.allow_files
        }

    def as_content_dict(self) -> dict:
        return {
            'heading': str(self.title),
            'content': self.content,
            'due_time': self.due_time,
            'allow_files': self.allow_files,
            'subheading': self.get_task_type_display(),
        }


class RestrictedFileField(models.FileField):
    """ max_upload_size:
            2.5MB - 2621440
            5MB - 5242880
            10MB - 10485760
            20MB - 20971520
            50MB - 5242880
            100MB 104857600
            250MB - 214958080
            500MB - 429916160
    """
    IMAGE = ['image/jpeg', 'image/gif', 'image/png', 'image/bmp', 'image/']
    TEXT = ['application/pdf', 'application/msword', 'text/plain', 'text/csv', 'text/md', 'application/json']
    COMPRESSED = ['application/zip', 'application/rar']
    AUDIO = ['audio/mpeg', 'audio/ac3', 'audio/wav']

    def __init__(self, *args, **kwargs):
        self.content_types = kwargs.pop("content_types", [])
        self.max_upload_size = kwargs.pop("max_upload_size", [])

        super().__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super().clean(*args, **kwargs)
        file = data.file
        try:
            content_type = file
            if content_type in self.content_types:
                if file.size > self.max_upload_size:
                    raise forms.ValidationError('Please keep filesize under {}. Current filesize {}'
                                                .format(filesizeformat(self.max_upload_size),
                                                        filesizeformat(file.size)))
            else:
                if self.content_types:
                    raise forms.ValidationError('This file type is not allowed.')
        except AttributeError:
            pass
        # return data


class UploadedTaskFile(models.Model):
    task = models.ForeignKey(Task, on_delete=models.PROTECT)
    student = models.ForeignKey(User, on_delete=models.PROTECT)
    file = RestrictedFileField(max_upload_size=10485760, upload_to='tasks/')
    time = models.DateTimeField(auto_now_add=True)
    index = models.IntegerField(primary_key=True, default=0)

    @staticmethod
    def create_instance(task, student, file, content_type: list):
        obj = UploadedTaskFile.objects.create(task=task, student=student, file=file)
        obj.file.content_types = content_type
        # RestrictedFileField(obj.file).clean() # Still bugged
        return obj
