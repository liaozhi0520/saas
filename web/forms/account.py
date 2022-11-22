from django import forms
from django.core.exceptions import ValidationError
from django.forms import widgets
from django.core.validators import RegexValidator
from web.models import ValidationPhone
from web.models import UserInfo

# class RegisterModelForm(ModelForm):
#     class Meta:
#         model=UserInfo
#         fields=['username','password','gender','province','phone','bg_img','avatar']
#         labels={
#             'username':'Username',
#             'password':'Password',
#             'gender':'Gender',
#             'province':'Province',
#             'phone':'Phone',
#             'bg_img':'Background_Image',
#             'avatar':'Avatar'
#         }
#         #因为不同的字段类型设置存在差异性，如果这样子去批量设置的话，细致性就不够哦
#         #所以，我还是不推荐新手使用这种方法去做一个Form
def validation_username(value):
    import re
    pattern=re.compile(r'nwu_.{1,6}')
    if not pattern.match(value):
        validation_username_res='The username has to start with "nwu_"'
        raise ValidationError(validation_username_res)
    if UserInfo.objects.filter(username=value).count():
        validation_username_res='The username is not available'
        raise ValidationError(validation_username_res)
def validation_code(value):
    import datetime
    query_res=ValidationPhone.objects.filter(code=value).first()
    if not query_res :
        validation_username_res='The code is incorrect'
        raise ValidationError(validation_username_res)
    elif query_res.exp_time.replace(tzinfo=None) < datetime.datetime.now():
        validation_username_res = 'The code is expired'
        raise ValidationError(validation_username_res)

def query_username(value):
    import re
    pattern=re.compile(r'nwu_.{1,6}')
    if not pattern.match(value):
        validation_username_res='The username has to start with "nwu_"'
        raise ValidationError(validation_username_res)
    if not UserInfo.objects.filter(username=value).count():
        validation_username_res='The username is not in our database'
        raise ValidationError(validation_username_res)

class RegisterForm(forms.Form):
    username=forms.CharField(
        max_length=10,
        label='Username',
        initial='nwu_',
        widget=widgets.TextInput(attrs={'class':'form-control'}),
        validators=[validation_username,]
    )
    password = forms.CharField(
        max_length=20,
        label='Password',
        widget=widgets.PasswordInput(render_value=True,attrs={'class':'form-control'}),
    )
    phone=forms.CharField(
        max_length=11,
        label='Phone',
        widget=widgets.TextInput(attrs={'class':'form-control'})
    )
    code=forms.CharField(
        required=False,
        label='Validation_Code',
        widget=widgets.TextInput(attrs={'class':'form-control','placeholder':'Input the 6-digital code'}),
        validators=[validation_code,]
    )
class BootstrapForm(object):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for name,field in self.fields.items():
            field.widget.attrs['class']='form-control'
            field.widget.attrs['placeholder']='input {}'.format(name)

class LoginForm(BootstrapForm,forms.Form):
    credential=forms.CharField(
        label='Phone or Username(start with nwu_)',
        initial='nwu_',
        widget=widgets.TextInput(),
    )
    password = forms.CharField(
        label='Password',
        widget=widgets.PasswordInput()
    )
    check_code=forms.CharField(
        label='Check Code',
        widget=widgets.TextInput()
    )
    def __init__(self,request,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.request=request

    def clean_credential(self):
        credential=self.cleaned_data.get('credential').strip()
        import re
        pattern_phone=re.compile(r'\d{11}')
        pattern_username=re.compile(r'nwu_.{1,6}')
        if  not pattern_phone.match(credential) and  not pattern_username.match(credential):
            raise ValidationError('please input a corrent credential')
        from web.models import UserInfo
        from django.db.models import Q
        user=UserInfo.objects.filter(Q(username=credential) | Q(phone=credential)).first()
        if not user:
            raise ValidationError('Your credential not in our database.Please check it out')
        return user.username

    def clean_check_code(self):
        check_code=self.cleaned_data.get('check_code').strip()
        if check_code.upper()!=self.request.session.get('grap_check_code').upper():
            raise ValidationError('Verification code is incorrect')
        return check_code

    def clean(self):
        username=self.cleaned_data.get('credential')
        if not username:
            return None
        password=self.cleaned_data.get('password')
        from django.contrib.auth import authenticate,login
        user=authenticate(username=username,password=password)
        if user:
            login(self.request,user)
            self.request.session.pop('grap_check_code')
            self.request.session.set_expiry(60 * 60)
        else:
            self.add_error('password','the password is incorrect')


class ResetPasswordForm(forms.Form):
    old_password=forms.CharField(
        max_length=20,
        label='Old_Password',
        widget=widgets.PasswordInput(
            attrs={'class':'form-control'}
        )
    )
    new_password = forms.CharField(
        max_length=20,
        label='New_Password',
        widget=widgets.PasswordInput(
            attrs={'class': 'form-control'}
        )
    )

class ResetPwdForm(BootstrapForm,forms.Form):
    old_pwd=forms.CharField(
        label='Old Password',
        widget=widgets.PasswordInput()
    )
    new_pwd=forms.CharField(
        label='New Password',
        widget=widgets.PasswordInput()
    )
    re_new_pwd = forms.CharField(
        label='New Password Again',
        widget=widgets.PasswordInput()
    )
    def __init__(self,request,*args,**kwargs):
        super(ResetPwdForm, self).__init__(*args,**kwargs)
        self.request=request

    def clean_old_pwd(self):
        old_pwd=self.cleaned_data.get('old_pwd')
        username=self.request.user.username
        from web.models import UserInfo
        user=UserInfo.objects.filter(username=username).first()
        if not user.check_password(raw_password=old_pwd):
            raise ValidationError('old password incorrect')
        return user

    def clean(self):
        old_pwd = self.cleaned_data.get('old_pwd')
        new_pwd = self.cleaned_data.get('new_pwd')
        re_new_pwd = self.cleaned_data.get('re_new_pwd')
        if (old_pwd == new_pwd):
            self.add_error('new_pwd','new password can not repeat the old password')
        if not (new_pwd==re_new_pwd):
            self.add_error('new_pwd',"new passwords don't match")


