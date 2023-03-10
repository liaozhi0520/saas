import io
import os.path
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse,HttpResponse
from web.models import File,Project
from urllib.parse import quote
from utils.cos import *
from uuid import uuid4
from web.forms.files import *

class LoginRequiredMixin(object):
    @method_decorator(login_required)
    #wrap the method dispatch a decorator
    def dispatch(self,request,*args,**kwargs):
        return super(LoginRequiredMixin, self).dispatch(request,*args,**kwargs)

class FileView(LoginRequiredMixin,View):
    def get(self,request,*args,**kwargs):
        param=request.GET.get('param')
        if param=='getProjectFiles':
            response=File.objects.filter(project=request.tracer.project).order_by('id').values()
            ##convert the datetime.datetimg object into isoformat
            for file in response:
                file['creating_time']=file.get('creating_time').isoformat()
            return JsonResponse(list(response),safe=False)
        else:
            create_folder_form=NewFolder(request)
        return render(request, r'web/file.html', {
            'request': request,
            'create_folder_form':create_folder_form,
        })

class FileUploadView(LoginRequiredMixin,View):
    def post(self,request,*args,**kwargs):
        folderId=int(request.POST.get('uploadFileParentId'))
        files=[request.FILES.get('file[%d]' %i)  for i in range(len(request.FILES))]
        response=[]
        def validate_file(file,folderId):
            validation_res={}
            ##file.size
            if file.size>524288000: ##500MB
                validation_res['file_size']='file size excceeds 500MB.'
            if len(file.name)>64:
                validation_res['file_name']='file name excceeds 64 chars.'
            if (file.name,) in File.objects.filter(id=folderId).first().subfiles.values_list('name'):
                validation_res['file_name'] = 'file name excceeds 64 chars and the file name dulicated in the folder'
            if len(file.name)>64 and (file.name,) in File.objects.filter(id=folderId).first().subfiles.values_list('name'):
                validation_res['file_name']= 'file name excceeds 64 chars and file name excceeds 64 chars and the file name dulicated in the folder'
            return validation_res
        for file in files:
            validation_res=validate_file(file,folderId)
            if len(validation_res):
                response.append({
                    'flag':False,
                    'code':'validation_failure',
                    'content':validation_res
                })
                continue
            buffer = io.BytesIO()
            buffer.write(file.read())
            try:
                file_key = '{uuid}-{file_name}'.format(uuid=uuid4().hex, file_name=file.name)
                uploading_response = cos_client_chengdu.put_object(
                    bucket_name=request.tracer.project.bucket_name,
                    fp=buffer,
                    file_key=file_key
                )
            except Exception as e:
                response.append({
                    'flag':False,
                    'code':'uploading_failure',
                    'content':'uploading failure'
                })
                continue
            if uploading_response:
                file = File.objects.create(
                    project=request.tracer.project,
                    parent_file=File.objects.filter(id=folderId).first(),
                    name=file.name,
                    file_size=file.size,
                    file_key=file_key,
                    file_type=1,
                    file_ext=os.path.splitext(file.name)[1],
                    creator=request.user
                )
                if file:
                    response.append({'flag': True,'code':'uploading success', 'content': 'uploading success'})
                else:
                    response.append({'flag': False,'code':'storing failure','content': 'file stored in mysql failure'})
        return JsonResponse(response,safe=False)


class FileCreateFolderView(LoginRequiredMixin,View):
    def post(self,request,*args,**kwargs):
        new_folder_form=NewFolder(request,request.POST)
        if new_folder_form.is_valid():
            parent_folder_id=new_folder_form.cleaned_data.get('parent_folder_id')
            foldername=new_folder_form.cleaned_data.get('foldername')
            file=File.objects.create(
                project=request.tracer.project,
                parent_file=File.objects.filter(id=parent_folder_id).first(),
                name=foldername,
                file_key=None,
                file_size=0,
                file_type=2,
                file_ext=None,
                creator=request.user
            )
            if file:
                response={
                    'flag':True,
                    'content':''
                }
            else:
                return HttpResponse('file stored in mysql failed',status=500)
        else:
            response={
                'flag':False,
                'content':{
                    'parent_folder_id':new_folder_form.errors.get('parent_folder_id',None),
                    'foldername':new_folder_form.errors.get('foldername',None)
                }
            }
        return JsonResponse(response)


