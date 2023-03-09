from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import uuid

#this is the tip from the official documentation:
#正常情况下一个 region 只需要生成一个 CosS3Client 实例，然后循环上传或下载对象，不能每次访问都生成 CosS3Client 实例，否则 python 进程会占用过多的连接和线程。
#so, the solution of mine is that I instantice the class I made to several objects the represent each region
#the list of the region
# beijing,nanjing,shanghai,guangzhou,chendu,chongqing
from saas.local_settings import app_id
class CosTencent():
    def __init__(self,region,token=None,scheme=None):
        try:
            import sys, os
            proj_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
            sys.path.append(proj_root)
            from saas import local_settings
            secret_key = local_settings.secret_key
            secret_id = local_settings.secret_id
            app_id=local_settings.app_id
        except Exception:
            print('significant parameters secret_key,secret_id and app_id are missing')
        self.config=CosConfig(Secret_key=secret_key,Secret_id=secret_id,Region=region,Token=token,Scheme=scheme)
        self.client=CosS3Client(self.config)

    def create_bucket(self,ACL='public-read'):
        #I need to valid that if the bucket is already existed
        #the bucket name must be this format <bucketname-appid>
        bucket_name=uuid.uuid4().hex+'-'+app_id
        #if you want to use others api, the best practic is the exception capture
        try:
            response = self.client.create_bucket(Bucket=bucket_name, ACL=ACL)
            flag=True
        except Exception as e:
            response=e
            flag=False
        return flag,response,bucket_name

    def put_object(self,bucket_name,fp,file_key,storage_class='STANDARD',enableMD5=False):
        response=self.client.put_object(
            Bucket=bucket_name,
            Body=fp,
            Key=file_key,
            StorageClass=storage_class,
            EnableMD5=enableMD5,
        )
        return response



list_region=[
    'ap-beijing',
    'ap-nanjing',
    'ap-shanghai',
    'ap-guangzhou',
    'ap-chendu',
    'ap-chongqing',
]
cos_client_chengdu=CosTencent('ap-chengdu')
# flag,response,bucket_name=cos_client_chengdu.create_bucket()
##for some tencent stupid namning rules, you can't have some so called illegal characters
##in the name, you can only name the bucket with digit,letter and hythen.
## so I can't include my project name in the bucket name, I have to find other methods. like
##uuid+ app_id
# if flag:
#     print('bucket created successfully')
#     print('And your bucket name is:{}'.format(bucket_name))
# else:
#     print('something wrong')
#     print(response)
#if the bucket was created successfully, then response is None
#but if something wrong, the response is a directory with specified keys, like:
#qcloud_cos.cos_exception.CosServiceError:
# {'code': 'BucketAlreadyOwnedByYou',
# 'message': 'Your previous request to create the named bucket succeeded and you already own it.',
# 'resource': '/', 'requestid': 'NjNiZWM1ZmJfNzc5ZTU4NjRfNmJmM180Y2U0MjBl',
# 'traceid': 'OGVmYzZiMmQzYjA2OWNhODk0NTRkMTBiOWVmMDAxODczNTBmNjMwZmQ0MTZkMjg0NjlkNTYyNmY4ZTRkZTk0NzAyMWIzNDJjY2Y0MTI4NWQyZTNjZjk5YzE1OGRhMDZkNDM4MDI0YTJhYmYxN2JlM2NjMGQ2M2ZkOWIzYTkwYzY='}

##test response of method put_object
import sys,os


# with open(r'C:\Users\HP\Desktop\test.txt','rb') as fp:
#     response = cos_client_chengdu.put_object(
#         bucket_name='f0a40b3c6fba48cfb6c39e64365241da-1313950337',
#         key=uuid.uuid4().hex,
#         fp=fp
#     )
# print(response)
# from urllib.parse import quote
# str=file_key=uuid.uuid4().hex
# file_key_prop='https://f0a40b3c6fba48cfb6c39e64365241da-1313950337.cos.ap-chengdu.mycloud.com/'+str
# print(quote(file_key_prop))
print(len('https%3A//f0a40b3c6fba48cfb6c39e64365241da-1313950337.cos.ap-chengdu.mycloud.com/512d752fc9c44d4ba1062e1abb571d6d'))
# path='认识实习动员大会.docx'
# res=os.path.splitext(path)
# print(res[1])
