from .models import MyPage, Message

def nanakorobiyaoki_context(request):
    if 'user_id' in request.session:
        try:
            user = MyPage.objects.get(user_id=request.session['user_id'])
            joined_communities = user.communities.all().order_by('-created_at')
            unread_count = Message.objects.filter(receiver=user, is_read=False).count()
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
