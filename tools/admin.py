from django.contrib import admin
from .models import Tool

class ToolAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'is_featured', 'created_at', 'updated_at')
    list_filter = ('is_featured', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(Tool, ToolAdmin)