from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from .models import Product,Category
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
import re
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .decorators import seller_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ProductForm
from .models import Seller, ProductListing, Product,Subcategory,Address
import random
from .models import CartItem, Order, OrderItem
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count
from django.db.models import F, Sum, FloatField
from django.core.mail import send_mail
from .forms import AddressForm
from .models import Address



#from .models import Product


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


def home(request):
    search_query = request.GET.get('search', '')
    selected_category = request.GET.get('category')
    selected_subcategory = request.GET.get('subcategory')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    products = Product.objects.all()

    # Search filter
    if search_query:
        products = products.filter(name__icontains=search_query)

    # Category filter
    if selected_category and selected_category.isdigit():
        products = products.filter(category_id=int(selected_category))

    # Subcategory filter
    if selected_subcategory and selected_subcategory.isdigit():
        products = products.filter(subcategory_id=int(selected_subcategory))

    # Min price filter
    if min_price:
        try:
            min_price = float(min_price)
            products = products.filter(price__gte=min_price)
        except ValueError:
            pass  # Ignore invalid min_price values

    # Max price filter
    if max_price:
        try:
            max_price = float(max_price)
            products = products.filter(price__lte=max_price)
        except ValueError:
            pass  # Ignore invalid max_price values

    categories = Category.objects.all()
    subcategories = Subcategory.objects.filter(category_id=selected_category) if selected_category else []

    cart_item_count = CartItem.objects.filter(user=request.user).count() if request.user.is_authenticated else 0

    context = {
        'products': products if (selected_category or search_query or selected_subcategory or min_price or max_price) else products[:10],
        'categories': categories,
        'subcategories': subcategories,
        'selected_category': int(selected_category) if selected_category and selected_category.isdigit() else None,
        'selected_subcategory': int(selected_subcategory) if selected_subcategory and selected_subcategory.isdigit() else None,
        'search_query': search_query,
        'cart_item_count': cart_item_count
    }

    return render(request, 'home.html', context)




def product_detail(request, id):
    product = Product.objects.get(id=id)
    return render(request, 'product_detail.html', {
        'product':product
    })


@csrf_exempt
def product_autocomplete(request):
    query = request.GET.get('term', '')  # jQuery uses `term` by default
    products = Product.objects.filter(name__icontains=query)[:10]
    results = [product.name for product in products]
    return JsonResponse(results, safe=False)

def about_view(request):
    return render(request, 'about.html')




def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # Validation (same as your existing code)

        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]{4,19}$', username):
            messages.error(request, "Invalid username.")
            return redirect('signup')

        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            messages.error(request, "Invalid email.")
            return redirect('signup')

        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
            messages.error(request, "Weak password.")
            return redirect('signup')

        if password != confirm_password:
            messages.error(request, "Passwords don't match.")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username taken.")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('signup')

        # Generate OTP
        otp = str(random.randint(100000, 999999))

        # Send OTP mail
        send_mail(
            'Your MyShopee Signup OTP',
            f'Hello {username}, your OTP for MyShopee signup is: {otp}',
            'myshopee@gmail.com',
            [email],
            fail_silently=False,
        )

        # Store signup data + OTP in session
        request.session['signup_data'] = {
            'username': username,
            'email': email,
            'password': password,
            'role': request.POST.get('role', 'buyer'),
            'otp': otp
        }

        return redirect('verify_otp')

    return render(request, 'signup.html')

def verify_otp(request):
    signup_data = request.session.get('signup_data')
    if not signup_data:
        return redirect('signup')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')

        if entered_otp == signup_data['otp']:
            # Create user
            user = User.objects.create_user(
                username=signup_data['username'],
                email=signup_data['email'],
                password=signup_data['password']
            )
            user.save()

            profile = user.profile
            profile.role = signup_data['role']
            profile.save()

            # Clean up session data
            del request.session['signup_data']

            messages.success(request, "Account verified and created successfully! Please log in.")
            return redirect('login')

        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, 'verify_otp.html')


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)

    if created:
        cart_item.quantity = quantity
    else:
        cart_item.quantity += quantity 

    cart_item.save()

    total_items = CartItem.objects.filter(user=request.user).count()
    total_price = sum(item.subtotal() for item in CartItem.objects.filter(user=request.user))

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'item_name': product.name,
            'item_quantity': cart_item.quantity,
            'cart_total_items': total_items,
            'cart_total_price': total_price,
        })

    return redirect('cart_detail')


