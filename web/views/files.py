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
        return render(request, r'web/file.html', {'request': request})

class FileUploadView(LoginRequiredMixin,View):
    def post(self,request,*args,**kwargs):
        folderId=request.POST.get('folderId')
        files=[request.FILES.get('file[%d]' %i)  for i in range(len(request.FILES))]
        response=[]
        def validate_file(file,bucket_name,file_key):
            validate_res={}
            validate_res['file_name'] = []
            accepted_file=[]
            file_url='https://{bucket_name}.cos.ap-chengdu.mycloud.com/{file_key_urlformat}'.format(bucket_name=bucket_name,file_key_urlformat=quote(file_key))
            if len(file_url)>256:
                validate_res['file_name'].append('file key generated from this file name is too long. Please cut it to remain only the extension')
            if len(file.name)>64:
                validate_res['file_name'].append('file name is too long')
            if file.size>524288000: ##500MB
                validate_res['file_size']=['file size excceeds the limit of 500MB',]
            return validate_res
        for file in files:
            file_key='{uuid}-{file_name}'.format(uuid=uuid4().hex,file_name=file.name)
            validate_res=validate_file(file,bucket_name=request.tracer.project.bucket_name,file_key=file_key)
            if len(validate_res['file_name']):
                file_name_for_file_key=os.path.splitext(file.name)[1]
                file_key='{uuid}-{file_name}'.format(uuid=uuid4().hex,file_name=file_name_for_file_key)
                del validate_res['file_name'][0]
                if len(validate_res)>1 or len(validate_res['file_name']):
                    response.append({'flag':'validation_failure','content':validate_res})
                    continue
            buffer = io.BytesIO()
            buffer.write(file.read())
            try:
                uploading_response = cos_client_chengdu.put_object(
                    bucket_name=request.tracer.project.bucket_name,
                    fp=buffer,
                    file_key=file_key
                )
            except Exception as e:
                response.append({'flag': 'uploading_failure', 'content': 'uploading to cloud failed'})
                continue
            if uploading_response:
                file = File.objects.create(
                    project=request.tracer.project,
                    parent_file=File.objects.filter(id=folderId).first(),
                    name=file.name,
                    file_size=file.size,
                    file_url='https://{bucket_name}.cos.ap-chengdu.mycloud.com/{file_key_urlformat}'.format(
                        bucket_name=request.tracer.project.bucket_name, file_key_urlformat=quote(file_key)),
                    file_type=1,
                    file_ext=os.path.splitext(file.name)[1],
                    creator=request.user
                )
                if file:
                    response.append({'flag': 'uploading success', 'content': 'uploading success'})
                else:
                    response.append({'flag': 'storing failure', 'content': 'file stored in mysql failure'})
        return JsonResponse(response,safe=False)



