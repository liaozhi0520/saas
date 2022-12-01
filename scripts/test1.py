import django
import sys,os
ROOT_PROJ=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_PROJ)
os.environ.setdefault('DJANGO_SETTINGS_MODULE','saas.settings')
django.setup()
#the logic to create a django offline script
#1. use the django_setup()
#2.the setup method need to an evironment variable called 'DJANGO_SETTINGS_MODULE'
#3.utilize the os.environ.setdefault method to set envrion variable
#4.the setdefault method need key and value as its parameters
#5.when you set the value,you can set the abspath of your project settings file,but cons-
#idering the compability issue,you need to utilize the os.path.dirname method to find the
#root dir of your project,and then add it to the sys.path


# from web.models import UserInfo
# UserInfo.objects.create_user(username='test_for_offline_script',password='testpwd')
# from web.models import Project
# proj=Project.objects.filter(id=1).first()
# print(proj.color)
from web.models import *
import uuid,datetime


# user=UserInfo.objects.filter(username='nwu_001').first()
# pri_pol=PricePolicy.objects.filter(id=2).first()
# tran_info = {
#         'user':user,
#         'status':1,
#         'order_num':uuid.uuid4().hex,
#         'price_policy':pri_pol,
#         'num_pri_pol':1,
#         'amount_trans':30,
#         'end_time':datetime.datetime.now()+datetime.timedelta(days=30)
#     }
#
# tran=Transaction.objects.create(**tran_info)
# trans=Transaction.objects.filter(user=user).first()
# print(trans.start_time.tzinfo) #the tzinfo is None, because I change the USE_TZ to False
#and the time I get from the db hava no the attribute tzinfo
#and then I can compare it to datetime.datetime.now() object.

from web.models import Project,UserInfo

user=UserInfo.objects.filter(username='nwu_001').first()
proj_name_list=ProjectUser.objects.filter(user=user).values_list('project__name')
print(type(proj_name_list))
print(proj_name_list)

