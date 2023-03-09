import datetime
import os.path
import re
import time
from saas.settings import MEDIA_ROOT
from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from django.views import View
from web.forms.account import *
from web.models import UserInfo,ValidationPhone
from utils.sms import SendSm
import random
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from web.models import Transaction,PricePolicy
import uuid

class LoginRequiredMixin(object):
    @method_decorator(login_required)
    #wrap the method dispatch a decorator
    def dispatch(self,request,*args,**kwargs):
        return super(LoginRequiredMixin, self).dispatch(request,*args,**kwargs)

# Create your views here.
class RegistrationView(View):
    def get(self,request,*args,**kwargs):
        register_form=RegisterForm()
        return render(request, r'web/registration.html', {'register_form':register_form})

    def post(self,request,*args,**kwargs):
        #both frontend and the backend valid the username to be unique and
        #the correctivity of code from sms.But the core is the same,just do it twice,
        #because for the a better UE
        register_form=RegisterForm(request.POST)
        #request.POST and request.FILES are both dicts and pass them to the formclass to get
        #an instance,and result of calling instance.cleaned_data() is get a dict
        #and the cleaned_data always be passed to model.objects.create() and create a new
        #entry of the database.The instance have the rendering function and validation function.
        if register_form.is_valid():
            cleaned_data=register_form.cleaned_data  #form.cleaed_data is a dict
            cleaned_data.pop('code')
            #cleaned_data is a dict.
            profile=UserInfo.objects.create_user(**cleaned_data)
            profile.save()
            pri_pol=PricePolicy.objects.filter(id=1).first()
            Transaction.objects.create(user=profile,status=1,order_num=uuid.uuid4().hex,
                                       price_policy=pri_pol,num_pri_pol=0,
                                       amount_trans=0,end_time=None)
            return redirect('web:login')
        else:
            context={
                'register_form':register_form,
                'valid_state':{}  #the valid_state is for the app01 class in the templates
            }
            #print(register_form.fields.get('username').error_messages)
            #that demonstrate the error info from the validators dosn't come from the
            #form.fields.get('field_name').error_messages
            for field in register_form.fields.keys():
                context['valid_state'][field]=''
                if field in register_form.errors.keys():
                    context['valid_state'][field] = 'has-error'
            return render(request, r'web/registration', context)

class ValidationUsernameView(View):
    def post(self, request, *args, **kwargs):
        username=request.POST.get('username')
        res=UserInfo.objects.filter(username=username).count()
        if res:
            validation_res='The username is not available'
            return HttpResponse(validation_res)
        else:
            validation_res='The username is available'
            return HttpResponse(validation_res)

class ValidationPhoneView(View):
    def post(self, request, *args, **kwargs):
        phone=request.POST.get('phone')
        pattern=re.compile(r'\d{11}')
        validation_res={}
        if not pattern.match(phone):
            validation_res['status']=False
            validation_res['msg']='The format of the phone is incorrect.'
            return JsonResponse(validation_res)
        res=UserInfo.objects.filter(phone=phone).count()
        if res:
            validation_res['status'] = False
            validation_res['msg'] = 'The format of the phone is incorrect'
            return JsonResponse(validation_res)
        else:
            tpl = request.POST.get('tpl')
            sendsm = SendSm(template_id=tpl)
            code = str(random.randint(100000, 1000000))
            # 这里的expired_time应该使用timestamp or strformattime or struccttime
            #resp=sendsm.send_single_sm(phone_number=["+86{}".format(phone),], template_para_set=[code,])
            if  True:#resp.SendStatusSet[0].Code=='Ok':
                import datetime
                exp_time=datetime.datetime.now()+datetime.timedelta(minutes=5)
                #A datetimefield in a model would be a date and a time,represented a datetime.datetime instance in Python
                #So,you need to pass a datetime.datetime instance to the exp_time when creating an entry
                #Note that an instance generated from  datetime.datetime.now() will exclude the timezone info,but
                #when you storage the datetime in the mysql database,it will add the default timezone(set by mysql) info to the value
                #so when you take it back from the database,you will get a datetime.datetime instance with a tzinfo,
                #if you want it be None,call the datetime.datetime.replace(tzinfo=None)
                code = ValidationPhone.objects.create(phone=phone, code=code, exp_time=exp_time)
                validation_res['status'] = True
                validation_res['msg'] = 'Validation code already being sent,and expires in 5 minutes'
                return JsonResponse(validation_res)
            else:
                validation_res['status']=False
                validation_res['msg']=resp.SendStatusSet[0].Message
                return JsonResponse(validation_res)

class LoginView(View):
    def get(self,request,*args,**kwargs):
        login_form=LoginForm(request)
        return render(request,r'web/login.html',context={'login_form':login_form})

    def post(self,request,*args,**kwargs):
        login_form=LoginForm(request,data=request.POST)
        if login_form.is_valid():
            return redirect('web:index')
        else:
            return render(request,r'web/login.html',{'login_form':login_form})

class GrapCheckCodeView(View):
    def get(self,request,*args,**kwargs):
        #choose a random pic from dist,Do I just return the bytes of the pic?
        #yes,I am right
        from io import BytesIO
        from utils.check_code.check_code import gen_check_code
        stream=BytesIO()
        code,img=gen_check_code()
        img.save(stream,'png')
        request.session['grap_check_code']=code
        return HttpResponse(stream.getvalue())

class TestView(View):
    def get(self,request,*args,**kwargs):
        return render(request,r'web/test_extends.html')
    def post(self,request):
        print(request.FILES)
        return HttpResponse('all done')

class IndexView(View):
    def get(self,request,*args,**kwargs):
        return render(request,r'web/index.html',{'requset':request})

class ResetPwdView(LoginRequiredMixin,View):
    def get(self,request,*args,**kwargs):
        reset_pwd_form=ResetPwdForm(request)
        return render(request,r'web/reset_pwd.html',{'form':reset_pwd_form})

    def post(self,request,*args,**kwargs):
        reset_pwd_form=ResetPwdForm(request,data=request.POST)
        if reset_pwd_form.is_valid():
            user=reset_pwd_form.cleaned_data.get('old_pwd')
            user.set_password(reset_pwd_form.cleaned_data.get('new_pwd'))
            user.save()
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request,user)
            return redirect('web:index')

        else:
            return render(request,r'web/reset_pwd.html',{'form':reset_pwd_form})



class VerifyOldPwdView(LoginRequiredMixin,View):
    def post(self,request,*args,**kwargs):
        old_pwd = request.POST.get('old_pwd').strip()
        username = request.user.username
        from web.models import UserInfo
        user = UserInfo.objects.filter(username=username).first()
        res={}
        if user.check_password(raw_password=old_pwd):
            res['flag']=True
            res['msg']='old password correct'
        else:
            res['flag'] = False
            res['msg'] = 'old password incorrect'
        return JsonResponse(res)

class LogoutView(LoginRequiredMixin,View):
    def get(self,request,*args,**kwargs):
        logout(request)
        return redirect('web:index')

