from django.contrib import admin
from .models import SearchResult, UserBookmark

@admin.register(SearchResult)
class SearchResultAdmin(admin.ModelAdmin):
    list_display = ['title', 'source_site', 'created_at']
    search_fields = ['title', 'description']
    list_filter = ['source_site']

@admin.register(UserBookmark)
class UserBookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'result', 'created_at']
    autocomplete_fields = ['user', 'result']