import datetime
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse

class Tracer(object):
    def __init__(self):
        self.user_status=None  #it stores the pricepolicy instance
        self.project=None       #it stores the project instance if the user request a project legally
        self.project_owner=None #it indicates the whether the user is the owner of this project

class UserStatusAuth(MiddlewareMixin):
    def process_request(self,request):
        request.tracer=Tracer()
        from django.contrib.auth.models import AnonymousUser
        if isinstance(request.user,AnonymousUser):
            return
        else:
            from web.models import Transaction
            transacs=Transaction.objects.filter(user=request.user).order_by('-price_policy__id')
            #can I order the results by a field in the foreign table?Let's try it.
            #Yes,we can
            for transac in transacs:
                # we store the object pricepolicy to the attribute of request.user.status
                if not transac.end_time:
                    request.tracer.user_status = transac.price_policy
                    break
                if transac.end_time > datetime.datetime.now() :
                    request.tracer.user_status = transac.price_policy
                    break
            return
            #consider this case: if a user is in the status of pripol2, but he want to upgrade
            #his priviledge to pripol3, So the transaction will have two inexpiry entries and how
            #the hell we should do?
            #when he upgrade his pripol to 3,the endtime of pripol should be extended

class ProjectAuth(MiddlewareMixin):

    def process_view(self,request,view_func,view_args,view_kwargs):
        url=request.path_info
        if not url.startswith(r'/manage/'):
            return
        project_id = view_kwargs.get('project_id')
        from web.models import ProjectUser
        projectuser_obj=ProjectUser.objects.filter(project__id=project_id,user=request.user).first()
        if not projectuser_obj:
            return redirect(reverse('web:project_list'))
        else:
            request.tracer.project = projectuser_obj.project
            if projectuser_obj.project.creator==request.user:
                request.tracer.project_owner=True
            else:
                request.tracer.project_owner=False
            return




