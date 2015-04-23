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
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.core.servers.basehttp import FileWrapper
from django.utils import timezone

from utils.render_helper import render_index
from users.models import User
from problem.models import Problem, Tag, Testcase
from problem.forms import ProblemForm, TagForm
from utils import log_info, config_info
from problem.problem_info import *
from utils import log_info
from utils.render_helper import render_index, get_current_page

import os
import json

logger = log_info.get_logger()

# Create your views here.
def problem(request):
    can_add_problem = False
    if request.user.is_anonymous():
        can_add_problem = False
    else:
        can_add_problem = request.user.has_subjudge_auth()
    all_problem_list = get_problem_list(request.user)
    all_problem = get_current_page(request, all_problem_list, 15)
    for p in all_problem:
        if p.total_submission != 0:
            p.pass_rate = float(p.ac_count) / float(p.total_submission) * 100.0
            p.not_pass_rate = 100.0 - p.pass_rate
            p.pass_rate = "%.2f" % (p.pass_rate)
            p.not_pass_rate = "%.2f" % (p.not_pass_rate)
        else:
            p.no_submission = True

    return render_index(request, 'problem/panel.html',
                  {'all_problem': all_problem,
                   'can_add_problem': can_add_problem})

def detail(request, pid):
    user = request.user
    tag_form = TagForm()
    try:
        problem = Problem.objects.get(pk=pid)
        if not problem.visible and user != problem.owner and not user.has_admin_auth():
            raise PermissionDenied()
        last_contest = problem.contest_set.all().order_by('-start_time')
        if len(last_contest) > 0:
            if last_contest[0].start_time < timezone.now():
                problem.visible = True
                problem.save()
    except Problem.DoesNotExist:
        logger.warning('problem %s not found' % (pid))
        raise Http404('problem %s does not exist' % (pid))
    problem.testcase = get_testcase(problem)
    return render_index(request, 'problem/detail.html', {'problem': problem, 'tag_form': tag_form})

@login_required
def new(request):
    if request.method == "GET":
        return render_index(request, "problem/new.html")
    elif request.method == "POST":
        if 'pname' in request.POST and request.POST['pname'].strip() != "":
            p = Problem(pname=request.POST['pname'], owner=request.user)
            p.save()
            logger.info("problem %s created by %s" % (p.pk, request.user))
            return redirect("/problem/%d/edit/" % p.pk)
        else:
            return render_index(request, "problem/new.html", {"error": "Problem name empty"})

@login_required
def edit(request, pid=None):
    tag_form = TagForm()
    try:
        problem = Problem.objects.get(pk=pid)
        if not request.user.has_admin_auth() and request.user != problem.owner:
            logger.warning("user %s has no permission to edit problem %s" % (request.user, pid))
            raise PermissionDenied()
    except Problem.DoesNotExist:
        logger.warning("problem %s does not exist" % (pid))
        raise Http404("problem %s does not exist" % (pid))
    testcase = Testcase.objects.filter(problem=problem)
    tags = problem.tags.all()
    if request.method == 'GET':
        form = ProblemForm(instance=problem,
                           initial={'owner': request.user.username})
    if request.method == 'POST':
        form = ProblemForm(request.POST,
                           instance=problem,
                           initial={'owner': request.user.username})
        if form.is_valid():
            problem = form.save(commit=False)
	    if not request.user.has_admin_auth():
		problem.owner = request.user
            problem.description = request.POST['description']
            problem.input= request.POST['input_description']
            problem.output = request.POST['output_description']
            problem.sample_in = request.POST['sample_in']
            problem.sample_out = request.POST['sample_out']
            problem.save()
            file_ex = get_problem_file_extension(problem)
            if "special_judge_code" in request.FILES:
                with open('%s%s%s' % (SPECIAL_PATH, problem.pk, file_ex), 'w') as t_in:
                    for chunk in request.FILES['special_judge_code'].chunks():
                        t_in.write(chunk)
            if "partial_judge_code" in request.FILES:
                with open('%s%s%s' % (PARTIAL_PATH, problem.pk, file_ex), 'w') as t_in:
                    for chunk in request.FILES['partial_judge_code'].chunks():
                        t_in.write(chunk)
            logger.info('edit problem, pid = %d by %s' % (problem.pk, request.user))
            logger.info('edit problem, pid = %d' % (problem.pk))
            return redirect('/problem/%d' % (problem.pk))
	else:
	    print "not valid"
    return render_index(request, 'problem/edit.html',
                            {'form': form, 'pid': pid, 'pname': problem.pname,
                             'tags': tags, 'tag_form': tag_form, 'description': problem.description,
                             'input': problem.input, 'output': problem.output,
                             'sample_in': problem.sample_in, 'sample_out': problem.sample_out,
                             'testcase': testcase,
                             'path': {
                                 'TESTCASE_PATH': TESTCASE_PATH,
                                 'SPECIAL_PATH': SPECIAL_PATH,
                                 'PARTIAL_PATH': PARTIAL_PATH, },
                             'has_special_judge_code': has_special_judge_code(problem),
                             'has_partial_judge_code': has_partial_judge_code(problem),
                             'file_ex': get_problem_file_extension(problem)})

