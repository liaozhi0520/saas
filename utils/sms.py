from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.sms.v20210111 import sms_client, models

class SendSm():
    def __init__(self,template_id):
        try:
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(__file__)))
            from saas import local_settings
        except Exception as e:
            print(e)
            print('缺少secret_id and secret_key 参数')
        self.secret_id=local_settings.secret_id
        self.secret_key=local_settings.secret_key
        self.SmsSdkAppId = local_settings.sms_sdk_app_id
        self.region = 'ap-beijing'
        self.SignName='DM个人公众号'
        self.cred=credential.Credential(self.secret_id,self.secret_key)
        self.client=sms_client.SmsClient(self.cred,self.region)
        self.req=models.SendSmsRequest()
        self.req.SmsSdkAppId=self.SmsSdkAppId
        self.req.SignName=self.SignName
        self.req.TemplateId=template_id

    def send_single_sm(self,phone_number,template_para_set):
        self.req.PhoneNumberSet=phone_number
        self.req.TemplateParamSet=template_para_set
        resp=self.client.SendSms(self.req)
        return resp

