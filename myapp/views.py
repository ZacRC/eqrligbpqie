from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import User, ForumPost, ForumReply, Connection, Notification, Course, Lesson, MiniLesson, Announcement, CommunityNews, Message, Listing, MarketplaceNotification  # Import your custom User model
from .forms import ForumPostForm, ForumReplyForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Listing
from .forms import ListingForm, ListingEditForm
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import NotificationSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from .serializers import NotificationSerializer
from django.urls import reverse
# In your views.py file
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import get_user_model
import json
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404
from .models import Course, Lesson, MiniLesson
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from .models import Announcement, CommunityNews
from django.shortcuts import render
from .models import Announcement, CommunityNews
from django.contrib.auth.hashers import make_password
import random
from django.contrib import messages
from django.core.files.storage import default_storage
from django.utils import timezone

def announcements(request):
    announcements = Announcement.objects.all().order_by('-created_at')
    return render(request, 'announcements.html', {'announcements': announcements})

def community_news(request):
    community_news = CommunityNews.objects.all().order_by('-created_at')
    return render(request, 'communitynews.html', {'community_news': community_news})

@staff_member_required
def admin_ann_news(request):
    print("admin_ann_news view is being called")
    return render(request, 'adminannnews.html')

@staff_member_required
def create_announcement(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        Announcement.objects.create(title=title, description=description)
        if Announcement.objects.count() > 2:
            oldest_announcement = Announcement.objects.earliest('created_at')
            oldest_announcement.delete()
        return redirect('admin_ann_news')

@staff_member_required
def create_community_news(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        CommunityNews.objects.create(title=title, description=description)
        if CommunityNews.objects.count() > 2:
            oldest_news = CommunityNews.objects.earliest('created_at')
            oldest_news.delete()
        return redirect('admin_ann_news')

def index(request):
    return render(request, 'index.html')

def idle(request):
    return render(request, 'idle.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            return redirect('dashboard')
    
    return render(request, 'register.html')

def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def dashboard(request):
    top_users = User.objects.order_by('-reputation')[:5]
    announcements = Announcement.objects.all().order_by('-created_at')[:2]
    community_news = CommunityNews.objects.all().order_by('-created_at')[:2]
    
    context = {
        'top_users': top_users,
        'announcements': announcements,
        'community_news': community_news,
    }
    return render(request, 'dash.html', context)

@login_required
def learning_center(request):
    courses = Course.objects.all()
    return render(request, 'learningcenter.html', {'courses': courses})

def marketplace(request):
    listings = Listing.objects.filter(is_approved=True).order_by('-created_at')
    return render(request, 'marketplace.html', {'listings': listings})

@login_required
def your_profile(request):
    user = request.user
    context = {
        'profile_user': user,
        'user_posts': user.forumpost_set.all(),
        'user_replies': user.forumreply_set.all(),
        'user_connections': user.connections.all(),
        'is_own_profile': True,
    }
    return render(request, 'yourprofile.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        user.bio = request.POST.get('bio', '')
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
        user.save()
        return redirect('your_profile')
    return render(request, 'edit_profile.html')

@login_required
def create_post(request):
    if request.method == 'POST':
        form = ForumPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('forum')
    else:
        form = ForumPostForm()
    return render(request, 'create_post.html', {'form': form})

@login_required
def reply_to_post(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    if request.method == 'POST':
        form = ForumReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.post = post
            reply.save()
            request.user.forum_replies.add(reply)
            return redirect('post_detail', post_id=post.id)
    else:
        form = ForumReplyForm()
    return render(request, 'post_detail.html', {'post': post, 'replies': post.replies.all().order_by('created_at'), 'form': form})

@login_required
def post_detail(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    replies = post.replies.filter(parent_reply=None).order_by('created_at')
    
    if request.method == 'POST':
        form = ForumReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.post = post
            reply.author = request.user
            
            # Check if it's a quoted reply
            content = form.cleaned_data['content']
            if content.startswith('>'):
                lines = content.split('\n')
                quoted_content = lines[0].strip('> ')
                reply.quoted_reply = quoted_content
                reply.content = '\n'.join(lines[2:])  # Skip the empty line after the quote
            
            reply.save()
            return redirect('post_detail', post_id=post.id)
    else:
        form = ForumReplyForm()
    
    form.fields['content'].widget.attrs.update({'class': 'w-full p-2 rounded-lg bg-gray-700 text-white'})
    
    return render(request, 'post_detail.html', {'post': post, 'replies': replies, 'form': form})

@login_required
def favorite_post(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    if post in request.user.favorite_posts.all():
        request.user.favorite_posts.remove(post)
        post.author.reputation -= 1
        status = 'unfavorited'
    else:
        request.user.favorite_posts.add(post)
        post.author.reputation += 1
        status = 'favorited'
    post.author.save()
    return JsonResponse({'status': status})

@login_required
def favorite_reply(request, reply_id):
    reply = get_object_or_404(ForumReply, id=reply_id)
    if reply in request.user.favorite_replies.all():
        request.user.favorite_replies.remove(reply)
        reply.author.reputation -= 1
        status = 'unfavorited'
    else:
        request.user.favorite_replies.add(reply)
        reply.author.reputation += 1
        status = 'favorited'
    reply.author.save()
    return JsonResponse({'status': status})

@login_required
def reply_to_reply(request, reply_id):
    parent_reply = get_object_or_404(ForumReply, id=reply_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        new_reply = ForumReply.objects.create(
            post=parent_reply.post,
            author=request.user,
            content=content,
            parent_reply=parent_reply
        )
        return redirect('post_detail', post_id=parent_reply.post.id)
    return redirect('post_detail', post_id=parent_reply.post.id)

def forum(request):
    categories = dict(ForumPost.CATEGORIES)
    posts = ForumPost.objects.all().order_by('-created_at')
    return render(request, 'forum.html', {'posts': posts, 'categories': categories})

@login_required
def user_profile(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    is_own_profile = request.user == profile_user
    is_connected = False
    connection_request_sent = False
    connection_request_received = None
    connection_requests = []
    connection_requests_count = 0

    if is_own_profile:
        connection_requests = Connection.objects.filter(to_user=profile_user, accepted=False)
        connection_requests_count = connection_requests.count()
    elif not is_own_profile:
        is_connected = Connection.objects.filter(
            (Q(from_user=request.user, to_user=profile_user) | Q(from_user=profile_user, to_user=request.user)),
            accepted=True
        ).exists()
        connection_request_sent = Connection.objects.filter(from_user=request.user, to_user=profile_user, accepted=False).exists()
        connection_request_received = Connection.objects.filter(from_user=profile_user, to_user=request.user, accepted=False).first()

    user_connections = Connection.objects.filter(
        (Q(from_user=profile_user) | Q(to_user=profile_user)),
        accepted=True
    )

    context = {
        'profile_user': profile_user,
        'user_posts': profile_user.forumpost_set.all(),
        'user_replies': profile_user.forumreply_set.all(),
        'user_connections': user_connections,
        'is_own_profile': is_own_profile,
        'is_connected': is_connected,
        'connection_request_sent': connection_request_sent,
        'connection_request_received': connection_request_received,
        'connection_requests': connection_requests,
        'connection_requests_count': connection_requests_count,
    }
    return render(request, 'yourprofile.html', context)

@login_required
@require_POST
def edit_post(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    if request.user != post.author:
        return JsonResponse({'status': 'error', 'message': 'You are not authorized to edit this post.'})
    
    data = json.loads(request.body)
    post.content = data.get('content')
    post.save()
    return JsonResponse({'status': 'success'})

@login_required
@require_POST
def delete_post(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    if request.user != post.author:
        return JsonResponse({'status': 'error', 'message': 'You are not authorized to delete this post.'})
    
    post.delete()
    return JsonResponse({'status': 'success'})

@login_required
@require_POST
def edit_reply(request, reply_id):
    reply = get_object_or_404(ForumReply, id=reply_id)
    if request.user != reply.author:
        return JsonResponse({'status': 'error', 'message': 'You are not authorized to edit this reply.'})
    
    data = json.loads(request.body)
    reply.content = data.get('content')
    reply.save()
    return JsonResponse({'status': 'success'})

@login_required
@require_POST
def delete_reply(request, reply_id):
    reply = get_object_or_404(ForumReply, id=reply_id)
    if request.user != reply.author:
        return JsonResponse({'status': 'error', 'message': 'You are not authorized to delete this reply.'})
    
    reply.delete()
    return JsonResponse({'status': 'success'})

@login_required
def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.user = request.user
            listing.is_approved = listing.escrow_type == 'unlocked'
            listing.save()
            if listing.escrow_type == 'locked':
                messages.info(request, "Your listing has been submitted for admin approval.")
            return redirect('marketplace')
    else:
        form = ListingForm()
    return render(request, 'create_listing.html', {'form': form})

def listing_detail(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    return render(request, 'listing_detail.html', {'listing': listing})

@login_required
def delete_listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id, user=request.user)
    was_approved = listing.is_approved
    admin_confirmation = listing.admin_confirmation
    listing_title = listing.title
    
    if was_approved:
        message = f"Your approved listing '{listing_title}' has been deleted."
        MarketplaceNotification.objects.create(
            user=request.user,
            message=f"{message} Admin confirmation: {admin_confirmation}"
        )
    else:
        message = f"Your pending listing '{listing_title}' has been canceled."
        MarketplaceNotification.objects.create(user=request.user, message=message)
    
    listing.delete()
    messages.success(request, message)
    
    return redirect('marketplace_profile')

@login_required
def send_connection_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    connection, created = Connection.objects.get_or_create(from_user=request.user, to_user=to_user)
    if created:
        Notification.objects.create(
            user=to_user,
            sender=request.user,
            message=f"{request.user.username} sent you a connection request."
        )
        return JsonResponse({'status': 'request_sent'})
    else:
        connection.delete()
        return JsonResponse({'status': 'request_cancelled'})

@login_required
def accept_connection_request(request, connection_id):
    connection = get_object_or_404(Connection, id=connection_id, to_user=request.user)
    connection.accepted = True
    connection.save()
    return JsonResponse({'status': 'request_accepted'})

@login_required
def reject_connection_request(request, connection_id):
    connection = get_object_or_404(Connection, id=connection_id, to_user=request.user)
    connection.delete()
    return JsonResponse({'status': 'request_rejected'})

@login_required
def unconnect(request, connection_id):
    connection = get_object_or_404(Connection, id=connection_id)
    if request.user == connection.from_user or request.user == connection.to_user:
        connection.delete()
        return JsonResponse({'status': 'unconnected'})
    else:
        return JsonResponse({'status': 'error', 'message': 'You are not authorized to perform this action.'})

class NotificationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_as_read(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return Response({'status': 'success'})
    except Notification.DoesNotExist:
        return Response({'status': 'error', 'message': 'Notification not found'}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_notifications(request):
    Notification.objects.filter(user=request.user).delete()
    return Response({'status': 'success'})


@require_POST
@csrf_protect
def check_username(request):
    data = json.loads(request.body)
    username = data.get('username')
    User = get_user_model()
    is_taken = User.objects.filter(username=username).exists()
    return JsonResponse({'available': not is_taken})

@staff_member_required
def admin_panel(request):
    return render(request, 'admin.html')

@staff_member_required
def admin_courses(request):
    courses = Course.objects.all()
    return render(request, 'admincourse.html', {'courses': courses})

@staff_member_required
def add_course(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        icon = request.POST['icon']
        youtube_url = request.POST.get('youtube_url', '')
        video = request.FILES.get('video')

        course = Course(title=title, description=description, icon=icon)
        if youtube_url:
            course.video_url = youtube_url
        if video:
            course.video = video
        course.save()

        return redirect('admin_courses')
    return redirect('admin_courses')

@staff_member_required
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        course.title = request.POST.get('title')
        course.description = request.POST.get('description')
        course.icon = request.POST.get('icon')
        course.save()
        return redirect('admin_courses')
    return render(request, 'edit_course.html', {'course': course})

@staff_member_required
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    course.delete()
    return redirect('admin_courses')

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    return render(request, 'course_detail.html', {'course': course})

@staff_member_required
def manage_lessons(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    return render(request, 'manage_lessons.html', {'course': course})

@staff_member_required
def add_lesson(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        lesson = Lesson.objects.create(
            course=course,
            title=request.POST['title'],
            order=request.POST['order']
        )
        video_urls = request.POST.getlist('video_urls[]')
        video_files = request.FILES.getlist('video_files[]')
        mini_titles = request.POST.getlist('mini_titles[]')
        descriptions = request.POST.getlist('descriptions[]')
        
        for i in range(len(mini_titles)):
            mini_lesson = MiniLesson.objects.create(
                lesson=lesson,
                title=mini_titles[i],
                description=descriptions[i],
                order=i+1
            )
            if i < len(video_urls) and video_urls[i]:
                mini_lesson.video_url = video_urls[i]
            if i < len(video_files) and video_files[i]:
                mini_lesson.video_file = video_files[i]
            mini_lesson.save()
    return redirect('manage_lessons', course_id=course_id)

@staff_member_required
def edit_lesson(request, course_id, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, course_id=course_id)
    if request.method == 'POST':
        lesson.title = request.POST['title']
        lesson.order = request.POST['order']
        lesson.save()

        mini_lesson_ids = request.POST.getlist('mini_lesson_ids[]')
        video_urls = request.POST.getlist('video_urls[]')
        video_files = request.FILES.getlist('video_files[]')
        mini_titles = request.POST.getlist('mini_titles[]')
        descriptions = request.POST.getlist('descriptions[]')

        for i in range(len(mini_titles)):
            if i < len(mini_lesson_ids):
                mini_lesson = MiniLesson.objects.get(id=mini_lesson_ids[i])
                mini_lesson.title = mini_titles[i]
                mini_lesson.description = descriptions[i]
                
                if video_files[i]:
                    # Delete old file if it exists
                    if mini_lesson.video_file:
                        default_storage.delete(mini_lesson.video_file.path)
                    mini_lesson.video_file = video_files[i]
                    mini_lesson.video_url = ''
                elif video_urls[i]:
                    mini_lesson.video_url = video_urls[i]
                    if mini_lesson.video_file:
                        default_storage.delete(mini_lesson.video_file.path)
                        mini_lesson.video_file = None
                
                mini_lesson.save()
            else:
                new_mini_lesson = MiniLesson.objects.create(
                    lesson=lesson,
                    title=mini_titles[i],
                    description=descriptions[i],
                    order=i+1
                )
                if video_files[i]:
                    new_mini_lesson.video_file = video_files[i]
                elif video_urls[i]:
                    new_mini_lesson.video_url = video_urls[i]
                new_mini_lesson.save()
        
        return redirect('manage_lessons', course_id=course_id)
    return render(request, 'edit_lesson.html', {'lesson': lesson})

@staff_member_required
def delete_lesson(request, course_id, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id, course_id=course_id)
    lesson.delete()  # This will also delete associated mini-lessons due to CASCADE
    return redirect('manage_lessons', course_id=course_id)

@staff_member_required
def admin_control_panel(request):
    User = get_user_model()
    users = User.objects.all()
    return render(request, 'admincontrolpanel.html', {'users': users})

@staff_member_required
def user_details(request, user_id):
    User = get_user_model()
    user = get_object_or_404(User, id=user_id)
    data = {
        'username': user.username,
        'email': user.email,
        'date_joined': user.date_joined.strftime('%B %d, %Y'),
        'last_login': user.last_login.strftime('%B %d, %Y') if user.last_login else 'Never',
        'connections': user.connections.count(),
        'forum_posts': [{'title': post.title} for post in user.forumpost_set.all()],
        'forum_replies': [{'content': reply.content} for reply in user.forumreply_set.all()],
    }
    return JsonResponse(data)

@staff_member_required
@require_POST
def edit_user(request, user_id):
    User = get_user_model()
    user = get_object_or_404(User, id=user_id)
    user.username = request.POST.get('username', user.username)
    user.email = request.POST.get('email', user.email)
    new_password = request.POST.get('password')
    if new_password:
        user.password = make_password(new_password)
    user.save()
    return JsonResponse({'status': 'success'})

@staff_member_required
@require_POST
def delete_user(request, user_id):
    User = get_user_model()
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return JsonResponse({'status': 'success'})

@staff_member_required
def marketplace_admin(request):
    users = User.objects.all()
    pending_listings = Listing.objects.filter(escrow_type='locked', is_approved=False)
    return render(request, 'marketplaceadmin.html', {'users': users, 'pending_listings': pending_listings})

@staff_member_required
def create_admin_listing(request):
    if request.method == 'POST':
        user_id = request.POST.get('user')
        user = User.objects.get(id=user_id)
        listing = Listing.objects.create(
            user=user,
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            platform=request.POST.get('platform'),
            followers=request.POST.get('followers'),
            niche=request.POST.get('niche'),
            price=request.POST.get('price'),
            tiktok_shop=request.POST.get('tiktok_shop') == 'on',
            creative_fund=request.POST.get('creative_fund') == 'on',
            youtube_monetization=request.POST.get('youtube_monetization') == 'on'
        )
        messages.success(request, 'Listing created successfully.')
        return redirect('marketplace_admin')
    return redirect('marketplace_admin')

import json
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
from .models import User, Listing

def is_staff(user):
    return user.is_staff

@user_passes_test(is_staff)
def create_bulk_listings(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        listings = data.get('listings', [])
        
        for listing_data in listings:
            user = User.objects.get(id=listing_data['user_id'])
            Listing.objects.create(
                user=user,
                title=listing_data['title'],
                description=listing_data['description'],
                platform=listing_data['platform'],
                followers=listing_data['followers'],
                niche=listing_data['niche'],
                price=listing_data['price'],
                tiktok_shop=listing_data['tiktok_shop'],
                creative_fund=listing_data['creative_fund'],
                youtube_monetization=listing_data['youtube_monetization']
            )
        
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@login_required
def get_mini_lesson(request, lesson_id, mini_lesson_id):
    mini_lesson = get_object_or_404(MiniLesson, id=mini_lesson_id, lesson_id=lesson_id)
    data = {
        'title': mini_lesson.title,
        'description': mini_lesson.description,
        'video_url': mini_lesson.video_url if mini_lesson.video_url else mini_lesson.video_file.url if mini_lesson.video_file else None,
    }
    return JsonResponse(data)

@login_required
def messages_view(request):
    connections = Connection.objects.filter(
        (Q(from_user=request.user) | Q(to_user=request.user)) & Q(accepted=True)
    ).select_related('from_user', 'to_user')
    
    connected_users = [
        conn.to_user if conn.from_user == request.user else conn.from_user
        for conn in connections
    ]
    
    return render(request, 'messages.html', {'connected_users': connected_users})

@login_required
def get_messages(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    messages = Message.objects.filter(
        (Q(sender=request.user, receiver=other_user) | 
         Q(sender=other_user, receiver=request.user))
    ).order_by('timestamp')
    
    message_data = [
        {
            'id': msg.id,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat(),
            'is_sender': msg.sender == request.user
        }
        for msg in messages
    ]
    
    return JsonResponse({'messages': message_data})

@login_required
@require_POST
def send_message(request):
    receiver_id = request.POST.get('receiver_id')
    content = request.POST.get('content')
    
    if not receiver_id or not content:
        return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)
    
    receiver = get_object_or_404(User, id=receiver_id)
    
    # Check if users are connected
    connection_exists = Connection.objects.filter(
        (Q(from_user=request.user, to_user=receiver) | 
         Q(from_user=receiver, to_user=request.user)),
        accepted=True
    ).exists()
    
    if not connection_exists:
        return JsonResponse({'status': 'error', 'message': 'Users are not connected'}, status=403)
    
    message = Message.objects.create(
        sender=request.user,
        receiver=receiver,
        content=content
    )
    
    return JsonResponse({
        'status': 'success',
        'message': {
            'id': message.id,
            'content': message.content,
            'timestamp': message.timestamp.isoformat(),
            'is_sender': True
        }
    })





from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
import os
from django.conf import settings

@staff_member_required
def admin_media(request):
    downloads_dir = os.path.join(settings.MEDIA_ROOT, 'downloads')
    lesson_videos_dir = os.path.join(settings.MEDIA_ROOT, 'lesson_videos')
    uploads_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')

    downloads = [{'name': f, 'path': os.path.join(downloads_dir, f)} 
                 for f in os.listdir(downloads_dir) if os.path.isfile(os.path.join(downloads_dir, f))]
    lesson_videos = [{'name': f, 'path': os.path.join(lesson_videos_dir, f)} 
                     for f in os.listdir(lesson_videos_dir) if os.path.isfile(os.path.join(lesson_videos_dir, f))]
    uploads = [{'name': f, 'path': os.path.join(uploads_dir, f)} 
               for f in os.listdir(uploads_dir) if os.path.isfile(os.path.join(uploads_dir, f))]
    
    return render(request, 'adminmedia.html', {
        'downloads': downloads,
        'lesson_videos': lesson_videos,
        'uploads': uploads,
    })

@staff_member_required
def admin_media_delete(request):
    if request.method == 'POST':
        selected_files = request.POST.getlist('selected_files')
        for file_path in selected_files:
            if os.path.exists(file_path):
                os.remove(file_path)
    return redirect('admin_media')

@staff_member_required
@require_POST
def approve_listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    admin_confirmation = request.POST.get('admin_confirmation')
    
    if admin_confirmation:
        listing.admin_confirmation = admin_confirmation
        listing.is_approved = True
        listing.save()
        
        MarketplaceNotification.objects.create(
            user=listing.user,
            message=f"Your listing '{listing.title}' has been approved."
        )
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Admin confirmation is required'})
    

@login_required
def marketplace_profile(request):
    listings = Listing.objects.filter(user=request.user).order_by('-created_at')
    marketplace_notifications = MarketplaceNotification.objects.filter(user=request.user)
    return render(request, 'marketplaceprofile.html', {
        'listings': listings,
        'marketplace_notifications': marketplace_notifications
    })

@login_required
def edit_listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id, user=request.user)
    if request.method == 'POST':
        form = ListingEditForm(request.POST, instance=listing)
        if form.is_valid():
            form.save()
            messages.success(request, "Listing updated successfully.")
            return redirect('marketplace_profile')
    else:
        form = ListingEditForm(instance=listing)
    return render(request, 'edit_listing.html', {'form': form, 'listing': listing})


