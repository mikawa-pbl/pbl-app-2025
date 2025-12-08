# Create your views here.
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .models import Member
from .models import Product

def index(request):
    products = Product.objects.order_by('-id')  # newest first
    # add formatted_price for template (e.g. "¥1,234")
    for p in products:
        try:
            p.formatted_price = f"¥{int(p.price):,}"
        except Exception:
            p.formatted_price = f"¥{p.price}"
    return render(request, 'teams/team_giryulink/index.html', {'products': products})

def members(request):
    qs = Member.objects.using('team_giryulink').all()  # ← Chỉ định rõ DB team_giryulink
    return render(request, 'teams/team_giryulink/members.html', {'members': qs})

def product_detail(request, pk):
    """Show product detail page."""
    product = get_object_or_404(Product.objects.using("team_giryulink"), pk=pk)
    return render(request, 'teams/team_giryulink/product_detail.html', {'product': product})

def add_product(request):
    """Handle POST from index form and create Product, then redirect to index or detail."""
    if request.method != 'POST':
        return redirect('team_giryulink:index')
    title = request.POST.get('title', '').strip()
    price = request.POST.get('price', '').strip()
    image = request.POST.get('image', '').strip() or 'https://via.placeholder.com/600x400?text=No+Image'
    description = request.POST.get('description', '').strip()

    if not title:
        # minimal validation: redirect back (you can add messages)
        return redirect('team_giryulink:index')

    try:
        price_val = int(price) if price else 0
    except ValueError:
        price_val = 0

    prod = Product.objects.create(title=title, price=price_val, image=image, description=description)
    # redirect to product detail after creation
    return redirect('team_giryulink:product_detail', pk=prod.pk)

@require_POST
def delete_product(request, pk):
    """Delete product and redirect back to index."""
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect('team_giryulink:index')
