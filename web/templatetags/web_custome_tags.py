from django import template
register=template.Library()
from django.urls import reverse
import unicodedata
import pinyin

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
        {'icon':'fa-solid fa-circle-question','title': 'Issues', 'url': reverse('web:issue', kwargs={'project_id': request.tracer.project.id})},
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

@register.inclusion_tag(r'web/inclusion/wiki_destination.html')
def wiki_destination_tag(wiki_group,wiki_id,request):
    from web.models import Wiki
    if wiki_id=='0':
        if wiki_group=='public-wiki':
            msg='Adding to Group: Public Wikis'
        if wiki_group=='individual-wiki':
            msg='Adding to Group: Individual Wikis'
    else:
        wiki=Wiki.objects.filter(id=wiki_id,project=request.tracer.project).first()
        if not wiki:
            msg = "You may be in an attempt to add a invalid wiki to others' proejct. But it's impossible."
            return {'msg':msg}
        wiki_title=wiki.title
        if wiki_group == 'public-wiki':
            msg='Add a subpage of wiki {} from Public Wikis'.format(wiki_title)
        if wiki_group == 'individual-wiki':
            msg='Add a subpage of wiki {} from Individual Wikis'.format(wiki_title)
    return {'msg':msg}

@register.inclusion_tag(r'web/inclusion/live-avatar.html')
def live_avatar(username):
    #this is generted from github copilot, so I don't account for the visual conformts
    color_pallete=[
        ('A','#f44336'),('B','#e91e63'),('C','#9c27b0'),('D','#673ab7'),('E','#3f51b5'),('F','#2196f3'),('G','#03a9f4'),('H','#00bcd4'),('I','#009688'),('J','#4caf50'),('K','#8bc34a'),('L','#cddc39'),('M','#ffeb3b'),('N','#ffc107'),('O','#ff9800'),('P','#ff5722'),('Q','#795548'),('R','#9e9e9e'),('S','#607d8b'),('T','#000000'),('U','#000000'),('V','#000000'),('W','#000000'),('X','#000000'),('Y','#000000'),('Z','#000000')
    ]
    first_char=username[0]
    unicode_name=unicodedata.name(first_char,'')
    if 'CJK UNIFIED IDEOGRAPH' in unicode_name:
        first_char=pinyin.get_initial(first_char).upper()
    else:
        first_char=first_char.upper()
    background_color=''
    for char,bgc in color_pallete:
        if first_char==char:
            background_color=bgc
            break
    return {
        'username':username,
        'first_char_username':first_char,
        'background_color':background_color
    }


@register.inclusion_tag(r'web/inclusion/issue_status.html')
def issue_status(status_symbol):
    issue_status_textual_color=[
        ('1','New','#00BFFF'),
        ('2','Processing','#FFD700'),
        ('3','Finished','#00FF00'),
        ('4','Timeout','#FF0000'),
    ]

    for issue_status_symbol,issue_status_text,issue_badge_color in issue_status_textual_color:
        if issue_status_symbol==status_symbol:
            text_issue_status=issue_status_text
            color_status_badge=issue_badge_color
            break
    return {
        'text_issue_status':text_issue_status,
        'color_status_badge':color_status_badge
    }

@register.inclusion_tag(r'web/inclusion/issue_priviledge.html')
def issue_privilidge(issue_priviledge_symbol):
    issue_priviledge_textual_color=[
        ('1', 'Low','#333333'),
        ('2', 'Medium','#0074D9'),
        ('3', 'High','#FF851B'),
        ('4', 'Premium','#FFD700')
    ]
    context={}
    for symbol,text,color in issue_priviledge_textual_color:
        if symbol==issue_priviledge_symbol:
            context['priviledge_text']=text
            context['badge_color']=color
            break
    return context

@register.inclusion_tag(r'web/inclusion/issue_type.html')
def issue_type(issue_type_symbol):
    issue_type_textual_color=[
        ('1', 'task','#0074D9'),
        ('2', 'bug','#FF4136'),
        ('3', 'feature_discussion','#B10DC9')
    ]
    context={}
    for symbol,text,color in issue_type_textual_color:
        if symbol==issue_type_symbol:
            context['type_text']=text
            context['type_badge_color']=color
            break
    return context