from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render,redirect
from web.forms.project_center import *
from django.http import JsonResponse,HttpResponse

class LoginRequiredMixin(object):
    @method_decorator(login_required)
    #wrap the method dispatch a decorator
    def dispatch(self,request,*args,**kwargs):
        return super(LoginRequiredMixin, self).dispatch(request,*args,**kwargs)

class ProjectListView(LoginRequiredMixin,View):
    def get(self,request,*args,**kwargs):
        from web.models import Project,ProjectUser
        projectuser_me_plus_invol=ProjectUser.objects.filter(user=request.user)
        project_dict={'me':[],'invol':[],'star':[]}
        for projectuser in projectuser_me_plus_invol:
            project=projectuser.project
            project_creator=project.creator
            if project_creator.username==request.user.username:
                project_dict['me'].append(project)
                if project.star:
                    project_dict['star'].append(project)
            else:
                project.owner=project_creator.username
                project.star_not_creator=projectuser.star
                project_dict['invol'].append(project)
                if project.star_not_creator:
                    project_dict['star'].append(project)
        proj_num=len(project_dict['me'])
        if proj_num<request.tracer.user_status.proj_num:
            crea_allow=True
        else:
            crea_allow=False
        new_proj_form=NewProjForm(request)
        context={
            'form':new_proj_form,
            'crea_allow':crea_allow,
            'projects_set_me':project_dict.get('me'),
            'projects_set_invol': project_dict.get('invol'),
            'projects_set_starred': project_dict.get('star'),
        }
        return render(request,r'web/project_list.html',context)

class CreateProjView(View):
    def post(self,request,*args,**kwargs):
        new_proj_form = NewProjForm(request,request.POST)
        res={}
        if new_proj_form.is_valid():
            from web.models import Project
            projects = Project.objects.filter(creator=request.user)
            proj_num = len(projects)
            if proj_num >request.tracer.user_status.proj_num:
                res['flag']=False
                res['msg']={'name':['You have no remain projects',]}
                return JsonResponse(res)
            else:
                ## now I need to create a bucket for this project
                from utils.cos import cos_client_chengdu
                flag,response,bucket_name=cos_client_chengdu.create_bucket()
                if flag:
                    from web.models import Project, ProjectUser, File
                    name = new_proj_form.cleaned_data.get('name')
                    color = new_proj_form.cleaned_data.get('color')
                    desc = new_proj_form.cleaned_data.get('description')
                    proj = Project.objects.create(name=name, color=color, description=desc, used_space=0, star=0, creator=request.user,bucket_name=bucket_name)
                    proj_user = ProjectUser.objects.create(user=request.user, project=proj, star=0)
                    ##create a root folder for each newly-created project
                    file=File.objects.create(
                        project=proj,
                        parent_file=None,
                        name='root',
                        file_size=0,
                        file_key=None,
                        file_type=2,
                        file_ext=None,
                        creator=request.user
                    )
                    res['flag'] = True
                    res['msg'] = 'Project have been created.'
                    return JsonResponse(res)
                else:
                    res['flag']=False
                    print(response)
                    res['msg']='False'
                    return JsonResponse(res)

#star my project view
class StarMyProjectView(View):
    def post(self,request,*args,**kwargs):
        project_name=request.POST.get('project_name').strip()
        from web.models import Project,ProjectUser
        myproject=Project.objects.filter(name=project_name,creator=request.user).first()
        myprojectuser=ProjectUser.objects.filter(project__creator=request.user,project__name=project_name).first()
        res={}
        if myproject:
            if myproject.star:
                # cancel the star
                res['flag'] = True
                res['projectName'] = project_name
                myproject.star = 0
                myprojectuser.star = 0
                myproject.save()
                myprojectuser.save()
            else:
                # star the project
                res['flag'] = False
                res['projectName'] = project_name
                myproject.star = 1
                myprojectuser.star = 1
                myproject.save()
                myprojectuser.save()
            return JsonResponse(res)
        else:
            res['flag'] = False
            res['projectName'] = project_name+'is not existing.'

#star others' proejects view
class StarInvolProjectView(View):
    def post(self, request, *args, **kwargs):
        res = {}
        try:
            project_owner = request.POST.get('project_owner')
            project_name = request.POST.get('project_name')
            from web.models import ProjectUser, UserInfo, Project
            user = UserInfo.objects.filter(username=request.user.username).first()
            projectuser = ProjectUser.objects.filter(project__name=project_name,
                                                     project__creator__username=project_owner, user=user).first()
        except Exception:
            res['flag']=False
            return JsonResponse(res)
        res['projectName'] = project_name
        res['projectOwner'] = project_owner
        if projectuser.star:
            res['flag']=True
            projectuser.star=0
            projectuser.save()
        else:
            res['flag']=False
            projectuser.star = 1
            projectuser.save()
        return JsonResponse(res)

