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
from web.models import PricePolicy
PricePolicy.objects.create(
    category=1,
    title='individual free',
    price=0,
    proj_num=3,
    proj_space=20,
    per_file_size=20,
)
PricePolicy.objects.create(
    category=2,
    title='Premium 30RMB/month',
    price=30,
    proj_num=30,
    proj_space=200,
    per_file_size=50,
)

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

from web.models import Wiki,Project

# project=Project.objects.filter(name='test001').first()
# pwiki=Wiki.objects.filter(name='test001').first()
# data={
#     'name':'test003',
#     'content':'test003_content',
#     'project':project,
#     'pwiki':pwiki
# }
# Wiki.objects.create(**data)
#自关联的时候，基于对象的反向查询可以直接用 modelname_set 获得一大堆对象
#基于链查询的时候，就不能在values_list()当中使用 modelname_set__field 作为参数l
# cwikis=Wiki.objects.filter(name='test001').first().wiki_set.all()
# # query how many cwiki a wiki has, you need to use the syntax of reverse-query
# #which is got the wiki object and then do the modelname_set and then you will get a set of cwiki obejct
# cwikis_list=[]
# for cwiki in cwikis:
#     data={'id':cwiki.id, 'name':cwiki.name,}
#     cwikis_list.append(data)
# print(cwikis_list)
##above query is a type of query called query based on obejcts/instances

## I want to learn about another type called query based on chain

# res=Wiki.objects.filter(name='test001').values_list('wiki_set__name','wiki_set__content')
# print(res)
#self related: if I reverse query with the QBC, I need to put the modelname__filed
#but in self related, it can't do it, we can do it by related_name.

# from web.models import  UserInfo,Project,Wiki
#
# nwu_001=UserInfo.objects.filter(username='nwu_001').first()
# test_002=Project.objects.filter(creator=nwu_001,name='test002').first()
# Wiki.objects.create(title='test_008',content='test_008_content',project=test_002,pwiki=None,creator=nwu_001,category='I'
#                     )
# Wiki.objects.create(title='test_009',content='test_009_content',project=test_002,pwiki=None,creator=nwu_001,category='I')
#
