from django.shortcuts import render, HttpResponse, Http404
from .models import Task
from CourseView.views import check_login
from django import forms
# Create your views here.


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), max_length=10240)


# Task page
@check_login
def task_list_view(request) -> HttpResponse:
    user_id = int(request.COOKIES.get('user_id'))
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
    user_id = int(request.COOKIES.get('user_id'))
    task = task.as_content_dict()
    task['user_name'] = user_id
    task['user_page'] = '/me'
    task['active'] = 'task'
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            print("ok")
        else:
            print("not ok" + str(form.errors) + str(request.FILES))

    form = UploadFileForm()
    task['form'] = form
    try:
        Task.objects.get(index=index-1)
        task['prev_page'] = str(index-1)
    except Task.DoesNotExist:
        pass
    try:
        Task.objects.get(index=index + 1)
        task['next_page'] = str(index + 1)
    except Task.DoesNotExist:
        pass
    return render(request, 'task.html', task)
