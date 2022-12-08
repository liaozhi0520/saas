from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render
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
        projectuser_me_plus_invol=ProjectUser.objects.filter(user=request.tracer.user)
        project_dict={'me':[],'invol':[],'star':[]}
        for projectuser in projectuser_me_plus_invol:
            project=projectuser.project
            project_creator=project.creator
            if project_creator.username==request.tracer.user.username:
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
            user = new_proj_form.cleaned_data.get('name').get('user')
            from web.models import Project
            projects = Project.objects.filter(creator=user)
            proj_num = len(projects)
            if proj_num >request.user.status.proj_num:
                res['flag']=False
                res['msg']={'name':['You have no remain projects',]}
                return JsonResponse(res)
            else:
                from web.models import Project, ProjectUser, UserInfo
                user = new_proj_form.cleaned_data.get('name').get('user')
                name = new_proj_form.cleaned_data.get('name').get('name')
                color = new_proj_form.cleaned_data.get('color')
                desc = new_proj_form.cleaned_data.get('description')
                proj = Project.objects.create(name=name, color=color, description=desc, used_space=0, star=0, creator=user)
                proj_user = ProjectUser.objects.create(user=user, project=proj, star=0)
                res['flag'] = True
                res['msg'] = 'Project have been created.'
                return JsonResponse(res)
        else:
            res['flag']=False
            res['msg']=new_proj_form.errors
            return JsonResponse(res)

#star my project view
class StarMyProjectView(View):
    def post(self,request,*args,**kwargs):
        project_name=request.POST.get('project_name').strip()
        from web.models import Project,ProjectUser,UserInfo
        user=UserInfo.objects.filter(username=request.user.username).first()
        myproject=Project.objects.filter(name=project_name,creator=user).first()
        myprojectuser=ProjectUser.objects.filter(project__creator=user,project__name=project_name).first()
        res={}
        if myproject.star:
            # cancel the star
            res['flag']=True
            res['projectName']=project_name
            myproject.star=0
            myprojectuser.star=0
            myproject.save()
            myprojectuser.save()
        else:
            #star the project
            res['flag'] = False
            res['projectName'] = project_name
            myproject.star = 1
            myprojectuser.star = 1
            myproject.save()
            myprojectuser.save()
        return JsonResponse(res)

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


class WikiView(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        return render(request, r'web/wiki.html', {'request': request})

class FileView(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        return render(request, r'web/file.html', {'request': request})

class SettingView(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        return render(request, r'web/setting.html', {'request': request})
