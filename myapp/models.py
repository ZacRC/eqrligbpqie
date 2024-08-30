from django.contrib.auth.models import AbstractUser
from django.db import models
from model_utils.managers import InheritanceManager
from django.utils import timezone

class User(AbstractUser):
    bio = models.TextField(blank=True)
    profile_picture = models.URLField(default='https://pbs.twimg.com/media/EEU0IauVAAE88xo.png')
    connections = models.ManyToManyField('self', through='Connection', symmetrical=False, related_name='connected_to')
    favorite_posts = models.ManyToManyField('ForumPost', related_name='favorited_by', blank=True)
    favorite_replies = models.ManyToManyField('ForumReply', related_name='favorited_by', blank=True)
    reputation = models.IntegerField(default=0)
    forum_posts = models.ManyToManyField('ForumPost', related_name='authors', blank=True)
    forum_replies = models.ManyToManyField('ForumReply', related_name='authors', blank=True)

class ForumPost(models.Model):
    CATEGORIES = [
        ('tiktok', 'TikTok'),
        ('youtube', 'YouTube'),
        ('affiliate', 'Affiliate Marketing'),
        ('other', 'Other'),
        ('accomplishments', 'Accomplishments'),
        ('partnerships', 'Partnerships'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORIES)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class ForumReply(models.Model):
    post = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent_reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    quoted_reply = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Reply to {self.post.title} by {self.author.username}"

class Listing(models.Model):
    PLATFORM_CHOICES = [
        ('youtube', 'YouTube'),
        ('tiktok', 'TikTok'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    platform = models.CharField(max_length=10, choices=PLATFORM_CHOICES)
    followers = models.IntegerField()
    niche = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notification_created_at = models.DateTimeField(default=timezone.now)
    tiktok_shop = models.BooleanField(default=False)
    creative_fund = models.BooleanField(default=False)
    youtube_monetization = models.BooleanField(default=False)

    escrow_type = models.CharField(max_length=10, choices=[('locked', 'Locked'), ('unlocked', 'Unlocked')], default='unlocked')
    escrow_details = models.TextField(blank=True, null=True)
    admin_confirmation = models.TextField(blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    marketplace_notification = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

class Connection(models.Model):
    from_user = models.ForeignKey(User, related_name='connections_initiated', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='connection_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('from_user', 'to_user')

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='fa-book')
    video = models.FileField(upload_to='course_videos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    order = models.IntegerField()

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class MiniLesson(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='mini_lessons')
    title = models.CharField(max_length=200)
    description = models.TextField()
    video_url = models.URLField(blank=True, null=True)
    video_file = models.FileField(upload_to='lesson_videos/', blank=True, null=True)
    order = models.IntegerField()

    def __str__(self):
        return f"{self.lesson.title} - {self.title}"

    def save(self, *args, **kwargs):
        if self.video_file and self.video_url:
            self.video_url = ''  # Clear YouTube URL if a file is uploaded
        super().save(*args, **kwargs)

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class CommunityNews(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"From {self.sender} to {self.receiver}: {self.content[:20]}..."

class MarketplaceNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marketplace_notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:50]}..."