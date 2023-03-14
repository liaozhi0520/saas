from django.views import View
from django.http import HttpResponse,JsonResponse
from django.shortcuts import render

class IssuesView(View):
    def get(self,request,*args,**kwargs):
        return render(request, r'web/issues.html', {'request': request})

class IssueDetailView(View):
    def get(self,request,*args,**kwargs):
        pass
