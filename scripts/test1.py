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
from web.models import Project
proj=Project.objects.filter(id=1).first()
print(proj.color)
