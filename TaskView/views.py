from django.shortcuts import render, HttpResponse, Http404
from django.http import StreamingHttpResponse
from .models import Task, UploadedTaskFile, RestrictedFileField
from CourseView.views import check_login
from CourseView.models import User
from django import forms
# Create your views here.


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), max_length=10485760)


# Task page
@check_login
def task_list_view(request) -> HttpResponse:
    user_id = request.COOKIES.get('user_id')
    tasks = Task.objects.all()
    items = [t.as_brief_dict() for t in tasks]
    return render(
        request, 'tasks.html',
        {
            'user_name': user_id,
            "user_page": "/me",
            "items": items,
            'active': 'task'
        }
    )


@check_login
def task_view(request, index) -> HttpResponse:
    try:
        task = Task.objects.get(index=index)
    except Task.DoesNotExist:
        raise Http404
    user_id = request.COOKIES.get('user_id')
    task_dict = task.as_content_dict()
    task_dict['user_name'] = user_id
    task_dict['user_page'] = '/me'
    task_dict['active'] = 'task'
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
            Task.objects.get(index=index-1)
            task_dict['prev_page'] = str(index-1)
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
