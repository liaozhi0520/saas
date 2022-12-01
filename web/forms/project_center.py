from django import forms
from django.forms import widgets
from django.core.exceptions import ValidationError


class NewProjForm(forms.Form):
    name=forms.CharField(
        max_length=20,
        label='Name',
        widget=widgets.TextInput(attrs={'class':'form-control','placeholder':'input the name of new project'})
    )
    from web.forms.mywidgets.color_proj import ColorWidget
    color=forms.ChoiceField(
        choices=(
            ("#56b8eb",''),
            ("#f28033",''),
            ("#ebc656",''),
            ("#a2d148",''),
            ("#20BFA4",''),
            ("#7461c2",''),
            ("#20bfa3",''),
        ),
        label='Color',
        widget=widgets.RadioSelect(attrs={'class':'sr-only'})
    )
    description=forms.CharField(
        label='Description for your new project',
        widget=widgets.Textarea(
            attrs={'class': 'form-control', 'placeholder': 'input the name of new project(max length equals 100 characters)',
                   'rows':3}
        ),
        max_length=100
    )
    def __init__(self,request,*args,**kwargs):
        super(NewProjForm, self).__init__(*args,**kwargs)
        self.request=request

    def clean_name(self):
        #the name have to be unique among the user's projects
        from web.models import UserInfo,ProjectUser
        name=self.cleaned_data.get('name').strip()
        user=UserInfo.objects.filter(username=self.request.user.username).first()
        pro_name_list=ProjectUser.objects.filter(user=user).values_list('project__name')
        for pro_name in pro_name_list:
            if pro_name[0] == name:
                raise ValidationError('"{}" already being used in your projects'.format(name))
        return {'user':user,'name':name}

    def clean_color(self):
        color=self.cleaned_data.get('color').strip()
        color_choices=(
            "#56b8eb",
            "#f28033",
            "#ebc656",
            "#a2d148",
            "#20BFA4",
            "#7461c2",
            "#20bfa3",
        )
        if color not in color_choices:
            raise ValidationError('You may modify the color value by the dev tool, We are really apprrciating that you make them original.')
        return color

    def clean_description(self):
        desc=self.cleaned_data.get('description').strip()
        #In some time, you may want to add a sensitive words filter here
        return desc


        