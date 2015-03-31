'''
The MIT License (MIT)

Copyright (c) 2014 NTHUOJ team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
import time
import random
import autocomplete_light
from django.http import Http404
from django.utils import timezone
from utils.log_info import get_logger
from contest.models import Contest
from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime, timedelta
from users.models import User, Notification
from django.template import RequestContext
from utils.user_info import validate_user
from django.template import RequestContext
from django.db.models import Q
from users.models import User
from problem.models import Problem
from contest.models import Contest
from group.models import Group

# Create your views here.
logger = get_logger()



def gg(request):
    return render(request, 'index/team_list.html')

def index(request, alert_info='none'):
    present = timezone.now()
    time_threshold = datetime.now() + timedelta(days=1);
    c_runnings = Contest.objects.filter \
        (start_time__lt=present, end_time__gt=present, is_homework=False)
    c_upcomings = Contest.objects.filter \
        (start_time__gt=present, start_time__lt=time_threshold, is_homework=False)
    return render(request, 'index/index.html',
                {'c_runnings':c_runnings, 'c_upcomings':c_upcomings,
                'alert_info':alert_info},
                context_instance=RequestContext(request, processors=[custom_proc]))

def navigation_autocomplete(request):
    q = request.GET.get('q', '')

    queries = {}

    queries['users'] = User.objects.filter(
        username__istartswith=q
    )[:5]

    queries['problems'] = Problem.objects.filter(
        Q(pname__icontains=q) |
        Q(id__contains=q)
    )[:10]

    queries['contests'] = Contest.objects.filter(
        cname__icontains=q
    )[:5]

    queries['groups'] = Group.objects.filter(
        gname__icontains=q
    )[:5]

    return render(request, 'index/navigation_autocomplete.html', queries)


def custom_404(request):
    return render(request, 'index/404.html', status=404)

def custom_500(request):
    return render(request, 'index/500.html',{'error_message':'error'}, status=500)

def base(request):
    return render(request, 'index/base.html',{},
                context_instance=RequestContext(request, processors=[custom_proc]))

def get_time(request):
    t = time.time()
    tstr = datetime.fromtimestamp(t).strftime('%Y/%m/%d %H:%M:%S')
    return HttpResponse(tstr)

def custom_proc(request):

    amount = Notification.objects.filter \
        (receiver=request.user, read=False).count()

    t = time.time()
    tstr = datetime.fromtimestamp(t).strftime('%Y/%m/%d %H:%M:%S')
    people = random.randint(100,999)
    return {
        'tstr': tstr,
        'people': people,
        'amount': amount
    }
