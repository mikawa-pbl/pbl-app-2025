# Create your views here.
import os
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .models import Member
from .models import Product


def index(request):
    products = Product.objects.order_by("-id")  # newest first
    # add formatted_price for template (e.g. "¥1,234")
    for p in products:
        try:
            p.formatted_price = f"¥{int(p.price):,}"
        except Exception:
            p.formatted_price = f"¥{p.price}"
    return render(request, "teams/team_giryulink/index.html", {"products": products})


def members(request):
    qs = Member.objects.all()
    return render(request, "teams/team_giryulink/members.html", {"members": qs})


def product_detail(request, pk):
    """Show product detail page."""
    product = get_object_or_404(Product, pk=pk)
    return render(
        request, "teams/team_giryulink/product_detail.html", {"product": product}
    )


def add_product(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        price_str = request.POST.get("price", "0")
        description = request.POST.get("description", "").strip()
        image_file = request.FILES.get("image")  # 获取上传的文件

        try:
            price = int(price_str)
        except ValueError:
            price = 0

        product = Product(title=title, price=price, description=description)

        # 处理上传的图片文件
        if image_file:
            product.image = image_file

        product.save()

    return redirect("team_giryulink:index")


@require_POST
def delete_product(request, pk):
    """Delete product and its associated image file, then redirect back to index."""
    product = get_object_or_404(Product, pk=pk)
    
    # Delete the image file from the file system if it exists
    if product.image:
        if os.path.isfile(product.image.path):
            os.remove(product.image.path)
    
    product.delete()
    return redirect("team_giryulink:index")
