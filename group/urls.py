from django.conf.urls import patterns, include, url
from django.contrib import admin
import views

urlpatterns = patterns('',
    url(r'^viewall_contest/(?P<group_id>\d+)/$', views.get_running_contest, name='viewall_contest'),
    url(r'^viewall_archive/(?P<group_id>\d+)/$', views.get_ended_contest, name='viewall_archive'),
    url(r'^viewall_announce/(?P<group_id>\d+)/$', views.get_all_announce, name='viewall_announce'),
    url(r'^list/$', views.list, name='list'),
    url(r'^detail/(?P<group_id>\d+)/$', views.detail, name='detail'),
    url(r'^new/$', views.new, name='new'),
    url(r'^delete/(?P<group_id>\d+)/$', views.delete, name='delete'),
    url(r'^edit/(?P<group_id>\d+)/$', views.edit, name='edit'),
    url(r'^co_edit/(?P<group_id>\d+)/$', views.co_edit, name='co_edit'),
    url(r'^add/(?P<group_id>\d+)/$', views.add, name='add'),
    url(r'^delete_announce/(?P<announce_id>\d+)/(?P<group_id>\d+)/$', views.delete_announce, name='delete_announce'),
    url(r'^delete_member/(?P<group_id>\d+)/(?P<student_name>\w+)/$', views.delete_member, name='delete_member'),
)
