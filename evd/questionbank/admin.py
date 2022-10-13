from django.contrib import admin
from .models import *


class QuestionTypeAdmin(admin.ModelAdmin):
    list_filter = ['name', 'instructions','code']
    search_fields = ['name']
    list_display = ['name', 'instructions', 'code','status','created_by','created_on','updated_by','updated_on']
    ordering = ['id']


class QuestionSetAdmin(admin.ModelAdmin):
    list_filter = ['name', 'topic', 'subtopic']
    search_fields = ['name']
    list_display = ['name', 'topic', 'subtopic','status','type','created_by','created_on','updated_by','updated_on','content_detail']
    ordering = ['id']




class QuestionComponentAdmin(admin.ModelAdmin):
    #list_filter = ['text', 'question', 'subtype','question__id','question__text']
    search_fields = ['text','question__id']
    list_display = ['text', 'status', 'subtype', 'is_answer','image_url','created_on','matching_component','question']
    ordering = ['id']

class QuestionComponentInline(admin.TabularInline):
    model = Question_Component


class QuestionAdmin(admin.ModelAdmin):
    inlines = [
        QuestionComponentInline
    ]
    list_filter = ['type']
    search_fields = ['title','text','topic__id']
    list_display = ['id','title', 'text', 'status', 'topic', 'subtopic','type','hint','complexity','points', 'created_on'
        , 'sequence','actual_sequence_string']
    ordering = ['id']

admin.site.register(Question_Type, QuestionTypeAdmin)
admin.site.register(Question_Set, QuestionSetAdmin)
admin.site.register(Question_Component,QuestionComponentAdmin)
admin.site.register(Question, QuestionAdmin)


