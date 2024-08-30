"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myapp import views
from django.contrib import admin
from django.urls import path, include
from tools import views as tool_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')),
    path('', views.index, name='index'),
    path('idle/', views.idle, name='idle'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('learning-center/', views.learning_center, name='learning_center'),
    path('forum/', views.forum, name='forum'),
    path('forum/create/', views.create_post, name='create_post'),
    path('forum/post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('favorite/<int:post_id>/', views.favorite_post, name='favorite_post'),
    path('profile/<int:user_id>/', views.user_profile, name='user_profile'),
    path('reply-to-reply/<int:reply_id>/', views.reply_to_reply, name='reply_to_reply'),
    path('edit-post/<int:post_id>/', views.edit_post, name='edit_post'),
    path('delete-post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('edit-reply/<int:reply_id>/', views.edit_reply, name='edit_reply'),
    path('delete-reply/<int:reply_id>/', views.delete_reply, name='delete_reply'),
    path('marketplace/', views.marketplace, name='marketplace'),
    path('marketplace/create/', views.create_listing, name='create_listing'),
    path('marketplace/<int:listing_id>/', views.listing_detail, name='listing_detail'),
    path('marketplace/delete/<int:listing_id>/', views.delete_listing, name='delete_listing'),
    path('send-connection-request/<int:user_id>/', views.send_connection_request, name='send_connection_request'),
    path('accept-connection-request/<int:connection_id>/', views.accept_connection_request, name='accept_connection_request'),
    path('reject-connection-request/<int:connection_id>/', views.reject_connection_request, name='reject_connection_request'),
    path('unconnect/<int:connection_id>/', views.unconnect, name='unconnect'),
    path('api/notifications/', views.NotificationAPIView.as_view(), name='notifications_api'),
    path('api/notifications/<int:notification_id>/mark-read/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('api/notifications/clear/', views.clear_notifications, name='clear_notifications'),
    path('check_username/', views.check_username, name='check_username'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-courses/', views.admin_courses, name='admin_courses'),
    path('add-course/', views.add_course, name='add_course'),
    path('edit-course/<int:course_id>/', views.edit_course, name='edit_course'),
    path('delete-course/<int:course_id>/', views.delete_course, name='delete_course'),
    path('manage-lessons/<int:course_id>/', views.manage_lessons, name='manage_lessons'),
    path('add-lesson/<int:course_id>/', views.add_lesson, name='add_lesson'),
    path('edit-lesson/<int:course_id>/<int:lesson_id>/', views.edit_lesson, name='edit_lesson'),
    path('delete-lesson/<int:course_id>/<int:lesson_id>/', views.delete_lesson, name='delete_lesson'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('announcements-news/', views.admin_ann_news, name='admin_ann_news'),
    path('create-announcement/', views.create_announcement, name='create_announcement'),
    path('create-community-news/', views.create_community_news, name='create_community_news'),
    path('announcements/', views.announcements, name='announcements'),
    path('community-news/', views.community_news, name='community_news'),
    path('admin_control_panel/', views.admin_control_panel, name='admin_control_panel'),
    path('api/user/<int:user_id>/details/', views.user_details, name='user_details'),
    path('api/user/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('api/user/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('marketplace-admin/', views.marketplace_admin, name='marketplace_admin'),
    path('create-admin-listing/', views.create_admin_listing, name='create_admin_listing'),
    path('create-bulk-listings/', views.create_bulk_listings, name='create_bulk_listings'),
    path('api/lesson/<int:lesson_id>/mini-lesson/<int:mini_lesson_id>/', views.get_mini_lesson, name='get_mini_lesson'),
    path('messages/<int:user_id>/', views.get_messages, name='get_messages'),
    path('messages/', views.messages_view, name='messages'),
    path('messages/<int:user_id>/', views.get_messages, name='get_messages'),
    path('tool-settings/', tool_views.tool_settings, name='tool_settings'),
    path('tool/<int:tool_id>/', tool_views.tool_view, name='tool_view'),
    path('tools/', tool_views.tools_page, name='tools_page'),
    path('edit-tool/<int:tool_id>/', tool_views.edit_tool, name='edit_tool'),
    path('delete-tool/<int:tool_id>/', tool_views.delete_tool, name='delete_tool'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)