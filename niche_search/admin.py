from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from search.models import SearchResult, UserBookmark

class NicheSearchAdminSite(AdminSite):
    index_template = 'admin/index.html'   # explicitly point to your template
    site_header = 'NicheSearch Admin'
    site_title = 'NicheSearch Admin'

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['total_results'] = SearchResult.objects.count()
        extra_context['total_users'] = User.objects.count()
        extra_context['total_bookmarks'] = UserBookmark.objects.count()
        return super().index(request, extra_context)

# Create the custom instance
custom_admin_site = NicheSearchAdminSite(name='niche_admin')

# Register the built-in User model so "Manage Users" appears
custom_admin_site.register(User, UserAdmin)