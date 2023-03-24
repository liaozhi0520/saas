from django.views import View
from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
from web.forms.issue import *
from web.models import *
from django.db.models import Q
from django.db.models.query import QuerySet
from django.core.paginator import Paginator
from django.forms.models import model_to_dict
from web.views.account import LoginRequiredMixin

class IssuesView(LoginRequiredMixin,View):
    def get(self,request,*args,**kwargs):
        new_issue_form=NewIssue(request)
        issue_filter_form=IssueFilter(request)
        rendering_context={
            'request': request,
            'new_issue_form': new_issue_form,
            'issue_filter_form':issue_filter_form
        }
        return render(request, r'web/issues.html', context=rendering_context)

    def post(self,request,*args,**kwargs):
        new_issue=NewIssue(request=request,data=request.POST)
        if new_issue.is_valid():
            cleaned_data=new_issue.cleaned_data
            manager=UserInfo.objects.filter(id=cleaned_data.get('issue_manager')).first()
            issue=Issue.objects.create(
                title=cleaned_data.get('title'),
                description=cleaned_data.get('description'),
                type=cleaned_data.get('type'),
                creator=request.user,
                manager=manager,
                status='1',
                priviledge=cleaned_data.get('priviledge'),
                deadline_time=cleaned_data.get('deadline_time'),
                project=request.tracer.project
            )
            if issue:
                members_id=cleaned_data.get('issue_members')
                members=[]
                for member_id in members_id:
                    members.append(IssueMember(issue=issue,member=UserInfo.objects.filter(id=member_id).first(),
                                               relation='3',operator=request.user))
                members.append(IssueMember(issue=issue,member=request.user,relation='1',operator=request.user))
                members.append(IssueMember(issue=issue,member=manager,relation='2',operator=request.user))
                IssueMember.objects.bulk_create(members)
            response={
                'flag':True,
                'content':'create the issue successfully'
            }
        else:
            response={
                'flag':False,
                'content':{
                    'validation_res':new_issue.errors
                }
            }
        return JsonResponse(response,safe=False)

class IssueListView(LoginRequiredMixin,View):
    def post(self,request,*args,**kwargs):
        page_number=request.GET.get('page')
        issue_filter=IssueFilter(request=request,data=request.POST)
        if issue_filter.is_valid():
            cleaned_data=issue_filter.cleaned_data
            issue_list_objs = None
            q = Q()
            q.connector = 'or'
            if cleaned_data.get('issue_members'):
                for member_id in cleaned_data.get('issue_members'):
                    q.children.append(('member__id',member_id))
                issue_members=IssueMember.objects.filter(q).all()
                for issue_member in issue_members:
                    issue_list_objs.append(issue_member.issue)
            if cleaned_data.get('issue_creator'):
                q.children.clear()
                for creator_id in cleaned_data.get('issue_creators'):
                    q.children.append(('creator__id',creator_id))
                if not issue_list_objs:
                    issue_list_objs=Issue.objects.filter(q).all()
                else:
                    issue_list_objs=issue_list_objs.filter(q).all()
            if cleaned_data.get('issue_managers'):
                q.children.clear()
                for manager_id in cleaned_data.get('issue_managers'):
                    q.children.append(('manager__id',manager_id))
                if not issue_list_objs:
                    issue_list_objs=Issue.objects.filter(q).all()
                else:
                    issue_list_objs=issue_list_objs.filter(q).all()
            if cleaned_data.get('type'):
                if not issue_list_objs:
                    issue_list_objs=Issue.objects.filter(type=cleaned_data.get('type')).all()
                else:
                    issue_list_objs=issue_list_objs.filter(type=cleaned_data.get('type')).all()
            if cleaned_data.get('proviledge'):
                if not issue_list_objs:
                    issue_list_objs=Issue.objects.filter(priviledge=cleaned_data.get('proviledge')).all()
                else:
                    issue_list_objs=issue_list_objs.filter(type=cleaned_data.get('proviledge')).all()
            sort=cleaned_data.get('sort')
            if issue_list_objs:
                if sort[0] == 'creating_time':
                    if len(sort) > 1 and sort[1] == 'ascending':
                        issue_list_objs.order_by('creating_time')
                    else:
                        issue_list_objs.order_by('-creating_time')
                else:
                    if len(sort) > 1 and sort[1] == 'ascending':
                        issue_list_objs.order_by('last_updated_time')
                    else:
                        issue_list_objs.order_by('-last_updated_time')
            else:
                issue_list_objs=Issue.objects.filter(project=request.tracer.project).all()
                if sort[0] == 'creating_time':
                    if len(sort) > 1 and sort[1] == 'ascending':
                        issue_list_objs.order_by('creating_time')
                    else:
                        issue_list_objs.order_by('-creating_time')
                else:
                    if len(sort) > 1 and sort[1] == 'ascending':
                        issue_list_objs=Issue.objects.all().order_by('last_updated_time')
                    else:
                        issue_list_objs = Issue.objects.all().order_by('-last_updated_time')
            ## now I have the issue_list_objects, next I need to paginate the issue_list_objects
            paginator=Paginator(issue_list_objs,6)
            try:
                page = paginator.page(page_number)
                object_list=page.object_list.values('id','title','type','creator__username','manager__username','status','priviledge','creating_time','last_updated_time')
                for obj in object_list:
                    updated_dict={'creating_time':obj['creating_time'].strftime('%Y-%m-%d %H:%M'),
                                    'last_updated_time': obj['last_updated_time'].strftime('%Y-%m-%d %H:%M')}
                    obj.update(updated_dict)
                response = {
                    'flag': True,
                    'content': {
                        'object_list':list(object_list),
                        'has_previous':page.has_previous(),
                        'previous_page_num':page.previous_page_number() if page.has_previous() else None,
                        'has_next':page.has_next(),
                        'next_page_num':page.next_page_number() if page.has_next() else None,
                        'num_pages':paginator.num_pages
                    }
                }
                return JsonResponse(response)
            except Exception as e:
                return JsonResponse('something for pagination went wrong. But don not fret. It was not your fault',status=500)
        else:
            response = {
                'flag': False,
                'content': {
                    'validation_res':issue_filter.errors
                }
            }
            return JsonResponse(response,safe=False)

