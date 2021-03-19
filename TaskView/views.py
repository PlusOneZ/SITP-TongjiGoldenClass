from django.shortcuts import render, HttpResponse, Http404
from django.http import StreamingHttpResponse
from .models import Task, UploadedTaskFile, RestrictedFileField
from CourseView.views import check_login, basic_info_dict
from CourseView.models import User, Course
from django import forms


# Create your views here.


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), max_length=10485760)


class CourseFrom(forms.Form):
    title = forms.CharField(max_length=30, label="标题")
    subtitle = forms.CharField(max_length=50, label="副标题")
    chapter = forms.CharField(max_length=20, label="所属章节")
    brief = forms.CharField(widget=forms.Textarea, label="简介")
    content = forms.CharField(widget=forms.Textarea, label="内容，支持Markdown语法")


class TaskForm(forms.Form):
    title = forms.CharField(max_length=30, label="标题")
    task_type = forms.ChoiceField(
        choices=[
            ('1', "通知"),
            ('2', "翻转课"),
            ('3', "作业"),
            ('4', "任务")
        ],
        label="任务类型"
    )
    due_time = forms.CharField(
        max_length=30,
        label="截止时间，格式：[年-月-日 时:分] ",
        # widget=forms.DateTimeInput(format='%Y-%m-%d %H:%M')
    )
    brief = forms.CharField(widget=forms.Textarea, label="简介")
    content = forms.CharField(widget=forms.Textarea, label="任务介绍")
    allow_file = forms.ChoiceField(choices=[('True', "是"), ('False', "否")], label="允许上传文件")


# Task page
@check_login
def task_list_view(request) -> HttpResponse:
    ret = basic_info_dict(request, 'task')
    tasks = Task.objects.all()
    items = [t.as_brief_dict() for t in tasks]
    ret.update({
        "items": items,
    })
    return render(request, 'tasks.html', ret)


@check_login
def task_view(request, index) -> HttpResponse:
    try:
        task = Task.objects.get(index=index)
    except Task.DoesNotExist:
        raise Http404
    user_id = request.COOKIES.get('user_id')
    task_dict = task.as_content_dict()
    task_dict.update(basic_info_dict(request, 'task'))
    task_dict['error'] = ''
    task_dict['teacher_view'] = False

    role = User.objects.get(ID=user_id).role

    if role == User.STUDENT:
        if request.method == 'POST':
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                if task.file_type == 'IMAGE':
                    content = RestrictedFileField.IMAGE
                elif task.file_type == 'TEXT':
                    content = RestrictedFileField.TEXT
                elif task.file_type == 'AUDIO':
                    content = RestrictedFileField.AUDIO
                elif task.file_type == 'COMPRESS':
                    content = RestrictedFileField.COMPRESSED
                else:
                    content = []
                print(content)
                try:
                    uploaded_file = UploadedTaskFile.create_instance(
                        task=task,
                        student=User.objects.get(ID=user_id),
                        file=request.FILES.get('file'),
                        content_type=content
                    )
                    uploaded_file.save()
                    print("ok")
                    task_dict['error'] = '上传成功'
                except forms.ValidationError:
                    task_dict['error'] = "文件格式不正确，请提供" + task.get_file_type_display() + "格式的文件。"
                    print('type not ok')
            else:
                print("not ok" + str(form.errors) + str(request.FILES))

        if task_dict['allow_files']:
            form = UploadFileForm()
            task_dict['form'] = form
        try:
            Task.objects.get(index=index - 1)
            task_dict['prev_page'] = str(index - 1)
        except Task.DoesNotExist:
            pass
        try:
            Task.objects.get(index=index + 1)
            task_dict['next_page'] = str(index + 1)
        except Task.DoesNotExist:
            pass
        return render(request, 'task.html', task_dict)

    elif role == User.TEACHER:
        task_dict['teacher_view'] = True
        files = UploadedTaskFile.objects.filter(task=task)
        task_dict['files'] = files
        task_dict['suffix'] = '?next=/task/' + str(task.index)
        return render(request, 'task.html', task_dict)


@check_login
def download(request, index):
    try:
        file_name = UploadedTaskFile.objects.get(index=index).file.name
        file = open("uploads/" + file_name, 'rb')
        response = StreamingHttpResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename=' + str('"' + file_name + '"')
        return response
    except UploadedTaskFile.DoesNotExist:
        return Http404


@check_login
def publish(request, type_name: str):
    ret = basic_info_dict(request, 'publish+' + type_name)
    if type_name == 'course':
        if request.method == 'POST':
            form = CourseFrom(request.POST)
            if form.is_valid():
                course = Course(
                    heading=request.POST['title'],
                    subheading=request.POST['subtitle'],
                    brief=request.POST['brief'],
                    chapter=request.POST['chapter'],
                    content=request.POST['content']
                )
                course.save()
                ret['hint'] = str(request.POST['title']) + "上传成功！"
            else:
                ret['hint'] = "上传失败，请重试。"
        form = CourseFrom()
        ret['form'] = form
        ret['heading'] = "发布课程"
        return render(request, 'publish.html', ret)
    elif type_name == 'task':
        if request.method == 'POST':
            form = TaskForm(request.POST)
            if form.is_valid():
                task = Task(
                    title=request.POST['title'],
                    task_type=request.POST['task_type'],
                    due_time=request.POST['due_time'],
                    brief=request.POST['brief'],
                    content=request.POST['content'],
                    allow_files=(request.POST['allow_file'] == 'True'),
                    file_type=[]
                )
                task.save()
                ret['hint'] = str(request.POST['title']) + "上传成功！"
            else:
                ret['hint'] = "上传失败，请重试。"
                print(form.errors)
        form = TaskForm()
        ret['form'] = form
        ret['heading'] = "发布任务"
        return render(request, 'publish.html', ret)
    else:
        return Http404