@login_required
def tag(request, pid):
    if request.method == "POST":
        tag = request.POST['tag_name']
        try:
            problem = Problem.objects.get(pk=pid)
        except Problem.DoesNotExist:
            logger.warning("problem %s does not exist" % (pid))
            raise Http404("problem %s does not exist" % (pid))
        if not problem.tags.filter(tag_name=tag).exists():
            new_tag, created = Tag.objects.get_or_create(tag_name=tag)
            problem.tags.add(new_tag)
            problem.save()
            logger.info("add new tag '%s' to problem %s by %s" % (tag, pid, request.user))
            return HttpResponse(json.dumps({'tag_id': new_tag.pk}),
                                content_type="application/json")
        return HttpRequestBadRequest()
    return HttpResponse()

@login_required
def delete_tag(request, pid, tag_id):
    try:
        problem = Problem.objects.get(pk=pid)
        tag = Tag.objects.get(pk=tag_id)
    except Problem.DoesNotExist:
        logger.warning("problem %s does not exist" % (pid))
        raise Http404("problem %s does not exist" % (pid))
    except Tag.DoesNotExist:
        logger.warning("tag %s does not exist" % (tag_id))
        raise Http404("tag %s does not exist" % (tag_id))
    if not request.user.has_admin_auth() and request.user != problem.owner:
        raise PermissionDenied()
    logger.info("tag %s deleted by %s" % (tag.tag_name, request.user))
    problem.tags.remove(tag)
    return HttpResponse()

@login_required
def testcase(request, pid, tid=None):
    if request.method == 'POST':
        try:
            problem = Problem.objects.get(pk=pid)
        except Problem.DoesNotExist:
            logger.warning("problem %s does not exist" % (pid))
            raise Http404("problem %s does not exist" % (pid))
        if tid == None:
            testcase = Testcase()
            testcase.problem = problem
        else:
            try:
                testcase = Testcase.objects.get(pk=tid)
            except Testcase.DoesNotExist:
                logger.warning("testcase %s does not exist" % (tid))
                raise Http404("testcase %s does not exist" % (tid))
            if testcase.problem != problem:
                logger.warning("testcase %s does not belong to problem %s" % (tid, pid))
                raise Http404("testcase %s does not belong to problem %s" % (tid, pid))
        if 'time_limit' in request.POST:
            testcase.time_limit = request.POST['time_limit']
            testcase.memory_limit = request.POST['memory_limit']
            testcase.save()
            logger.info("testcase saved, tid = %s by %s" % (testcase.pk, request.user))
        if 't_in' in request.FILES:
            TESTCASE_PATH = config_info.get_config('path', 'testcase_path')
            try:
                with open('%s%s.in' % (TESTCASE_PATH, testcase.pk), 'w') as t_in:
                    for chunk in request.FILES['t_in'].chunks():
                        t_in.write(chunk)
                    logger.info("testcase %s.in saved by %s" % (testcase.pk, request.user))
                with open('%s%s.out' % (TESTCASE_PATH, testcase.pk), 'w') as t_out:
                    for chunk in request.FILES['t_out'].chunks():
                        t_out.write(chunk)
                    logger.info("testcase %s.out saved by %s" % (testcase.pk, request.user))
            except IOError, OSError:
                logger.error("saving testcase error")
            return HttpResponse(json.dumps({'tid': testcase.pk}),
                                content_type="application/json")
    return HttpResponse()

@login_required
def delete_testcase(request, pid, tid):
    try:
        problem = Problem.objects.get(pk=pid)
        testcase = Testcase.objects.get(pk=tid)
    except Problem.DoesNotExist:
        logger.warning("problem %s does not exist" % (pid))
        raise Http404("problem %s does not exist" % (pid))
    except Testcase.DoesNotExist:
        logger.warning("testcase %s does not exist" % (tid))
        raise Http404("testcase %s does not exist" % (tid))
    if not request.user.has_admin_auth() and request.user != problem.owner:
        raise PermissionDenied
    logger.info("testcase %d deleted" % (testcase.pk))
    try:
        os.remove('%s%d.in' % (TESTCASE_PATH, testcase.pk))
        os.remove('%s%d.out' % (TESTCASE_PATH, testcase.pk))
    except IOError, OSError:
        logger.error("remove testcase %s error" % (testcase.pk))
    logger.info("testcase %d deleted by %s" % (testcase.pk, request.user))
    testcase.delete()
    return HttpResponse()

def delete_problem(request, pid):
    try:
        problem = Problem.objects.get(pk=pid)
    except Problem.DoesNotExist:
        logger.warning("problem %s does not exist" % (pid))
        raise Http404("problem %s does not exist" % (pid))
    if not request.user.has_admin_auth() and request.user != problem.owner:
        raise PermissionDenied
    logger.info("problem %d deleted by %s" % (problem.pk, request.user))
    problem.delete()
    return redirect('/problem/')

def preview(request):
    problem = Problem()
    problem.pname = request.POST['pname']
    problem.description = request.POST['description']
    problem.input= request.POST['input_description']
    problem.output = request.POST['output_description']
    problem.sample_in = request.POST['sample_in']
    problem.sample_out = request.POST['sample_out']
    problem.tag = request.POST['tags'].split(',')
    return render_index(request, 'problem/preview.html', {'problem': problem, 'preview': True})

def download_testcase(request, filename):
    try:
        f = open(TESTCASE_PATH+filename, "r")
    except IOError:
        raise Http404()
    response = HttpResponse(FileWrapper(f), content_type="text/plain")
    response['Content-Disposition'] = 'attachment; filename=' + filename
    return response

