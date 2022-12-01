from django import forms
from django.forms import widgets

class ColorWidget(forms.RadioSelect):
    class Media():
        js=('web/static/web/js/new_radio_widget.js',)

