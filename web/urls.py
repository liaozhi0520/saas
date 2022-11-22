from django.urls import re_path
from web.views.account import *
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
]