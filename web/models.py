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
    projects=models.ManyToManyField(to='Project')

class ValidationPhone(models.Model):
    phone=models.CharField(max_length=11,default=None)
    code=models.CharField(max_length=6)
    exp_time=models.DateTimeField()

class Project(models.Model):
    name=models.CharField(max_length=20)
    creator=models.ForeignKey(to='UserInfo',on_delete=False) # I don't pass the models.CASCADE to it,you know why?
    bgc = models.CharField(max_length=7)
    description=models.CharField(max_length=100)

