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
        from web.models import UserInfo,Project,ProjectUser
        user=UserInfo.objects.filter(username=request.user.username).first()
        projects_me=Project.objects.filter(creator=user)
        projectsuser_invol=ProjectUser.objects.filter(user=user)
        #the values_list() will get the id of entries automatically
        projects_dict={'me':set({}),'invol':set({}),'starred':set({})}
        for project in projects_me:
            if project.star==1:
                projects_dict['starred'].add(project)
            projects_dict['me'].add(project)
        for projectuser in projectsuser_invol:
            project=projectuser.project
            project.star_not_creator=projectuser.star
            project.owner=project.creator.username
            projects_dict['invol'].add(project)
            if projectuser.star:
                projects_dict['starred'].add(project)
        del_projects=[]
        for project_invol in projects_dict.get('invol'):
            for project_me in projects_dict.get('me'):
                if project_invol.owner==project_me.creator.username:
                    del_projects.append(project_invol)
                    break
        for del_proj in del_projects:
            projects_dict.get('invol').remove(del_proj)
        proj_num=len(projects_me)
        if proj_num<request.user.status.proj_num:
            crea_allow=True
        else:
            crea_allow=False
        new_proj_form=NewProjForm(request)
        context={
            'form':new_proj_form,
            'crea_allow':crea_allow,
            'projects_set_me':projects_dict.get('me'),
            'projects_set_invol': projects_dict.get('invol'),
            'projects_set_starred': projects_dict.get('starred'),
            'projects_set_invol_creator':projects_dict.get('invol_creator')
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
        project_owner=request.POST.get('project_owner')
        project_name=request.POST.get('project_name')
        from web.models import ProjectUser,UserInfo,Project
        user=UserInfo.objects.filter(username=request.user.username).first()
        creator=UserInfo.objects.filter(username=project_owner).first()
        project=Project.objects.filter(name=project_name,creator=creator).first()
        projectuser=ProjectUser.objects.filter(project=project,user=user).first()
        res={}
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

