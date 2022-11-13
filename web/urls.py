from django.urls import re_path
from web.views.account import *
urlpatterns=[
    re_path(r'^registration/',RegistrationView.as_view(),name='registration'),
    re_path(r'^validation_username/',ValidationUsernameView.as_view(),name='validation_username'),
    re_path(r'^validaiton_phone/',ValidationPhoneView.as_view(),name='validation_phone'),
    re_path(r'^test/$',TestView.as_view(),name='test'),
    re_path(r'^filepond/$',FilePondView.as_view())
]