from django.db import models

# Create your models here.
TASK_TYPES = [
    ('1', "通知"),
    ('2', "翻转课"),
    ('3', "作业"),
    ('4', "任务")
]

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


class Task(models.Model):
    index = models.IntegerField(primary_key=True)
    title = models.CharField(null=False, default='新任务', max_length=30)
    task_type = models.CharField(null=False, choices=TASK_TYPES, max_length=10, default='1')
    content = models.TextField(null=False, default='发布了新的任务')
    brief = models.TextField(default='任务描述')
    allow_files = models.BooleanField(default=True)
    due_time = models.DateField(null=True, default=None)

    def as_brief_dict(self) -> dict:
        return {
            'font_color': colors[self.index % len(colors)][1],
            'block_color': colors[self.index % len(colors)][0],
            'heading': str(self.title),
            'subheading': self.get_task_type_display(),
            'index': self.index,
            'graph_text': self.title[0],
            'brief': self.brief
        }

    def as_content_dict(self) -> dict:
        return {
            'heading': str(self.title),
            'content': self.content,
            'due_time': self.due_time,
            'allow_files': self.allow_files,
        }
