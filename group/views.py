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
SOFTWARE.'''

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, render
from django.utils import timezone
from django.forms.models import model_to_dict
from group.forms import GroupForm, GroupFormEdit, AnnounceForm
from group.models import Group, Announce
from utils.user_info import has_group_ownership, has_group_coownership
from utils.log_info import get_logger
from utils.render_helper import render_index
from users.models import User


logger = get_logger()

def get_group(group_id):
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        logger.warning('Group: Can not edit group %s! Group does not exist!' % group_id)
        raise Http404('Group: Can not edit group %s! Group does not exist!' % group_id)
    return group

def get_running_contest(request, group_id):

    group = get_group(group_id)
    all_contest = group.trace_contest.all()
    all_running_contest_list = []
    now = timezone.now()

    for contest in all_contest:
        if contest.start_time < now and contest.end_time > now:
            all_running_contest_list.append(contest)

    paginator = Paginator(all_running_contest_list, 15)  # Show 25 users per page
    page = request.GET.get('page')

    try:
        all_running_contest_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        all_running_contest_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        all_running_contest_list = paginator.page(paginator.num_pages)

    return render_index(
        request, 'group/viewall.html', {
            'data_list': all_running_contest_list,
            'title': 'running contest',
            'list_type': 'runContest',
        })

def get_ended_contest(request, group_id):

    group = get_group(group_id)
    all_contest = group.trace_contest.all()
    all_ended_contest_list = []
    now = timezone.now()

    for contest in all_contest:
        if contest.end_time < now:
            all_ended_contest_list.append(contest)

    paginator = Paginator(all_ended_contest_list, 15)  # Show 25 users per page
    page = request.GET.get('page')

    try:
        all_ended_contest_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        all_ended_contest_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        all_ended_contest_list = paginator.page(paginator.num_pages)

    return render_index(
        request, 'group/viewall.html', {
            'data_list': all_ended_contest_list,
            'title': 'ended contest',
            'list_type': 'endContest',
        })

def get_all_announce(request, group_id):

    group = get_group(group_id)
    user_is_owner = has_group_ownership(request.user, group)
    form = AnnounceForm()
    all_announce_list = group.announce.all()

    paginator = Paginator(all_announce_list, 15)  # Show 25 users per page
    page = request.GET.get('page')

    try:
        all_announce_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        all_announce_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        all_announce_list = paginator.page(paginator.num_pages)

    return render_index(
        request, 'group/viewall.html', {
            'data_list': all_announce_list,
            'title': 'announce',
            'list_type': 'announce',
            'user_is_owner': user_is_owner,
            'group_id': group.id,
        })


def detail(request, group_id):

    group = get_group(group_id)
    show_number = 5; #number for brief list to show in group detail page.
    all_contest = group.trace_contest.all()
    annowence_list = group.announce.all()
    student_list = group.member.order_by('user_level')
    coowner_list = group.coowner.all()
    owner = group.owner
    user_is_owner = has_group_ownership(request.user, group)
    user_is_coowner = has_group_coownership(request.user, group)
    form = AnnounceForm()
    running_contest_list = []
    ended_contest_list = []
    now = timezone.now()
    for contest in all_contest:
        if contest.start_time < now and contest.end_time > now:
            running_contest_list.append(contest)
        elif contest.end_time < now:
            ended_contest_list.append(contest)

    paginator = Paginator(student_list, 15)  # Show 25 users per page
    page = request.GET.get('page')

    try:
        student_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        student_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        student_list = paginator.page(paginator.num_pages)

    return render_index(
        request, 'group/groupDetail.html', {
            'running_contest_list': running_contest_list[0:show_number],
            'ended_contest_list': ended_contest_list[0:show_number],
            'announce_list': annowence_list,
            'coowner_list': coowner_list,
            'owner': owner,
            'student_list': student_list,
            'group_name': group.gname, 
            'group_description': group.description,
            'group_id': group.id,
            'user_is_owner': user_is_owner,
            'user_is_coowner': user_is_coowner,
            'form': form,
        })


def list(request):
    all_group = Group.objects.order_by('id')
    unsorted_group_list = Group.objects.filter(Q(member__username__contains=request.user.username) \
                                             | Q(owner__username=request.user.username) \
                                             | Q(coowner__username=request.user.username)).distinct()
    my_group = unsorted_group_list.order_by('id')
    page = request.GET.get('page')
    if request.user.is_anonymous():
        my_group = []
    paginator = Paginator(all_group, 25)  # Show 25 users per page
    try:
        all_group = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        all_group = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        all_group = paginator.page(paginator.num_pages)
    
    paginator = Paginator(my_group, 25)  # Show 25 users per page
    try:
        my_group = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        my_group = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        my_group = paginator.page(paginator.num_pages)

    return render_index(
        request,'group/groupList.html', {
            'all_group_list': all_group,
            'my_group_list': my_group,
        })

@login_required
def new(request):
    if request.user.has_judge_auth():
        if request.method == 'GET':
            form = GroupForm(initial={'owner':request.user})
            return render_index(request,'group/editGroup.html',{'form':form})
        if request.method == 'POST':
            form = GroupForm(request.POST, initial={'owner':request.user})
            if form.is_valid():
                new_group = form.save()
                logger.info('Group: Create a new group %s!' % new_group.id)
                return HttpResponseRedirect('/group/list')
            else:
                return render_index(
                    request,
                    'group/editGroup.html', {'form': form})
        else:
            return None
    else:
        raise PermissionDenied

@login_required
def delete(request, group_id):
    if request.user.has_judge_auth():
        group = get_group(group_id)
        deleted_gid = group.id
        group.delete()
        logger.info('Group: Delete group %s!' % deleted_gid)
        return HttpResponseRedirect('/group/list')
    else:
        raise PermissionDenied

@login_required
def delete_announce(request, announce_id, group_id):
    group = get_group(group_id)

    if has_group_ownership(request.user, group):  
        try:
            Announce.objects.get(id=announce_id).delete()
            return HttpResponseRedirect('/group/detail/%s' % group.id)
        except Announce.objects.get(id=announce_id).DoesNotExist:
            logger.info('Announce: already deleted %s!' % announce_id)
            raise Http404('Announce: already deleted %s!' % announce_id)
    else:
        raise PermissionDenied

@login_required
def delete_member(request, group_id, student_name):
    group = get_group(group_id)
    deleted_member = User.objects.get(username=student_name)
    
    if has_group_ownership(request.user, group):  
        try:
            group.member.remove(deleted_member)
            return HttpResponseRedirect('/group/detail/%s' % group.id)
        except:
            logger.info('Member: %s already deleted from group!' % student_name)
            raise Http404('Member: %s already deleted from group!' % student_name)
    else:
        raise PermissionDenied

@login_required
def edit(request, group_id):
        group = get_group(group_id)

        if has_group_ownership(request.user, group):
            if request.method == 'GET':
                group_dic = model_to_dict(group)
                form = GroupFormEdit(initial = group_dic)
                return render_index(request,'group/editGroup.html',{'form':form})
            if request.method == 'POST':
                form = GroupFormEdit(request.POST, instance = group)
                if form.is_valid():
                    modified_group = form.save()
                    logger.info('Group: Modified group %s!' % modified_group.id)
                    return HttpResponseRedirect('/group/detail/%s' % modified_group.id)
                else:
                    return render_index(
                        request,
                        'group/editGroup.html', {'form': form})
            else: 
                return None
        else:
            raise PermissionDenied

@login_required
def co_edit(request, group_id):
        group = get_group(group_id)

        if has_group_coownership(request.user, group):
            if request.method == 'GET':
                group_dic = model_to_dict(group)
                form = Co_GroupFormEdit(initial = group_dic)
                return render_index(request,'group/editGroup.html',{'form':form})
            if request.method == 'POST':
                form = Co_GroupFormEdit(request.POST, instance = group)
                if form.is_valid():
                    modified_group = form.save()
                    logger.info('Group: Modified group %s!' % modified_group.id)
                    return HttpResponseRedirect('/group/detail/%s' % modified_group.id)
                else:
                    return render_index(
                        request,
                        'group/editGroup.html', {'form': form})
            else: 
                return None
        else:
            raise PermissionDenied

@login_required
def add(request, group_id):
    group = get_group(group_id)

    if has_group_ownership(request.user, group):
        if request.method == 'POST':
            form = AnnounceForm(request.POST)
            if form.is_valid():
                new_announce = form.save()
                group.announce.add(new_announce)
                logger.info('Announce: User %s add Announce %s!' % (request.user.username, new_announce.id))
                return HttpResponseRedirect('/group/detail/%s' % group.id)
    else:
        raise PermissionDenied

