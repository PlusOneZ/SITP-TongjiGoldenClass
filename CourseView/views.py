from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect

from functools import wraps

from .models import User, Course

# Create your views here.

SALT = '盐巴'


# login decorator
def check_login(func):
    @wraps(func)
    def inner(request, *args, **kwargs):
        ret = request.get_signed_cookie("signed_in", default="0", salt=SALT)
        if ret == "1":
            return func(request, *args, **kwargs)
        # 没有登录过
        else:
            next_url = request.path_info
            return redirect("/signin/?next={}".format(next_url))

    return inner


# Index page for courses
@check_login
def index_view(request) -> HttpResponse:
    user_name = request.COOKIES.get('user_id')
    if not user_name:
        redirect('/signin?next={}'.format('/'))
    return redirect('/courses/1')


# User console page
@check_login
def console_view(request) -> HttpResponse:
    user_id = int(request.COOKIES.get('user_id'))
    role = User.objects.get(ID=user_id).role
    name = User.objects.get(ID=user_id).real_name
    if role == User.STUDENT:
        r = "同学"
    elif role == User.TEACHER:
        r = "老师"
    elif role == User.ADMIN:
        r = "管理员"
    else:
        r = ''
    return render(
        request, 'console.html',
        {
            'user_name': name,
            "user_page": "/me",
            "user_id": user_id,
            "user_title": r,
            'user_name_and_title': name + r + '的控制台'
        }
    )


# Task page
@check_login
def task_view(request) -> HttpResponse:
    user_id = int(request.COOKIES.get('user_id'))
    return render(
        request, 'courses.html',
        {
            'user_name': user_id,
            "user_page": "/me",
            'item': item,
            'title': "任务"
        }
    )


# Courses page
@check_login
def courses_list_view(request) -> HttpResponse:
    user_id = int(request.COOKIES.get('user_id'))
    data = Course.objects.order_by('time')
    items = [d.as_brief_dict() for d in data]
    return render(
        request, 'courses.html',
        {
            'user_name': user_id,
            "user_page": "/me",
            'items': items,
            'title': "课程"
        }
    )


# Course
def course_view(request, index=0) -> HttpResponse:
    print(request.path)
    course = Course.objects.get(index=index)
    if course:
        return render(request, 'index.html', course.as_content_dict())


# ############################### Login ##############################


# Sign in page
def sign_in_view(request) -> HttpResponse:
    hint = request.GET.get('hint')
    if hint == 'user_not_found':
        h = "User doesn't exist, please check your input."
    elif hint == 'wrong_password':
        h = "Wrong password, try again or contact your admin."
    elif hint:
        h = 'Unknown error.'
    else:
        h = ''

    return render(request, 'signin.html', {'hint': h})


# login logic check
def login_view(request) -> HttpResponse:
    user_id = request.POST["ID"]
    user_password = request.POST['pwd']
    next_url = request.GET.get("next")
    print(user_id, user_password)
    print(User.objects.all())

    try:
        user = User.objects.get(ID=int(user_id))
    except User.DoesNotExist:
        user = []

    if user:
        if user.pwd == user_password:
            if next_url:
                ret = redirect(next_url)
            else:
                ret = redirect('/')
            ret.set_signed_cookie('signed_in', '1', salt=SALT, max_age=10000)
            ret.set_cookie('user_id', str(user.ID))
        else:
            print('Wrong password')
            ret = HttpResponseRedirect('/signin?hint=wrong_password')
            ret.set_signed_cookie('signed_in', '0', salt=SALT, max_age=1000)
    else:
        print("User not exist")
        ret = HttpResponseRedirect('/signin?hint=user_not_found')
        ret.set_signed_cookie('signed_in', '0', salt=SALT, max_age=1000)

    return ret
