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
        name = self.cleaned_data.get('name').strip()
        if '_clickStarInvol_' in name:
            raise ValidationError("This is the id of an elemetn in this page, can't use it.")
        from web.models import Project
        user=self.request.user
        if Project.objects.filter(creator=user).first():
                raise ValidationError('"{}" already being used in your projects'.format(name))
        return name

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




class WikiAddForm(forms.Form):
    title=forms.CharField(
        label='Title',
        max_length=20,
        widget=widgets.TextInput(attrs={'class':'form-control','placeholder':'Select a Fancy Name for your Wiki. Max length=20'})
    )
    content=forms.CharField(
        label='Content',
        max_length=3000,
        widget=widgets.Textarea(attrs={'class':'form-control','rows':40,'id':'editor'})
    )
    def __init__(self,request,wiki_view=False,*args,**kwargs):
        super(WikiAddForm, self).__init__(*args,**kwargs)
        self.request=request
        self.wiki_view=wiki_view

    def clean_title(self):
        title=self.cleaned_data.get('title').strip()
        if self.wiki_view:
            return title
        from web.models import Wiki
        if Wiki.objects.filter(project=self.request.tracer.project,title=title):
            raise ValidationError('the title name is duplicated in your project.')
        return title

    def clean_content(self):
        content=self.cleaned_data.get('content').strip()
        return content



        