def cart_detail(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.subtotal() for item in cart_items)
    shipping_charge = 80 if cart_items else 0
    final_amount = total_price + shipping_charge
    cart_count = cart_items.count()
    
    addresses = Address.objects.filter(user=request.user)
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'shipping_charge': shipping_charge,
        'final_amount': final_amount,
        'cart_count': cart_count,
        'addresses': addresses, 
    }
    return render(request, 'cart_detail.html', context)

def remove_from_cart(request, product_id):
    CartItem.objects.filter(user=request.user, product_id=product_id).delete()
    return redirect('cart_detail')

def clear_cart(request):
    CartItem.objects.filter(user=request.user).delete()
    return redirect('cart_detail')

# views.py

def decrease_quantity(request, product_id):
    cart_item = get_object_or_404(CartItem, user=request.user, product_id=product_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return cart_json_response(request, product_id)


def increase_quantity(request, product_id):
    cart_item = get_object_or_404(CartItem, user=request.user, product_id=product_id)
    cart_item.quantity += 1
    cart_item.save()
    return cart_json_response(request, product_id)


def cart_json_response(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_items = CartItem.objects.filter(user=request.user)

    try:
        cart_item = CartItem.objects.get(user=request.user, product=product)
        quantity = cart_item.quantity
        subtotal = cart_item.subtotal()
    except CartItem.DoesNotExist:
        quantity = 0
        subtotal = 0

    total_price = sum(item.subtotal() for item in cart_items)
    shipping_charge = 80 if cart_items else 0
    final_amount = total_price + shipping_charge

    return JsonResponse({
        'success': True,
        'quantity': quantity,
        'subtotal': subtotal,
        'total_price': total_price,
        'final_amount': final_amount,
    })



@login_required
def add_product(request):
    if request.user.profile.role != 'seller':
        return redirect('home')

    seller = get_object_or_404(Seller, user=request.user)

    if request.method == 'POST':
        name = request.POST['name']
        price = request.POST['price']
        discount_price = request.POST.get('discount_price') or None
        stock = request.POST['stock']
        description = request.POST['description']
        image = request.FILES.get('image')
        category_id = request.POST['category']
        subcategory_id = request.POST.get('subcategory') or None

        category = Category.objects.get(id=category_id)
        subcategory = Subcategory.objects.get(id=subcategory_id) if subcategory_id else None

        product = Product.objects.create(
            name=name,
            price=price,
            discount_price=discount_price,
            stock=stock,
            description=description,
            image=image,
            category=category,
            subcategory=subcategory
        )

        ProductListing.objects.create(
            product=product,
            seller=seller,
            price=price,
            stock=stock,
            is_approved=False
        )

        messages.success(request, "Product submitted for admin approval.")
        return redirect('seller_dashboard')

    categories = Category.objects.all()
    subcategories = Subcategory.objects.all()

    return render(request, 'add_product.html', {
        'categories': categories,
        'subcategories': subcategories
    })


def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('product_list')

@login_required
def seller_dashboard(request):
    if request.user.profile.role != 'seller':
        return redirect('home')

    seller = get_object_or_404(Seller, user=request.user)

    approved_listings = ProductListing.objects.filter(seller=seller, is_approved=True)
    seller_products = approved_listings.values_list('product', flat=True)

    order_items = OrderItem.objects.filter(listing__in=approved_listings)

    total_orders = order_items.values('order').distinct().count()
    total_sales = order_items.aggregate(
        total=Sum(F('price') * F('quantity'), output_field=FloatField())
    )['total'] or 0

    total_products = approved_listings.count()

    context = {
        'listings': approved_listings,
        'total_orders': total_orders,
        'total_sales': total_sales,
        'total_products': total_products,
    }

    return render(request, 'seller_dashboard.html', context)

@login_required
def edit_listing(request, listing_id):
    listing = get_object_or_404(ProductListing, id=listing_id)

    if request.user != listing.seller.user:
        return redirect('seller_dashboard')

    if request.method == 'POST':
        listing.price = request.POST.get('price')
        listing.stock = request.POST.get('stock')
        listing.save()
        return redirect('seller_dashboard')

    return render(request, 'accounts/edit_listing.html', {'listing': listing})

@login_required
def delete_listing(request, listing_id):
    listing = get_object_or_404(ProductListing, id=listing_id)

    if request.user != listing.seller.user:
        return redirect('seller_dashboard')

    listing.delete()
    return redirect('seller_dashboard')

def generate_order_number():
    return 'ORD' + str(random.randint(10000, 99999))

from django.http import JsonResponse
import traceback

def place_order(request):
    if request.method == 'POST':
        try:
            data = request.POST

            address_id = data.get('address_id')
            if address_id:
                address = get_object_or_404(Address, id=address_id, user=request.user)
            else:
                address = Address.objects.create(
                    user=request.user,
                    full_name=data.get('full_name'),
                    phone_number=data.get('phone_number'),
                    address_line_1=data.get('address_line_1'),
                    city=data.get('city'),
                    state=data.get('state'),
                    pincode=data.get('pincode'),
                    is_default=True
                )

            cart_items = CartItem.objects.filter(user=request.user)
            if not cart_items.exists():
                return JsonResponse({'success': False, 'message': 'Cart is empty!'})

            total_price = 0
            order = Order.objects.create(
                user=request.user,
                order_number=generate_order_number(),
                total_price=0,
                delivery_date=timezone.now() + timedelta(days=4),
                address=address
            )

            for item in cart_items:
                subtotal = item.product.price * item.quantity
                total_price += subtotal

                listing = ProductListing.objects.filter(product=item.product, is_approved=True).first()

                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    listing=listing,
                    quantity=item.quantity,
                    price=item.product.price
                )

            order.total_price = total_price
            order.save()

            cart_items.delete()

            return JsonResponse({
                'success': True,
                'order_number': order.order_number,
                'delivery_date': order.delivery_date.strftime('%d %b %Y')
            })

        except Exception as e:
            print("Error in placing order:", e)
            traceback.print_exc()
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request'})


def chatbot_response(request):
    stage = request.GET.get('stage')
    selected_id = request.GET.get('id')

    response = {}

    if not stage:
        categories = Category.objects.all()
        response['message'] = "What category are you interested in?"
        response['options'] = [{'label': c.name, 'id': c.id, 'stage': 'subcategory'} for c in categories]

    elif stage == 'subcategory':
        subcategories = Subcategory.objects.filter(category_id=selected_id)
        response['message'] = "Great! Choose a subcategory:"
        response['options'] = [{'label': s.name, 'id': s.id, 'stage': 'product'} for s in subcategories]

    elif stage == 'product':
        products = Product.objects.filter(subcategory_id=selected_id)
        response['message'] = "Here are some products you might like:"
        response['options'] = [{'label': p.name, 'id': p.id, 'price': str(p.price)} for p in products]

    return JsonResponse(response)


def get_categories(request):
    categories = list(Category.objects.values('id', 'name'))
    return JsonResponse({'categories': categories})

def get_subcategories(request, category_id):
    subcategories = list(Subcategory.objects.filter(category_id=category_id).values('id', 'name'))
    return JsonResponse({'subcategories': subcategories})

def get_products(request, subcategory_id):
    products = list(Product.objects.filter(subcategory_id=subcategory_id).values('name', 'price'))
    return JsonResponse({'products': products})


def get_price_range(request, subcategory_id):
    products = Product.objects.filter(subcategory_id=subcategory_id)
    if not products.exists():
        return JsonResponse({'min_price': None})
    
    min_price = products.order_by('price').first().price
    return JsonResponse({'min_price': min_price})

@csrf_exempt
def log_chat_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ChatbotLog.objects.create(
            session_id=data.get('session_id'),
            page=data.get('page'),
            message=data.get('message'),
            message_by=data.get('message_by'),
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        return JsonResponse({'status': 'success'})
    
@login_required
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('cart_detail')  # or 'checkout' if you're building that
    else:
        form = AddressForm()
    
    return render(request, 'add_address.html', {'form': form})