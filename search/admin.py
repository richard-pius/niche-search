from django.contrib import admin
from .models import SearchResult, UserBookmark, UserProfile

@admin.register(SearchResult)
class SearchResultAdmin(admin.ModelAdmin):
    list_display = ['title', 'source_site', 'created_at']
    search_fields = ['title', 'description']

@admin.register(UserBookmark)
class UserBookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'result', 'created_at']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'profile_picture']