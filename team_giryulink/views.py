# Create your views here.
import os
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Member, Product, GiryulinkUser
from .forms import RegistrationForm, LoginForm
import django.db.models as models


# Session helper functions
def get_current_user(request):
    """Get the currently logged-in user from session"""
    user_id = request.session.get('giryulink_user_id')
    if user_id:
        try:
            return GiryulinkUser.objects.get(id=user_id)
        except GiryulinkUser.DoesNotExist:
            pass
    return None


def login_required(view_func):
    """Decorator to require login for a view"""
    def wrapper(request, *args, **kwargs):
        if not get_current_user(request):
            messages.warning(request, 'ログインが必要です。')
            return redirect('team_giryulink:login')
        return view_func(request, *args, **kwargs)
    return wrapper


def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Auto login after registration
            request.session['giryulink_user_id'] = user.id
            messages.success(request, '登録が完了しました！')
            return redirect('team_giryulink:index')
    else:
        form = RegistrationForm()
    
    return render(request, 'teams/team_giryulink/register.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            try:
                user = GiryulinkUser.objects.get(email=email)
                if user.check_password(password):
                    request.session['giryulink_user_id'] = user.id
                    messages.success(request, f'ようこそ {user.name or user.email}さん！')
                    return redirect('team_giryulink:index')
                else:
                    messages.error(request, 'メールアドレスまたはパスワードが正しくありません。')
            except GiryulinkUser.DoesNotExist:
                messages.error(request, 'メールアドレスまたはパスワードが正しくありません。')
    else:
        form = LoginForm()
    
    return render(request, 'teams/team_giryulink/login.html', {'form': form})


def logout_view(request):
    """User logout view"""
    if 'giryulink_user_id' in request.session:
        del request.session['giryulink_user_id']
    messages.success(request, 'ログアウトしました。')
    return redirect('team_giryulink:index')

def index(request):
    # Get current user
    current_user = get_current_user(request)
    
    # Get search query from GET parameters
    search_query = request.GET.get('search', '').strip()
    
    # Filter products by search query if provided
    if search_query:
        products = Product.objects.filter(
            models.Q(title__icontains=search_query) | 
            models.Q(description__icontains=search_query)
        ).order_by("-id")
    else:
        products = Product.objects.order_by("-id")  # newest first
    
    # add formatted_price for template (e.g. "¥1,234")
    for p in products:
        try:
            p.formatted_price = f"¥{int(p.price):,}"
        except Exception:
            p.formatted_price = f"¥{p.price}"
    
    return render(request, "teams/team_giryulink/index.html", {
        "products": products,
        "search_query": search_query,
        "current_user": current_user,
    })


def members(request):
    qs = Member.objects.all()
    return render(request, "teams/team_giryulink/members.html", {"members": qs})


@login_required
def add_product(request):
    if request.method == "POST":
        current_user = get_current_user(request)
        
        title = request.POST.get("title", "").strip()
        price_str = request.POST.get("price", "0")
        description = request.POST.get("description", "").strip()
        image_file = request.FILES.get("image")  # 获取上传的文件

        try:
            price = int(price_str)
        except ValueError:
            price = 0

        product = Product(
            title=title, 
            price=price, 
            description=description,
            user=current_user
        )

        # 处理上传的图片文件
        if image_file:
            product.image = image_file

        product.save()
        messages.success(request, '商品が追加されました！')

    return redirect("team_giryulink:index")


@login_required
@require_POST
def delete_product(request, pk):
    """Delete product and its associated image file, then redirect back to index.
    Only the user who created the product can delete it."""
    current_user = get_current_user(request)
    product = get_object_or_404(Product, pk=pk)
    
    # Check if current user is the owner
    if product.user_id != current_user.id:
        messages.error(request, 'この商品を削除する権限がありません。')
        return redirect("team_giryulink:index")
    
    # Delete the image file from the file system if it exists
    if product.image:
        if os.path.isfile(product.image.path):
            os.remove(product.image.path)
    
    product.delete()
    messages.success(request, '商品が削除されました。')
    return redirect("team_giryulink:index")


@login_required
def my_products(request):
    """Show products created by current user"""
    current_user = get_current_user(request)
    products = Product.objects.filter(user=current_user).order_by("-id")
    
    # add formatted_price for template
    for p in products:
        try:
            p.formatted_price = f"¥{int(p.price):,}"
        except Exception:
            p.formatted_price = f"¥{p.price}"
    
    return render(request, "teams/team_giryulink/my_products.html", {
        "products": products,
        "current_user": current_user,
    })


@login_required
@require_POST
def purchase_product(request, pk):
    """Purchase a product"""
    from django.utils import timezone
    from .models import ChatRoom
    
    current_user = get_current_user(request)
    product = get_object_or_404(Product, pk=pk)
    
    # Check if product is already sold
    if product.is_sold:
        messages.error(request, 'この商品は既に購入されています。')
        return redirect("team_giryulink:index")
    
    # Check if user is trying to buy their own product
    if product.user_id == current_user.id:
        messages.error(request, '自分の商品は購入できません。')
        return redirect("team_giryulink:index")
    
    # Mark product as purchased
    product.buyer = current_user
    product.purchased_at = timezone.now()
    product.save()
    
    # Create chat room for transaction
    chat_room = ChatRoom.objects.create(
        product=product,
        seller=product.user,
        buyer=current_user
    )
    
    messages.success(request, f'「{product.title}」を購入しました！チャットで出品者と連絡できます。')
    return redirect("team_giryulink:chat_room", room_id=chat_room.id)


@login_required
def chat_list(request):
    """Show all chat rooms for current user"""
    from .models import ChatRoom
    current_user = get_current_user(request)
    
    # Get chats where user is seller or buyer
    chat_rooms = ChatRoom.objects.filter(
        models.Q(seller=current_user) | models.Q(buyer=current_user)
    ).select_related('product', 'seller', 'buyer')
    
    return render(request, "teams/team_giryulink/chat_list.html", {
        "chat_rooms": chat_rooms,
        "current_user": current_user,
    })


@login_required
def chat_room(request, room_id):
    """Chat room for a transaction"""
    from .models import ChatRoom, ChatMessage
    
    current_user = get_current_user(request)
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    
    # Check if user is part of this chat
    if chat_room.seller_id != current_user.id and chat_room.buyer_id != current_user.id:
        messages.error(request, 'このチャットにアクセスできません。')
        return redirect("team_giryulink:index")
    
    # Handle message sending
    if request.method == "POST":
        message_text = request.POST.get("message", "").strip()
        if message_text:
            ChatMessage.objects.create(
                chat_room=chat_room,
                sender=current_user,
                message=message_text
            )
            return redirect("team_giryulink:chat_room", room_id=room_id)
    
    # Mark messages as read
    ChatMessage.objects.filter(
        chat_room=chat_room
    ).exclude(sender=current_user).update(is_read=True)
    
    # Get all messages
    messages_list = chat_room.messages.all().select_related('sender')
    
    # Determine other user
    other_user = chat_room.seller if chat_room.buyer_id == current_user.id else chat_room.buyer
    
    return render(request, "teams/team_giryulink/chat_room.html", {
        "chat_room": chat_room,
        "messages_list": messages_list,
        "current_user": current_user,
        "other_user": other_user,
    })


def product_detail(request, product_id):
    """Product detail page with comments"""
    from .models import ProductComment
    
    product = get_object_or_404(Product, id=product_id)
    current_user = get_current_user(request)
    
    # Handle comment submission
    if request.method == "POST":
        if not current_user:
            messages.warning(request, "コメントするにはログインが必要です。")
            return redirect("team_giryulink:login")
        
        comment_text = request.POST.get("comment", "").strip()
        if comment_text:
            ProductComment.objects.create(
                product=product,
                user=current_user,
                text=comment_text
            )
            messages.success(request, "コメントを投稿しました。")
            return redirect("team_giryulink:product_detail", product_id=product_id)
    
    comments = product.comments.all().select_related('user')
    
    return render(request, "teams/team_giryulink/product_detail.html", {
        "product": product,
        "comments": comments,
        "current_user": current_user,
    })


def history(request):
    """Purchase history page"""
    current_user = get_current_user(request)
    if not current_user:
        messages.warning(request, "ログインが必要です。")
        return redirect("team_giryulink:login")
    
    # Get products user has purchased
    purchased = Product.objects.filter(buyer=current_user).order_by('-purchased_at')
    
    return render(request, "teams/team_giryulink/history.html", {
        "purchased_products": purchased,
        "current_user": current_user,
    })


def add_product_page(request):
    """Add product page"""
    current_user = get_current_user(request)
    if not current_user:
        messages.warning(request, "ログインが必要です。")
        return redirect("team_giryulink:login")
    
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        price = request.POST.get("price", "0")
        description = request.POST.get("description", "").strip()
        image = request.FILES.get("image")
        
        if title and price:
            Product.objects.create(
                title=title,
                price=int(price),
                description=description,
                image=image,
                user=current_user
            )
            messages.success(request, "商品を出品しました。")
            return redirect("team_giryulink:index")
        else:
            messages.error(request, "タイトルと価格は必須です。")
    
    return render(request, "teams/team_giryulink/add_product.html", {
        "current_user": current_user,
    })


def my_page(request):
    """My page - redirects to my_products"""
    return redirect("team_giryulink:my_products")


@login_required
def edit_product(request, pk):
    """Edit a product"""
    from .forms import ProductEditForm
    
    current_user = get_current_user(request)
    product = get_object_or_404(Product, pk=pk)
    
    # Check if current user is the owner
    if product.user_id != current_user.id:
        messages.error(request, 'この商品を編集する権限がありません。')
        return redirect("team_giryulink:my_products")
    
    # Check if product is already sold
    if product.is_sold:
        messages.error(request, '購入済みの商品は編集できません。')
        return redirect("team_giryulink:my_products")
    
    if request.method == 'POST':
        form = ProductEditForm(request.POST, request.FILES)
        if form.is_valid():
            product.title = form.cleaned_data['title']
            product.price = form.cleaned_data['price']
            product.description = form.cleaned_data['description']
            
            # Handle image update
            if 'image' in request.FILES:
                # Delete old image if it exists
                if product.image:
                    if os.path.isfile(product.image.path):
                        os.remove(product.image.path)
                product.image = request.FILES['image']
            
            product.save()
            messages.success(request, '商品情報を更新しました。')
            return redirect("team_giryulink:my_products")
    else:
        # Pre-fill form with existing data
        form = ProductEditForm(initial={
            'title': product.title,
            'price': product.price,
            'description': product.description,
        })
    
    return render(request, "teams/team_giryulink/edit_product.html", {
        "form": form,
        "product": product,
        "current_user": current_user,
    })
