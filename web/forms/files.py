from django import forms
from django.forms import widgets
from django.core.exceptions import ValidationError
from web.models import File

class NewFolder(forms.Form):

    parent_folder_id=forms.IntegerField(
        widget=widgets.HiddenInput(
        )
    )
    foldername=forms.CharField(
        label='New Folder Name',
        widget=widgets.TextInput(
            attrs={
                'class':'form-control',
                'placeholder':'Folder Name'
            }
        ),
        max_length=64
    )
    def __init__(self,request,*args,**kwargs):
        super(NewFolder, self).__init__(args,kwargs)
        self.request=request

    def clean_foldername(self):
        parent_folder_id=self.cleaned_data.get('parent_folder_id')
        foldername=self.cleaned_data.get('foldername')
        subfolder_name_list=File.objects.filter(
            id=parent_folder_id
        ).first().subfiles.filter(file_type=2).values_list('name')
        if (foldername,) in subfolder_name_list:
            raise ValidationError('the foldername is duplicated in the parent folder')
        return foldername
