from django.urls import re_path
from web.views.account import *
from web.views.project_center import *
from django.conf.urls import include


urlpatterns=[
    re_path(r'^index/$',IndexView.as_view(),name='index'),
    re_path(r'^registration/',RegistrationView.as_view(),name='registration'),
    re_path(r'^login/$',LoginView.as_view(),name='login'),
    re_path(r'^validation_username/',ValidationUsernameView.as_view(),name='validation_username'),
    re_path(r'^validaiton_phone/',ValidationPhoneView.as_view(),name='validation_phone'),
    re_path(r'^test/$',TestView.as_view(),name='test'),
    re_path(r'^grap_check_code/$',GrapCheckCodeView.as_view(),name='graphic_check_code'),
    re_path(r'^reset_password/$',ResetPwdView.as_view(),name='reset_pwd'),
    re_path(r'^verify_old_password',VerifyOldPwdView.as_view(),name='verify_old_pwd'),
    re_path(r'^logout/$',LogoutView.as_view(),name='logout'),

    ## project center
    re_path(r'^project/list/$',ProjectListView.as_view(),name='project_list'),
    re_path(r'^project/create_proj/$', CreateProjView.as_view(), name='create_proj'),
    re_path(r'^project/starme/$',StarMyProjectView.as_view(),name='star_me'),
    re_path(r'^project/starinvol/$',StarInvolProjectView.as_view(),name='star_invol'),

    ##manage
    re_path(r'^manage/(?P<project_id>\d+)/',include([
        re_path(r'^dashboard/$',DashboardView.as_view(),name='dashboard'),
        re_path(r'^issues/$',IssuesView.as_view(),name='issues'),
        re_path(r'^statistics/$',StatisticsView.as_view(),name='statistics'),
        re_path(r'^wiki/$',WikiView.as_view(),name='wiki'),
        re_path(r'^file/$',FileView.as_view(),name='file'),
        re_path(r'^setting/$',SettingView.as_view(),name='setting')
    ],None)),
]
