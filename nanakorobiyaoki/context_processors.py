from .models import MyPage, Message, Post, CommunityReadStatus

def nanakorobiyaoki_context(request):
    if 'user_id' in request.session:
        try:
            user = MyPage.objects.get(user_id=request.session['user_id'])
            joined_communities = list(user.communities.all().order_by('-created_at'))
            unread_count = Message.objects.filter(receiver=user, is_read=False).count()
            
            # 各コミュニティの未読投稿数を計算
            for community in joined_communities:
                read_status = CommunityReadStatus.objects.filter(user=user, community=community).first()
                if read_status:
                    community.unread_posts_count = Post.objects.filter(
                        community=community,
                        created_at__gt=read_status.last_read_at
                    ).exclude(author=user).count()
                else:
                    # 一度も見ていない場合は全ての投稿（自分以外）を未読とする
                    community.unread_posts_count = Post.objects.filter(
                        community=community
                    ).exclude(author=user).count()

            return {
                'joined_communities': joined_communities,
                'unread_messages_count': unread_count,
            }
        except MyPage.DoesNotExist:
            pass
    return {
        'joined_communities': [],
        'unread_messages_count': 0,
    }
