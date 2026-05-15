from django.db import models
from django.contrib.auth.models import User

class SearchResult(models.Model):
    title = models.CharField(max_length=300)
    url = models.URLField(unique=True)
    description = models.TextField(blank=True)
    source_site = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # NEW: static importance score for page ranking (higher = more relevant)
    rank = models.FloatField(default=0.0, help_text="Static importance score")

    class Meta:
        ordering = ['-rank', '-created_at']   # show boosted articles first

    def __str__(self):
        return self.title

class UserBookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    result = models.ForeignKey(SearchResult, on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'result']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} → {self.result.title}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.user.username