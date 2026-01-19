from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import MyPage, Member, Community, Post, Comment, Message, CommunityReadStatus
from .forms import MyPageEditForm, UserRegisterForm, LoginForm, CommunityForm, PostForm, CommentForm, MessageForm

def index(request):
    # ログイン済みならホームへリダイレクト
    if 'user_id' in request.session:
        return redirect('nanakorobiyaoki:home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user_id = form.cleaned_data['user_id']
            password = form.cleaned_data['password']
            
            try:
                user = MyPage.objects.get(user_id=user_id, password=password)
                request.session['user_id'] = user.user_id
                return redirect('nanakorobiyaoki:home')
            except MyPage.DoesNotExist:
                form.add_error(None, 'ユーザーIDまたはパスワードが間違っています。')
    else:
        form = LoginForm()

    return render(request, 'teams/nanakorobiyaoki/index.html', {'form': form})

def home(request):
    if 'user_id' not in request.session:
        return redirect('nanakorobiyaoki:index')
        
    # 全コミュニティ一覧 (community_listの内容も統合)
    all_communities = Community.objects.all().order_by('-created_at')
            
    return render(request, 'teams/nanakorobiyaoki/home.html', {
        'communities': all_communities
    })

def members(request):
    qs = Member.objects.using('nanakorobiyaoki').all()  # ← team_terrace DBを明示
    return render(request, 'teams/nanakorobiyaoki/members.html', {'members': qs})

def login_view(request):
    return redirect('nanakorobiyaoki:index')

def logout_view(request):
    request.session.flush() # セッションをクリア
    return redirect('nanakorobiyaoki:index')


def mypage(request):
    qs = MyPage.objects.all()
    return render(request, 'teams/nanakorobiyaoki/mypage.html', {'mypage': qs})

def user_profile(request, user_id):
    if 'user_id' not in request.session:
        return redirect('nanakorobiyaoki:index')

    user_data = get_object_or_404(MyPage, user_id=user_id)
    context = {
        'user': user_data,
    }
    return render(request, 'teams/nanakorobiyaoki/mypage.html', context)

def users(request):
    all_users = MyPage.objects.all()
    context = {
        'users': all_users
    }
    return render(request, 'teams/nanakorobiyaoki/users.html', context)

def user_profile_edit(request, user_id):
    user_data = get_object_or_404(MyPage, user_id=user_id)
    if request.method == 'POST':
        form = MyPageEditForm(request.POST, request.FILES, instance=user_data)
        if form.is_valid():
            form.save()
            return redirect('nanakorobiyaoki:user_profile', user_id=user_data.user_id)
    else:
        form = MyPageEditForm(instance=user_data)

    context = {
        'form': form,
        'user': user_data,
    }
    return render(request, 'teams/nanakorobiyaoki/user_profile_edit.html', context)

def user_register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            request.session['user_id'] = user.user_id
            return redirect('nanakorobiyaoki:user_register_confirm', user_id=user.user_id)
    else:
        form = UserRegisterForm()
    return render(request, 'teams/nanakorobiyaoki/user_register.html', {'form': form})

def user_register_confirm(request, user_id):
    if 'user_id' not in request.session:
        return redirect('nanakorobiyaoki:index')
    user = get_object_or_404(MyPage, user_id=user_id)
    if user.user_id != request.session['user_id']:
         return redirect('nanakorobiyaoki:index')
    return render(request, 'teams/nanakorobiyaoki/user_register_confirm.html', {'user': user})

def community_create(request):
    if 'user_id' not in request.session:
        return redirect('nanakorobiyaoki:index')
    if request.method == 'POST':
        form = CommunityForm(request.POST, request.FILES)
        if form.is_valid():
            community = form.save(commit=False)
            community.save()
            user = get_object_or_404(MyPage, user_id=request.session['user_id'])
            community.members.add(user)
            return redirect('nanakorobiyaoki:home')
    else:
        form = CommunityForm()
    return render(request, 'teams/nanakorobiyaoki/community_form.html', {'form': form})

def community_detail(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    posts = community.posts.all().order_by('-created_at')
    is_member = False
    if 'user_id' in request.session:
        user = get_object_or_404(MyPage, user_id=request.session['user_id'])
        if user in community.members.all():
            is_member = True
            # 既読状態を更新または作成
            CommunityReadStatus.objects.update_or_create(
                user=user,
                community=community
            )
    return render(request, 'teams/nanakorobiyaoki/community_detail.html', {
        'community': community, 
        'posts': posts,
        'is_member': is_member,
    })

def community_members(request, community_id):
    if 'user_id' not in request.session:
        return redirect('nanakorobiyaoki:index')
    community = get_object_or_404(Community, id=community_id)
    members = community.members.all()
    return render(request, 'teams/nanakorobiyaoki/community_member_list.html', {
        'community': community,
        'members': members,
    })

def community_join(request, community_id):
    if 'user_id' not in request.session:
        return redirect('nanakorobiyaoki:index')
    community = get_object_or_404(Community, id=community_id)
    user = get_object_or_404(MyPage, user_id=request.session['user_id'])
    community.members.add(user)
    return redirect('nanakorobiyaoki:community_detail', community_id=community_id)

def community_leave(request, community_id):
    if 'user_id' not in request.session:
        return redirect('nanakorobiyaoki:index')
    community = get_object_or_404(Community, id=community_id)
    user = get_object_or_404(MyPage, user_id=request.session['user_id'])
    community.members.remove(user)
    return redirect('nanakorobiyaoki:community_detail', community_id=community_id)

def post_create(request, community_id):
    if 'user_id' not in request.session:
        return redirect('nanakorobiyaoki:index')
    community = get_object_or_404(Community, id=community_id)
    user = get_object_or_404(MyPage, user_id=request.session['user_id'])
    if user not in community.members.all():
        return redirect('nanakorobiyaoki:community_detail', community_id=community_id)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.community = community
            post.author = user
            post.save()
    return redirect('nanakorobiyaoki:community_detail', community_id=community_id)

def post_delete(request, post_id):
    if 'user_id' not in request.session:
        return redirect('nanakorobiyaoki:index')
    post = get_object_or_404(Post, id=post_id)
    if post.author.user_id != request.session['user_id']:
        return redirect('nanakorobiyaoki:community_detail', community_id=post.community.id)
    community_id = post.community.id
    post.delete()
    return redirect('nanakorobiyaoki:community_detail', community_id=community_id)

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all().order_by('created_at')
    comment_form = CommentForm()
    return render(request, 'teams/nanakorobiyaoki/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form
    })

def comment_create(request, post_id):
    if 'user_id' not in request.session:
        return redirect('nanakorobiyaoki:index')
    post = get_object_or_404(Post, id=post_id)
    user = get_object_or_404(MyPage, user_id=request.session['user_id'])
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = user
            comment.save()
    return redirect('nanakorobiyaoki:post_detail', post_id=post_id)

def community_list(request):
    query = request.GET.get('q')
    if query:
        communities = Community.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).distinct().order_by('-created_at')
    else:
        communities = Community.objects.all().order_by('-created_at')
    return render(request, 'teams/nanakorobiyaoki/community_list.html', {
        'communities': communities,
    })

