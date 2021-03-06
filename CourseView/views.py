from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
# from django.views.defaults import page_not_found

from functools import wraps

from .models import *
from TaskView.models import Task

# Create your views here.

SALT = '盐巴'


def basic_info_dict(request, highlight: str) -> dict:
    user_id = request.COOKIES.get('user_id')
    role = User.objects.get(ID=user_id).role
    ret = {"user_name": user_id}
    if role == User.TEACHER or role == User.ADMIN:
        ret['teacher_view'] = True
    else:
        ret['teacher_view'] = False
    ret['active'] = highlight
    ret["user_page"] = "/me"
    return ret


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
    ret = basic_info_dict(request, 'none')
    user_id = request.COOKIES.get('user_id')
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
        ret['progress'] = table
    elif role == User.TEACHER:
        courses = Course.objects.all()
        tasks = Task.objects.all()
        ret.update({'courses': courses, 'tasks': tasks})

    ret.update({
        'user_name': name,
        "user_title": r,
        'user_name_and_title': name + r + '的控制台',
    })
    return render(request, 'console.html', ret)


# Courses page
@check_login
def courses_list_view(request) -> HttpResponse:
    ret = basic_info_dict(request, 'course')
    data = Course.objects.order_by('time')
    items = [d.as_brief_dict() for d in data]
    ret.update({
        'items': items,
        'title': "课程",
    })
    return render(request, 'courses.html', ret)


# Course
@check_login
def course_view(request, index=0) -> HttpResponse:
    course_dict = basic_info_dict(request, 'course')
    try:
        course = Course.objects.get(index=index)
    except Course.DoesNotExist:
        raise Http404
    # record
    user_id = int(request.COOKIES.get('user_id'))
    if not Learns.objects.filter(course=course):
        learns = Learns.objects.create(student=User.objects.get(ID=user_id), course=course)
        learns.save()
    else:
        learns = Learns.objects.get(course=course)
        learns.time = learns.time.now()
        learns.save()
    # build dict
    course_dict.update(course.as_content_dict())
    # prev and next
    try:
        Course.objects.get(index=index - 1)
        course_dict['prev_page'] = str(index - 1)
    except Course.DoesNotExist:
        pass
    try:
        Course.objects.get(index=index + 1)
        course_dict['next_page'] = str(index + 1)
    except Course.DoesNotExist:
        pass
    return render(request, 'index.html', course_dict)


@check_login
def in_develop(request) -> HttpResponse:
    d = basic_info_dict(request, 'none')
    return render(request, 'in_development.html', d)


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
        user = User.objects.get(ID=user_id)
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
            ret.set_signed_cookie('signed_in', '0', salt=SALT)
    else:
        print("User not exist")
        ret = HttpResponseRedirect('/signin?hint=user_not_found')
        ret.set_signed_cookie('signed_in', '0', salt=SALT)
    return ret


# Logout
def logout(request) -> HttpResponse:
    ret = redirect('/')
    ret.set_signed_cookie('signed_in', '0', salt=SALT)
    ret.set_cookie('user_id', str('undefined'))
    return ret
