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
        (1,'individual free'),
        (2,'charged'),
        (3,'flur category')
    )
    category=models.PositiveSmallIntegerField(choices=CATEGORY_CHOICES)
    title=models.CharField(max_length=10)
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
    start_time=models.DateTimeField(null=True,blank=True) #when you create a transaction for a new user who is not paying anything
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
    name=models.CharField(max_length=32)
    description=models.CharField(max_length=128)
    color=models.CharField(max_length=7,choices=COLOR_PROJ)
    used_space=models.BigIntegerField(help_text="Bytes")
    star=models.PositiveSmallIntegerField(choices=STRAED_STATUS)
    creator=models.ForeignKey(to='UserInfo',on_delete=False)

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