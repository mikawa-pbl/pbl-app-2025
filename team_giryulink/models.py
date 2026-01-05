# Create your models here.
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password

def validate_tut_email(value):
    """Validate that email ends with @tut.jp"""
    if not value.endswith('@tut.jp'):
        raise ValidationError('メールアドレスは@tut.jpドメインを使用してください。')

class GiryulinkUser(models.Model):
    """Custom user model for team_giryulink app"""
    email = models.EmailField(unique=True, validators=[validate_tut_email])
    password = models.CharField(max_length=128)  # Will store hashed password
    name = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def set_password(self, raw_password):
        """Hash and set the password"""
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Check if the provided password is correct"""
        return check_password(raw_password, self.password)
    
    def __str__(self):
        return self.email

class Member(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

class Product(models.Model):
    title = models.CharField(max_length=200)
    price = models.IntegerField(default=0)
    image = models.ImageField(upload_to="team_giryulink/products/", blank=True, null=True)
    description = models.TextField(blank=True)
    user = models.ForeignKey(GiryulinkUser, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    buyer = models.ForeignKey(GiryulinkUser, on_delete=models.SET_NULL, related_name='purchased_products', null=True, blank=True)
    purchased_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title
    
    @property
    def is_sold(self):
        """Check if product is already sold"""
        return self.buyer is not None

class ChatRoom(models.Model):
    """Chat room for a product transaction"""
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='chat_room')
    seller = models.ForeignKey(GiryulinkUser, on_delete=models.CASCADE, related_name='seller_chats')
    buyer = models.ForeignKey(GiryulinkUser, on_delete=models.CASCADE, related_name='buyer_chats')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Chat: {self.product.title} - {self.seller.email} & {self.buyer.email}"


class ChatMessage(models.Model):
    """Individual message in a chat room"""
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(GiryulinkUser, on_delete=models.CASCADE, related_name='sent_messages')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.email}: {self.message[:50]}"


class ProductComment(models.Model):
    """Comment on a product"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(GiryulinkUser, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} on {self.product.title}"
