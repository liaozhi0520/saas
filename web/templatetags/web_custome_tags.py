from django import template
register=template.Library()
from django.urls import reverse

#include the project_menu_markup
@register.inclusion_tag(r'web/inclusion/project_menu.html')
def project_menu_tag(project_list_me,project_lsit_invol):
    res={
        'project_list_me':project_list_me,
        'project_list_invol':project_lsit_invol
    }
    return res

@register.inclusion_tag(r'web/inclusion/manage_menu.html')
def manage_menu_tag(request):
    path_info=request.path_info
    data_list=[
        {'icon':'fa-solid fa-eye','title':'Dashboard','url':reverse('web:dashboard',kwargs={'project_id':request.tracer.project.id})},
        {'icon':'fa-solid fa-circle-question','title': 'Issues', 'url': reverse('web:issues', kwargs={'project_id': request.tracer.project.id})},
        {'icon':'fa-solid fa-chart-line','title': 'Statistics', 'url': reverse('web:statistics', kwargs={'project_id': request.tracer.project.id})},
        {'icon':'fa-brands fa-wikipedia-w','title': 'Wiki', 'url': reverse('web:wiki', kwargs={'project_id': request.tracer.project.id})},
        {'icon':'fa-solid fa-file','title': 'File', 'url': reverse('web:file', kwargs={'project_id': request.tracer.project.id})},
        {'icon':'fa-solid fa-gears','title': 'Setting', 'url': reverse('web:setting', kwargs={'project_id': request.tracer.project.id})},
    ]
    for item in data_list:
        if item['url']==path_info:
            item['class']='active'
    return {'data_list':data_list,'request':request}

# why do I need to use the inclusion tag? Because the DTL is not powerful enough, if I need some data generate from the
#context passed from the view and the DTL can't implement the genneration logic, then the inclusion_tag can help.
#Because the python power is super cool.