def message_inbox(request):
    if 'user_id' not in request.session:
        return redirect('nanakorobiyaoki:index')
    
    current_user = get_object_or_404(MyPage, user_id=request.session['user_id'])
    
    # 全てのメッセージの相手を抽出
    sent_to = Message.objects.filter(sender=current_user).values_list('receiver', flat=True)
    received_from = Message.objects.filter(receiver=current_user).values_list('sender', flat=True)
    partner_ids = set(list(sent_to) + list(received_from))
    
    partners_info = []
    for pid in partner_ids:
        partner = MyPage.objects.get(id=pid)
        # 最新のメッセージを1件取得
        latest_msg = Message.objects.filter(
            (Q(sender=current_user) & Q(receiver=partner)) |
            (Q(sender=partner) & Q(receiver=current_user))
        ).order_by('-timestamp').first()
        
        # この相手からの未読メッセージ件数を取得
        unread_count = Message.objects.filter(sender=partner, receiver=current_user, is_read=False).count()
        
        partners_info.append({
            'partner': partner,
            'latest_message': latest_msg,
            'unread_count': unread_count
        })
    
    # 最新メッセージの時刻順にソート
    partners_info.sort(key=lambda x: x['latest_message'].timestamp if x['latest_message'] else 0, reverse=True)
    
    return render(request, 'teams/nanakorobiyaoki/message_inbox.html', {
        'partners_info': partners_info,
    })

def chat_room(request, partner_user_id):
    if 'user_id' not in request.session:
        return redirect('nanakorobiyaoki:index')
    current_user = get_object_or_404(MyPage, user_id=request.session['user_id'])
    partner = get_object_or_404(MyPage, user_id=partner_user_id)
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = current_user
            message.receiver = partner
            message.save()
            return redirect('nanakorobiyaoki:chat_room', partner_user_id=partner_user_id)
    else:
        form = MessageForm()
    messages = Message.objects.filter(
        (Q(sender=current_user) & Q(receiver=partner)) |
        (Q(sender=partner) & Q(receiver=current_user))
    ).order_by('timestamp')
    Message.objects.filter(sender=partner, receiver=current_user, is_read=False).update(is_read=True)
    return render(request, 'teams/nanakorobiyaoki/chat_room.html', {
        'partner': partner,
        'messages': messages,
        'form': form,
    })
