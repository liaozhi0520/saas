from django import forms
from django.forms import widgets



class NewProjForm(forms.Form):
    name=forms.CharField(
        label='Name',
        widget=widgets.TextInput(attrs={'class':'form-control','placeholder':'input the name of new project'})
    )
    color=forms.ChoiceField(
        choices=(
            ("#56b8eb",'a'),
            ("#f28033",'b'),
            ("#ebc656",'c'),
            ("#a2d148",'d'),
            ("#20BFA4",'e'),
            ("#7461c2",'f'),
            ("#20bfa3",'g'),
        ),
        label='Color',
        widget=widgets.RadioSelect()
    )
    description=forms.CharField(
        label='Description for your new project',
        widget=widgets.Textarea(
            attrs={'class': 'form-control', 'placeholder': 'input the name of new project(max length equals 100 characters)',
                   'rows':3}
        ),
        max_length=100
    )
