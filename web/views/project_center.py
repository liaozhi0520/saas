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
        from web.models import UserInfo,Project
        user=UserInfo.objects.filter(username=request.user.username).first()
        projects=Project.objects.filter(creator=user)
        proj_num=len(projects)
        if proj_num<request.user.status.proj_num:
            crea_allow=True
        else:
            crea_allow=False
        new_proj_form=NewProjForm(request)
        context={
            'form':new_proj_form,
            'crea_allow':crea_allow
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
