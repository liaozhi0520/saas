from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render


class LoginRequiredMixin(object):
    @method_decorator(login_required)
    #wrap the method dispatch a decorator
    def dispatch(self,request,*args,**kwargs):
        return super(LoginRequiredMixin, self).dispatch(request,*args,**kwargs)

class ProjectListView(LoginRequiredMixin,View):
    def get(self,request,*args,**kwargs):
        return render(request,r'web/project_list.html',{})

    def post(self,request,*args,**kwargs):
        pass