from django import forms
from django.forms import widgets
from django.core.exceptions import ValidationError
from web.models import Issue,ProjectUser,IssueMember

class SelectCanSetAttributesToSingleOption(widgets.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option=super(SelectCanSetAttributesToSingleOption, self).create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        if index==0:
            option['attrs'].update({'disabled':True})
        return option

class NewIssue(forms.Form):
    TYPE_CHOICES=(
        ('1','assignment'),
        ('2','bug'),
        ('3','feature discussing')
    )
    PRIVILEDGE_CHOICES=(
        ('1','Low'),
        ('2','Medium'),
        ('3','High'),
        ('4','Premium')
    )
    title=forms.CharField(
        label='Title',
        widget=widgets.TextInput(attrs={
            'class':'form-control',
            'placeholder':'Make a title for your issue'
        }),
        max_length=60,
    )
    description=forms.CharField(
        label='Description',
        widget=widgets.Textarea(attrs={
            'class':'form-control',
            'rows':3,
            'placeholder':'Please describe your issue'
        }),
        max_length=160
    )
    type=forms.ChoiceField(
        choices=TYPE_CHOICES,
        label='Type',
        widget=forms.Select(
            attrs={
                'class':'form-control selectpicker'
            }
        )
    )
    priviledge = forms.ChoiceField(
        choices=PRIVILEDGE_CHOICES,
        label='Priviledge',
        widget=forms.Select(
            attrs={
                'class': 'form-control selectpicker'
            }
        ),
        initial='2'
    )
    deadline_time=forms.DateTimeField(
        label='Deadline',
        widget=forms.DateTimeInput(
            attrs={
                'type':'datetime-local',
                'class':'form-control',
            }
        ),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    def __init__(self,request,*args,**kwargs):
        super(NewIssue, self).__init__(*args,**kwargs)
        issue_creator_or_manager_or_members_choices = [('', '---select someone you like---')]
        users_list = ProjectUser.objects.filter(project=request.tracer.project,).values_list('user__id','user__username')
        issue_creator_or_manager_or_members_choices.extend(users_list)
        self.request=request
        self.fields['issue_manager']=forms.ChoiceField(
        choices=issue_creator_or_manager_or_members_choices,
        label='Manager',
        widget=widgets.Select(attrs={
            'class':'form-control selectpicker',
            'data-live-search':'true'
        })
    )
        self.fields['issue_members']=forms.MultipleChoiceField(
        choices=issue_creator_or_manager_or_members_choices,
        label='Members',
        widget=widgets.SelectMultiple(attrs={
            'class': 'form-control selectpicker',
            'data-live-search':'true'
        })
    )


    def clean_title(self):
        title=self.cleaned_data.get('title').strip()
        issues_title_of_project=Issue.objects.filter(project=self.request.tracer.project).all().values_list('title')
        if (title,) in issues_title_of_project:
            raise ValidationError('the title is duplicated in this project')
        return title

    def clean_members(self):
        manager=self.cleaned_data.get('manager')
        members=self.cleaned_data.get('issue_members')
        if manager in members:
            raise("You cannot select manager in the members.Please remove him/her")
        return members


class IssueFilter(forms.Form):
    TYPE_CHOICES=(
        ('','--select a type--'),
        ('1','Assignment'),
        ('2','Bug'),
        ('3','Feature Discussing')
    )
    PRIVILEDGE_CHOICES=(
        ('','--select a priviledge--'),
        ('1','Low'),
        ('2','Medium'),
        ('3','High'),
        ('4','Premium')
    )
    sort=forms.MultipleChoiceField(
        choices=(
            ('Time',(('creating_time','Creating Time'),('last_updatimg_time','UpdatingTime'))),
            ('Order',(('descending','Descending'),('ascending','Ascending')))
        ),
        label='Sort',
        widget=widgets.SelectMultiple(attrs={
            'class':'selectpicker form-control'
        }),
        initial=['creating_time','descending']
    )
    type=forms.ChoiceField(
        choices=TYPE_CHOICES,
        label='Type',
        widget=SelectCanSetAttributesToSingleOption(
            attrs={
                'class':'form-control selectpicker'
            }
        ),
        required=False
    )
    priviledge=forms.ChoiceField(
        choices=PRIVILEDGE_CHOICES,
        label='Priviledge',
        widget=SelectCanSetAttributesToSingleOption(attrs={
            'class':'form-control selectpicker'
        }),
        required=False
    )
    def __init__(self,request,*args,**kwargs):
        super(IssueFilter, self).__init__(*args,**kwargs)
        issue_creator_or_manager_or_members_choices=ProjectUser.objects.filter(project=request.tracer.project).values_list('user__id', 'user__username')
        self.fields['issue_creators']=forms.MultipleChoiceField(
            choices=issue_creator_or_manager_or_members_choices,
            label='Creators',
            widget=widgets.SelectMultiple(attrs={
                'class':'form-control selectpicker',
                'data-live-search':'true',
            }),
            required=False
        )
        self.fields['issue_managers']=forms.MultipleChoiceField(
            choices=issue_creator_or_manager_or_members_choices,
            label='Managers',
            widget=widgets.SelectMultiple(attrs={
                'class': 'form-control selectpicker',
                'data-live-search': 'true',
            }),
            required=False

        )
        self.fields['issue_members']=forms.MultipleChoiceField(
            choices=issue_creator_or_manager_or_members_choices,
            label='Members',
            widget=widgets.SelectMultiple(attrs={
                'class': 'form-control selectpicker',
                'data-live-search': 'true',
            }),
            required=False
        )
    def clean_sort(self):
        sort_data=self.cleaned_data.get('sort')
        if ('creating_time' in sort_data and 'last_updating_time' in sort_data) or (
            'ascending' in sort_data and 'descending' in sort_data
        ):
            raise ValidationError('The can not select both time options or orser options')
        return sort_data


class updateIssueDetailForm(NewIssue):
    def __init__(self,request,*args,**kwargs):
        super(updateIssueDetailForm, self).__init__(request,*args,**kwargs)
    def clean_title(self):
        title = self.cleaned_data.get('title')
        issue=Issue.objects.filter(project=self.request.tracer.project,title=title).first()
        if issue and issue!=self.request.tracer.issue:
            raise ValidationError('The title of issue is duplicated in current project')
        return title
    def clean_issue_manager(self):
        manager=self.cleaned_data.get('issue_manager')
        if manager!=self.request.tracer.issue.manager.id:
            self.cleaned_data['manager_being_altered']=True
        return manager
    def clean_issue_members(self):
        members=self.cleaned_data.get('issue_members')
        original_members=[member_id_tuple[0] for member_id_tuple in
                       IssueMember.objects.filter(issue=self.request.tracer.issue,relation='3').values_list('member')]
        if members!=original_members:
            self.cleaned_data['members_being_altered']=False
            self.cleaned_data['original_members']=original_members
        return members