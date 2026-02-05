from django.forms import ModelForm
from .models import LFGPost


class LFGPostForm(ModelForm):
    class Meta:
        model = LFGPost
        fields = '__all__'
        exclude = ['host', 'participants']