class IssueDetailsView(LoginRequiredMixin,View):
    def get(self,request,*args,**kwargs):
        issue=request.tracer.issue
        current_issue_data_for_issue_details_displaying={
            'title':issue.title,
            'manager__username':issue.manager.username,
            'creator__username':issue.creator.username,
            'creating_time':issue.creating_time.strftime('%Y-%m-%d %H:%M'),
            'status':issue.status,
            'priviledge':issue.priviledge,
            'type':issue.type,
            'last_updated_time':issue.last_updated_time.strftime('%Y-%m-%d %H:%M'),
            'members':[member_username[0] for member_username in
                             IssueMember.objects.filter(issue=issue,relation='3').values_list('member__username')],
            'description':issue.description,
        }
        current_issue_data_for_updating_form={
            'title':issue.title,
            'description':issue.description,
            'type':issue.type,
            'priviledge':issue.priviledge,
            'issue_manager':issue.manager.id,
            'issue_members':[member_id_tuple[0] for member_id_tuple in
                       IssueMember.objects.filter(issue=issue,relation='3').values_list('member')],
            'deadline_time':issue.deadline_time.strftime('%Y-%m-%dT%H:%M')
        }
        update_issue_details_form=updateIssueDetailForm(request,data=current_issue_data_for_updating_form)
        context={
            'request':request,
            'update_issue_details_form':update_issue_details_form,
            'issue_details':current_issue_data_for_issue_details_displaying
        }
        return render(request,r'web/issue_detail.html',context=context)

class IssueDetailsUpdateView(LoginRequiredMixin,View):
    def post(self,request,*args,**kwargs):
        if request.user!=request.tracer.issue.creator or request.user!=request.tracer.issue.manager:
            response={
                'flag':False,
                'content':'only the creator or the manager can update details of issue'
            }
            return JsonResponse(response)
        update_issue_details_form=updateIssueDetailForm(request,data=request.POST)
        if update_issue_details_form.is_valid():
            cleaned_data=update_issue_details_form.cleaned_data
            Issue.objects.filter(id=request.tracer.issue.id).update(
                title=cleaned_data.get('title'),
                description=cleaned_data.get('description'),
                type=cleaned_data.get('type'),
                priviledge=cleaned_data.get('priviledge'),
                manager=UserInfo.objects.filter(id=cleaned_data.get('issue_manager')).first(),
                deadline_time=cleaned_data.get('deadline_time')
            )
            if cleaned_data.get('manager_being_altered',None):
                IssueMember.objects.filter(issue=request.tracer.issue,relation='2').update(
                    member=UserInfo.objects.filter(id=cleaned_data.get('issue_manager')).first()
                )
            if cleaned_data.get('members_being_altered',None):
                original_members=cleaned_data.get('original_members')
                altered_members=cleaned_data.get('issue_members')
                for original_member in original_members:
                    if original_member not in altered_members:
                        IssueMember.objects.filter(issue=request.tracer.issue,member__id=original_member).delete()
                for altered_member in altered_members:
                    if altered_member not in original_members:
                        IssueMember.objects.create(
                            issue=request.tracer.issue,
                            member=UserInfo.objects.filter(id=altered_member).first(),
                            relation='3',
                            operator=request.user
                        )
            response={
                'flag':True,
                'content':'Update issue details successfully.'
            }
        else:
            response={
                'flag':False,
                'content':update_issue_details_form.errors
            }
        return JsonResponse(response,safe=False)

class IssueDetailsDeleteView(LoginRequiredMixin,View):
    def get(self,request,*args,**kwargs):
        if request.user!=request.tracer.issue.creator:
            response={
                'flag':False,
                'content':"If you aren't creator of this issue, you have no permission to procceed this deletion."
            }
            return JsonResponse(response)
        else:
            Issue.objects.filter(id=request.tracer.issue.id).delete()
            response = {
                'flag': True,
                'content': "You have already deleted this issue."
            }
            return JsonResponse(response)