class DashboardView(LoginRequiredMixin,View):
    def get(self,request,*args,**kwargs):
        return render(request,r'web/dashboard.html',{'request':request})


class IssuesView(LoginRequiredMixin,View):
    def get(self,request,*args,**kwargs):
        return render(request,r'web/issues.html',{'request':request})

class StatisticsView(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        return render(request, r'web/statistics.html', {'request': request})


class SettingView(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        return render(request, r'web/setting.html', {'request': request})

class WikiView(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        return render(request, r'web/wiki.html', {'request': request})

class WikiTreeView(View):
    def get(self,request,*args,**kwargs):
        from web.models import Wiki
        project = request.tracer.project
        wikis = Wiki.objects.filter(project=project).order_by('id').values('category', 'id', 'title', 'pwiki__id')
        res={}
        res['flag']=True
        res['wikiTree']=list(wikis)
        return JsonResponse(res)

class WikiAddView(View):
    def get(self,request,*args,**kwargs):
        wiki_group=kwargs.get('wiki_group')
        wiki_id=kwargs.get('wiki_id')
        wiki_add_bool=True
        new_wiki_form=WikiAddForm(request)
        context={
            'request': request,
            'wiki_group':wiki_group,
            'wiki_id':wiki_id,
            'wiki_add_bool':wiki_add_bool,
            'new_wiki_form':new_wiki_form,
        }
        return render(request,r'web/wiki.html',context=context)

    def post(self,request,*args,**kwargs):
        wiki_group = kwargs.get('wiki_group')
        wiki_id = kwargs.get('wiki_id')
        print(request.POST)
        new_wiki_form=WikiAddForm(request,data=request.POST)
        if new_wiki_form.is_valid():
            cleaned_data=new_wiki_form.cleaned_data
            from web.models import Wiki
            pwiki=Wiki.objects.filter(project=request.tracer.project,id=wiki_id).first()
            wiki={
                'title':cleaned_data.get('title'),
                'content':cleaned_data.get('content'),
                'project':request.tracer.project,
                'category': 'P' if wiki_group=='public-wiki' else 'I',
                'creator': request.tracer.user,
                'pwiki': pwiki
            }
            Wiki.objects.create(**wiki)
            return redirect('web:wiki',project_id=request.tracer.project.id)
        else:
            wiki_add_bool = True
            context = {
                'request': request,
                'wiki_group': wiki_group,
                'wiki_id': wiki_id,
                'wiki_add_bool': wiki_add_bool,
                'new_wiki_form': new_wiki_form,
            }
            return render(request,r'web/wiki.html',context=context)

class WikiContentView(View):
    def get(self,request,*args,**kwargs):
        wiki_id=kwargs.get('wiki_id')
        from web.models import Wiki
        wiki_obj=Wiki.objects.filter(project=request.tracer.project,id=wiki_id).first()
        if wiki_obj:
            wiki_view_bool=True
            data={
                'title':wiki_obj.title,
                "content":wiki_obj.content
            }
            wiki_form=WikiAddForm(request,wiki_view=True,data=data)
            #when I access to the errors of the wiki_form in the DTL,it will call the clean-related method
            context={
                'wiki_view_bool':wiki_view_bool,
                'wiki_form':wiki_form,
                'wiki_id':wiki_obj.id
            }
            return render(request,r'web/wiki.html',context)

class WikiUpdateView(View):
    def post(self,request,*args,**kwargs):
        wiki_id=kwargs.get('wiki_id')
        wiki_update_form=WikiAddForm(request,request.POST)
        if wiki_update_form.is_valid():
            from web.models import Wiki
            wiki_obj=Wiki.objects.filter(project=request.tracer.project,id=wiki_id).first()
            wiki_obj.title=wiki_update_form.cleaned_data.get('title')
            wiki_obj.content=wiki_update_form.cleaned_data.get('content')
            wiki_obj.save()
            return redirect('web:wiki',project_id=request.project.id)
        else:
            context = {
                'wiki_view_bool': True,
                'wiki_form': wiki_update_form,
                'wiki_id': wiki_id
            }
            return render(request,r'web/wiki.html',context=context)




