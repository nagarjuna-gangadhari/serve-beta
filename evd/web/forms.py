from django import forms
from .models import TvBroadCast
  
# creating a form 
class TvBroadCastForm(forms.ModelForm):
    class Meta:
        model = TvBroadCast
        fields = ('state','student_class', 'date', )
