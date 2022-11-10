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

class SigninForm(forms.Form):
    username=forms.CharField(
        label='Username',
        initial='nwu_',
        widget=widgets.TextInput(attrs={'class':'form-control'}),
        validators=[query_username,]
    )
    password = forms.CharField(
        label='Password',
        widget=widgets.PasswordInput(attrs={'class': 'form-control'})

    )

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

