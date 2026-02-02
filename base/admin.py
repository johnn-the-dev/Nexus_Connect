from django.contrib import admin

# Register your models here.

from .models import LFGPost, Message

admin.site.register(LFGPost)
admin.site.register(Message)