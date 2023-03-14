from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
def bg_img_upload_path(instance,filename):
    return '/'.join(['bg_img','{}_{}'.format(instance.username,filename)])

def avatar_upload_path(instance,filename):
    return '/'.join(['avatar','{}_{}'.format(instance.username,filename)])
class UserInfo(AbstractUser):

    PROVINCE=(
        ('HEB','河北省'),('SX1','山西省'),('LN','辽宁省'),
        ('JL','吉林省'),('HLJ','黑龙江省'),
        ('JS','江苏省'),('ZJ','浙江省'),('AH','安徽省'),('FJ','福建省'),
        ('JX','江西省'),('SD','山东省'),('HEN','河南省'),('HUB','湖北省'),
        ('HUN','湖南省'),('GD','广东省'),('HN','海南省'),('SC','四川省'),
        ('GZ','贵州省'),('YN','云南省'),('SX2','陕西省'),('GS','甘肃省'),
        ('QH','青海省'),('NM','内蒙古自治区'),('GX','广西壮族自治区'),('XZ','西藏自治区'),
        ('NX','宁夏回族自治区'),('XJ','新疆维吾尔自治区'),
        ('BJ','北京市'),('TJ','天津市'),('SH','上海市'),('CX','重庆市')
    )
    GENDER=(
        ('M','Male'),
        ('F','Female'),
        ('S','Special')
    )
    phone=models.CharField(max_length=25)
    bg_img=models.ImageField(upload_to=bg_img_upload_path,default='bg_img/default.png')     #存放的是图片在mysql的地址吗
                                                                          #user 通过request将file传给wsgi，wsgi将request转化成对象进行使用，将file的内容放在request.FILES.get('FILE_NAME')当中
    province=models.CharField(max_length=3,choices=PROVINCE)
    gender=models.CharField(max_length=2,choices=GENDER)
    avatar=models.ImageField(upload_to=avatar_upload_path,default='avatar/default.png')

class ValidationPhone(models.Model):
    phone=models.CharField(max_length=11,default=None)
    code=models.CharField(max_length=6)
    exp_time=models.DateTimeField()

class PricePolicy(models.Model):
    CATEGORY_CHOICES=(
        (1,'free'),
        (2,'charged'),
    )
    category=models.PositiveSmallIntegerField(choices=CATEGORY_CHOICES)
    title=models.CharField(max_length=50)
    price=models.PositiveSmallIntegerField()
    proj_num=models.PositiveSmallIntegerField()
    proj_space=models.PositiveSmallIntegerField(help_text='GB')
    per_file_size=models.PositiveSmallIntegerField(help_text='MB')
    create_time=models.DateTimeField(auto_now_add=True)
#now I want to implete the function of knowing the user status of payment,so I need to
#build a table that show the status of payment called transaction
#and the table transaction need a foreign key to pricepolicy to know what's the transaction for

class Transaction(models.Model):
    STATUS_CHOICES=(
        (0,'unpayed'),
        (1,'payed'),
        (2,'cancled')
    )
    user=models.ForeignKey(to='UserInfo',on_delete=models.CASCADE)
    status=models.PositiveSmallIntegerField(choices=STATUS_CHOICES)
    order_num=models.CharField(max_length=64,unique=True)
    price_policy=models.ForeignKey(to='PricePolicy',on_delete=models.CASCADE)
    num_pri_pol=models.PositiveSmallIntegerField(verbose_name='numbers of that pricepolicy')
    amount_trans=models.PositiveSmallIntegerField()
    start_time=models.DateTimeField(auto_now_add=True,blank=True) #when you create a transaction for a new user who is not paying anything
    end_time=models.DateTimeField(null=True,blank=True)   #he can have the pricepolicy category 1 forever, so there is no start or end time
    create_time=models.DateTimeField(auto_now_add=True)

#So,now you can create a middelware to know the status of the logined user
#you select the transactions of the user,and select one who have a max number of pri_pol
#and then give a value to request.user.status(options:ordinary,vip,svip)
#if a user not logined(request.user is instance of Anonymous),don't even give the att
#ribute of status.

#now I have the status of user,I can give the project center different options by the stutus
class Project(models.Model):
    COLOR_PROJ = (
        (1, "#56b8eb"),  # 56b8eb
        (2, "#f28033"),  # f28033
        (3, "#ebc656"),  # ebc656
        (4, "#a2d148"),  # a2d148
        (5, "#20BFA4"),  # #20BFA4
        (6, "#7461c2"),  # 7461c2,
        (7, "#20bfa3"),  # 20bfa3,
    )
    #when I get an instance of this model, and access the color_proj,what type would I get.
    #you will get a integer listing above, and the second element is showing on the admin page
    STRAED_STATUS=(
        (0,'not stared'),
        (1,'stared')
    )
    name=models.CharField(max_length=15)
    description=models.CharField(max_length=128)
    color=models.CharField(max_length=7,choices=COLOR_PROJ)
    used_space=models.BigIntegerField(help_text="Bytes")
    star=models.PositiveSmallIntegerField(choices=STRAED_STATUS)
    creator=models.ForeignKey(to='UserInfo',on_delete=False)
    bucket_name=models.CharField(max_length=64)
    class Meta:
        constraints=[
            models.UniqueConstraint(fields=['name','creator'],name='unique_project_name')
        ]

