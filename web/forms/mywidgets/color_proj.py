from django import forms
from django.forms import widgets

class ColorWidget(forms.RadioSelect):
    class Media():
        pass