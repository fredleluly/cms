from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Tag, Section, Element, StudySession, StudyRecord

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'user')
    search_fields = ('name',)
    list_filter = ('user',)

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'parent', 'user', 'order')
    search_fields = ('title',)
    list_filter = ('user',)

@admin.register(Element)
class ElementAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'user', 'section', 'is_completed', 'created_at')
    list_filter = ('type', 'user', 'is_completed', 'is_archived', 'is_favorite')
    search_fields = ('title', 'content')
    readonly_fields = ('id', 'created_at', 'updated_at')

@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'started_at', 'ended_at', 'section')
    list_filter = ('user',)

@admin.register(StudyRecord)
class StudyRecordAdmin(admin.ModelAdmin):
    list_display = ('element', 'session', 'result', 'studied_at')
    list_filter = ('result', 'session')