from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
# from django.views.defaults import page_not_found

from functools import wraps

from .models import *

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

    table = []
    if role == User.STUDENT:
        progress = Learns.objects.filter(student=user_id)
        courses = Course.objects.all()
        for course in courses:
            if progress.filter(course=course.index):
                table.append({
                    'title': str(course.chapter) + str(course.heading),
                    'status': '完成',
                    'bool': 1,
                    'time': progress.get(course=course.index).time
                })
            else:
                table.append({
                    'title': str(course.chapter) + str(course.heading),
                    'status': '未完成',
                    'bool': 0,
                    'time': '-'
                })

    return render(
        request, 'console.html',
        {
            'user_name': name,
            "user_page": "/me",
            "user_id": user_id,
            "user_title": r,
            'user_name_and_title': name + r + '的控制台',
            'progress': table
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
@check_login
def course_view(request, index=0) -> HttpResponse:
    try:
        course = Course.objects.get(index=index)
    except Course.DoesNotExist:
        raise Http404
    # record
    user_id = int(request.COOKIES.get('user_id'))
    learns = Learns.objects.create(student=User.objects.get(ID=user_id), course=course)
    learns.save()
    # build dict
    course = course.as_content_dict()
    course['user_name'] = user_id
    course['user_page'] = '/me'
    # prev and next
    try:
        Course.objects.get(index=index-1)
        course['prev_page'] = str(index-1)
    except Course.DoesNotExist:
        pass
    try:
        Course.objects.get(index=index + 1)
        course['next_page'] = str(index + 1)
    except Course.DoesNotExist:
        pass
    return render(request, 'index.html', course)


@check_login
def in_develop(request) -> HttpResponse:
    user_id = int(request.COOKIES.get('user_id'))
    return render(request, 'in_development.html', {"user_name": user_id, 'user_page': '/me'})


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

    try:
        user = User.objects.get(ID=int(user_id))
    except User.DoesNotExist:
        user = None

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