class ProjectUser(models.Model):
    STRAED_STATUS = (
        (0, 'not stared'),
        (1, 'stared')
    )
    user=models.ForeignKey(to='UserInfo',on_delete=False)
    project=models.ForeignKey(to='Project',on_delete=models.CASCADE)
    star=models.PositiveSmallIntegerField(choices=STRAED_STATUS) #this star field is for showing my own stared project
    join_date=models.DateTimeField(auto_now_add=True)

#now when I take the token  request.user.status and get into the project center
#the page will show me that option1 to create a project
#option2 is the

class Wiki(models.Model):
    WIKI_CATEGORY=(
        ('P','Public'),
        ('I','Individual')
    )
    title=models.CharField(max_length=20)
    content=models.CharField(max_length=3000)
    project=models.ForeignKey(to='Project',on_delete=models.CASCADE)
    category=models.CharField(max_length=1,choices=WIKI_CATEGORY,default='P')
    creator=models.ForeignKey(to='UserInfo',on_delete=models.CASCADE)
    pwiki=models.ForeignKey(to='self',on_delete=models.CASCADE,null=True,blank=True)
    class Meta:
        constraints=[
            models.UniqueConstraint(fields=['title','project'],name='wiki_unique_in_project')
        ]
    #what'st the related name for?
    #when you want to check how many cwiki a pwiki have? You may want to do it like this:
    #Wiki.objects.filter(name='xxx').first().wiki_set.all()
    #反向查询用的是 modelname_set  (同理的是ForeignKey)
    #正向查询用的是 Wiki.objects.filter(name='xxx').first().pwiki

class File(models.Model):
    FILE_TYPE=(
        (1,'file'),
        (2,'folder'))
    project = models.ForeignKey(to='Project', on_delete=models.CASCADE)
    parent_file=models.ForeignKey(to='File',related_name='subfiles',on_delete=models.CASCADE,null=True)
    name=models.CharField(max_length=64)
    file_key=models.CharField(max_length=128,null=True)
    file_size=models.BigIntegerField(help_text='Bytes')
    file_type=models.PositiveSmallIntegerField(choices=FILE_TYPE)
    file_ext=models.CharField(max_length=32,null=True)
    creator=models.ForeignKey(to='UserInfo',on_delete=models.CASCADE)
    creating_time=models.DateTimeField(auto_now_add=True)
    class meta:
        constraints=[
            models.UniqueConstraint(fields=('name','project','parent_file'),name='InSameProjectAndSameFolderNameUnique'),
            models.CheckConstraint(check=(models.Q(file_type='folder') & models.Q(file_size=0)&models.Q(file_key=None)&models.Q(file_ext=None)),name='FolderSize0'),
            #this constraint will not change the model scheme, so no change detected
        ]

class Issue(models.Model):
    ISSUE_TYPE = (
        (1, 'task'),
        (2, 'bug'),
        (3, 'feature_discussion')
    )
    ISSUE_STATUS=(
        (1,'NEWLY_CREATED'),
        (2,'PROCESSING'),
        (3,'FINISHED'),
        (4,'TIMEOUT')
    )
    ISSUE_PRIVILEDGE=(
        (1,'low'),
        (2,'medium'),
        (3,'high'),
        (4,'premium')
    )
    title=models.CharField(max_length=64,)
    description=models.CharField(max_length=192)
    type=models.CharField(choices=ISSUE_TYPE,max_length=2)
    creator=models.ForeignKey(to='Userinfo',on_delete=models.CASCADE)
    status=models.CharField(choices=ISSUE_STATUS,max_length=2)
    priviledge=models.CharField(choices=ISSUE_PRIVILEDGE,max_length=2)
    creating_time=models.DateTimeField(auto_now_add=True)
    deadline_time=models.DateTimeField(null=True)  # that depends on the type of the issue
    last_updated_time=models.DateTimeField(auto_now=True)
    project=models.ForeignKey(to='Project',on_delete=models.CASCADE)

class IssueUser(models.Model):
    ISSUE_USER_RELATION=(
        (1,'creator'),
        (2,'manager'),
        (3,'invited')
    )
    issue=models.ForeignKey(to='Issue',on_delete=models.CASCADE)
    user=models.ForeignKey(to='UserInfo',on_delete=models.CASCADE,related_name='all_my_issues')
    relation=models.CharField(choices=ISSUE_USER_RELATION,max_length=2)
    operator=models.ForeignKey(to='UserInfo',on_delete=models.CASCADE,related_name='all_my_operating_issue')
    operating_time=models.DateTimeField(auto_now_add=True)

class IssueReply(models.Model):
    issue=models.ForeignKey(to='Issue',on_delete=models.CASCADE)
    parent_reply=models.ForeignKey(to='IssueReply',on_delete=models.CASCADE,related_name='subreplies')
    content=models.CharField(max_length=320)
    creator=models.ForeignKey(to='UserInfo',on_delete=models.CASCADE)
    reply_time=models.DateTimeField(auto_now_add=True)