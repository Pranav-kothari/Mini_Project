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
from django.shortcuts import render, redirect
from .forms import ProductForm
from .forms import ProductReviewForm
from .models import Seller, ProductListing, Product,Subcategory,Address,Order,ProductReview
import random
from .models import CartItem, Order, OrderItem
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count
from django.db.models import F, Sum, FloatField
from django.core.mail import send_mail
from .forms import AddressForm
from .models import Address
import razorpay
from .forms import ProfileForm
import pandas as pd
from openpyxl.drawing.image import Image as ExcelImage
from io import BytesIO
from django.core.files.base import ContentFile
from django.db.models import Q
from django.db import models
from django.utils.timezone import now
from .models import WishlistRequest
from .forms import WishlistRequestForm
from django.db.models import OuterRef, Exists
from django.shortcuts import render, redirect, get_object_or_404

client = razorpay.Client(auth=("rzp_test_Ai6oeBbFCLdyQ7", "D6aHM59vpvwEo267Yzyv0xhW"))

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

    approved_listings = ProductListing.objects.filter(
        product=OuterRef('pk'),
        supervisor_status='approved',
        admin_status='approved'
    )

    products = Product.objects.annotate(
        has_approved_listing=Exists(approved_listings)
    ).filter(has_approved_listing=True)

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




def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user = request.user

    has_purchased = False
    has_reviewed = False

    if user.is_authenticated:
        has_purchased = OrderItem.objects.filter(order__user=user, product=product).exists()
        has_reviewed = ProductReview.objects.filter(user=user, product=product).exists()

    reviews = ProductReview.objects.filter(product=product)

    context = {
        'product': product,
        'has_purchased': has_purchased,
        'has_reviewed': has_reviewed,
        'reviews': reviews,
    }
    return render(request, 'product_detail.html', context)




@csrf_exempt
def product_autocomplete(request):
    query = request.GET.get('term', '')
    products = Product.objects.filter(name__icontains=query)[:10]
    results = [{'label': product.name, 'value': product.name} for product in products]
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



def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('product_list')



@login_required
def seller_dashboard(request):
    seller = Seller.objects.get(user=request.user)

    # Show all except rejected
    listings = ProductListing.objects.filter(seller=seller).exclude(
        Q(supervisor_status='rejected') | Q(admin_status='rejected')
    )

    # Recently rejected listings (within 1 day)
    rejected_listings = ProductListing.objects.filter(seller=seller).filter(
        Q(supervisor_status='rejected') | Q(admin_status='rejected'),
        listed_date__gte=now() - timedelta(days=1)
    )

    total_orders = Order.objects.filter(items__listing__seller=seller).count()
    total_sales = OrderItem.objects.filter(listing__seller=seller).aggregate(
        total=models.Sum('price'))['total'] or 0
    total_products = ProductListing.objects.filter(seller=seller).count()

    # ✅ NEW: Fetch approved wishlist requests
    approved_wishlist = WishlistRequest.objects.filter(status='approved')

    return render(request, 'seller_dashboard.html', {
        'listings': listings,
        'rejected_listings': rejected_listings,
        'total_orders': total_orders,
        'total_sales': total_sales,
        'total_products': total_products,
        'approved_wishlist': approved_wishlist,  # ✅ pass to template
    })


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

                listing = ProductListing.objects.filter(product=item.product, status='approved').first()

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
        try:
            data = json.loads(request.body.decode('utf-8'))
            user_message = data.get('message', '')
            
            # You can later store it or do more, but for now:
            print(f"User message received: {user_message}")

            return JsonResponse({'status': 'success', 'message': 'Logged successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'error': 'Only POST allowed'}, status=405)

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






@csrf_exempt
def create_payment_order(request):
    if request.method == 'POST':
        try:
            # Read amount from POST data (sent via AJAX)
            amount_in_rupees = request.POST.get('total_amount')
            
            if not amount_in_rupees:
                return JsonResponse({'success': False, 'message': 'Cart amount missing'})

            # Convert rupees to paise for Razorpay
            amount = int(float(amount_in_rupees) * 100)

            # Create Razorpay order
            payment = client.order.create({
                "amount": amount,
                "currency": "INR",
                "payment_capture": '1'
            })

            # Optionally fetch other form fields if you need (like full name, phone)
            customer_name = request.POST.get('full_name', 'Guest User')
            customer_phone = request.POST.get('phone_number', '9999999999')
            customer_email = 'test@example.com'  # if you had email input

            # Generate order number (real projects: use a model or UUID)
            import random
            order_number = 'ORD' + str(random.randint(1000, 9999))

            return JsonResponse({
                'success': True,
                'razorpay_order_id': payment['id'],
                'amount': amount,
                'customer_name': customer_name,
                'customer_email': customer_email,
                'customer_phone': customer_phone,
                'order_number': order_number
            })

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def order_success(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number)
        order_items = order.items.all()

        total_items = order_items.count()
        grand_total = sum(item.subtotal() for item in order_items)

        context = {
            'order_number': order_number,
            'order': order,
            'order_items': order_items,
            'total_items': total_items,
            'grand_total': grand_total
        }
        return render(request, 'order_success.html', context)

    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('home')


def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date').prefetch_related('items__product')
    return render(request, 'orders.html', {'orders': orders})

def my_profile(request):
    return render(request, 'my_profile.html')


def edit_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('my_profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'edit_profile.html', {'form': form})

@login_required
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('my_profile')
    else:
        form = AddressForm()
    return render(request, 'add_address.html', {'form': form})

@login_required
def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect('my_profile')
    else:
        form = AddressForm(instance=address)
    return render(request, 'edit_address.html', {'form': form})

@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    return redirect('my_profile')



def add_product(request):
    if request.user.profile.role != 'seller':
        return redirect('home')

    seller = get_object_or_404(Seller, user=request.user)
    categories = Category.objects.all()
    subcategories = Subcategory.objects.all()
    wishlist_id = request.GET.get('wishlist_id')  # optional

    wishlist_obj = None
    if wishlist_id:
        wishlist_obj = get_object_or_404(WishlistRequest, id=wishlist_id, status='approved')

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'individual':
            name = request.POST['name']
            price = request.POST['price']
            discount_price = request.POST.get('discount_price') or None
            stock = request.POST['stock']
            description = request.POST['description']
            image = request.FILES.get('image')
            category_id = request.POST['category']
            subcategory_id = request.POST.get('subcategory') or None

            category = get_object_or_404(Category, id=category_id)
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
                supervisor_status='waiting',
                admin_status='waiting'
            )
            admin_emails = list(User.objects.filter(is_superuser=True).values_list('email', flat=True))
            supervisor_emails = list(User.objects.filter(profile__role='supervisor').values_list('email', flat=True))

            subject = f"New Product Submitted: {product.name}"
            message = f"A new product '{product.name}' has been submitted by seller '{request.user.username}' for approval."
            send_mail(subject, message, 'myshopee762@gmail.com', admin_emails + supervisor_emails)

            # ✅ If product was added via wishlist request
            if wishlist_obj:
                wishlist_obj.status = 'fulfilled'
                wishlist_obj.save()
                messages.success(request, f"Product from wishlist '{wishlist_obj.product_name}' added and marked as fulfilled.")
            else:
                messages.success(request, "Product submitted for admin approval.")

            return redirect('seller_dashboard')

        elif form_type == 'bulk':
            product_file = request.FILES.get('product_file')
            image_files = request.FILES.getlist('bulk_images')

            if not product_file:
                messages.error(request, "No file uploaded.")
                return redirect('add_product')

            try:
                image_map = {}
                for image in image_files:
                    base_name = os.path.splitext(image.name)[0].replace(' ', '_').lower()
                    image_map[base_name] = image

                df = pd.read_excel(product_file)

                for index, row in df.iterrows():
                    category = Category.objects.get(name=row['Category'])
                    subcategory = None
                    if not pd.isna(row.get('Subcategory')):
                        subcategory = Subcategory.objects.get(name=row['Subcategory'], category=category)

                    product, created = Product.objects.get_or_create(
                        name=row['Product Name'],
                        defaults={
                            'price': row['Price'],
                            'discount_price': row.get('Discount Price', None),
                            'stock': row['Stock'],
                            'description': row['Description'],
                            'category': category,
                            'subcategory': subcategory,
                        }
                    )

                    if created and not pd.isna(row.get('Image Filename')):
                        image_key = str(row['Image Filename']).replace(' ', '_').lower()
                        if image_key in image_map:
                            image_file = image_map[image_key]
                            product.image.save(image_file.name, image_file, save=True)

                    ProductListing.objects.create(
                        product=product,
                        seller=seller,
                        price=row['Price'],
                        stock=row['Stock'],
                        status='waiting'
                    )

                messages.success(request, "Products uploaded successfully.")
                return redirect('seller_dashboard')

            except Exception as e:
                print("Bulk upload error:", e)
                messages.error(request, f"Error uploading products: {e}")
                return redirect('add_product')

    # If GET method and wishlist_id present, optionally pre-fill (your template must support this)
    initial_data = {}
    if wishlist_obj:
        initial_data = {
            'name': wishlist_obj.product_name,
            'description': wishlist_obj.description,
            'category': wishlist_obj.category,
            'subcategory': wishlist_obj.subcategory,
        }

    return render(request, 'add_product.html', {
        'categories': categories,
        'subcategories': subcategories,
        'initial_data': initial_data,
        'wishlist_id': wishlist_id,
    })


@csrf_exempt
@login_required
def add_address_ajax(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone_number = request.POST.get('phone_number')
        address_line_1 = request.POST.get('address_line_1')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')

        address = Address.objects.create(
            user=request.user,
            full_name=full_name,
            phone_number=phone_number,
            address_line_1=address_line_1,
            city=city,
            state=state,
            pincode=pincode
        )

        return JsonResponse({
            'success': True,
            'address_id': address.id,
            'full_name': address.full_name,
            'phone_number': address.phone_number,
            'address_line_1': address.address_line_1,
            'city': address.city,
            'state': address.state,
            'pincode': address.pincode
        })
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def supervisor_approve_listing(request, listing_id):
    if not request.user.profile.role == 'supervisor':
        return HttpResponseForbidden("You are not authorized to approve.")

    listing = get_object_or_404(ProductListing, id=listing_id)
    listing.supervisor_status = 'approved'
    listing.save()
    return redirect('supervisor_dashboard')


@login_required
def admin_approve_listing(request, listing_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Only admin can approve.")

    listing = get_object_or_404(ProductListing, id=listing_id)
    if listing.supervisor_status != 'approved':
        return HttpResponseBadRequest("Supervisor approval pending.")
    listing.admin_status = 'approved'
    listing.save()
    seller_emails = list(User.objects.filter(profile__role='seller').values_list('email', flat=True))
    subject = f"Approved Wishlist Item: {wishlist.product_name}"
    message = f"A wishlist request has been approved for product: {wishlist.product_name}\nDescription: {wishlist.description}"
    send_mail(subject, message, 'myshopee762@gmail.com', seller_emails)
    return redirect('admin_dashboard')



# Buyer Wishlist Submission
@login_required
def my_wishlist(request):
    if request.method == 'POST':
        form = WishlistRequestForm(request.POST)
        if form.is_valid():
            wishlist = form.save(commit=False)
            wishlist.user = request.user
            wishlist.save()
            admin_emails = list(User.objects.filter(is_superuser=True).values_list('email', flat=True))
            subject = f"New Wishlist Request from {request.user.username}"
            message = f"{request.user.username} has submitted a wishlist request for '{wishlist.product_name}'.\n\nDescription: {wishlist.description}"
            send_mail(subject, message, 'myshopee762@gmail.com', admin_emails)
            messages.success(request, "Your wishlist request was submitted!")
            return redirect('my_wishlist')
    else:
        form = WishlistRequestForm()

    requests = WishlistRequest.objects.filter(user=request.user)
    return render(request, 'my_wishlist.html', {'form': form, 'requests': requests})

# Seller View for Approved Wishlist
@login_required
def wishlist_suggestions(request):
    seller = Seller.objects.get(user=request.user)
    approved_requests = WishlistRequest.objects.filter(status='approved')
    return render(request, 'wishlist_suggestions.html', {'requests': approved_requests})

def userinfo(request):
    user = request.user
    name = user.get_full_name() if user.is_authenticated else "Guest"
    return JsonResponse({'name': name})

# 2. POST log message
@csrf_exempt
def log_message(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print("Logged message:", data)  # for testing
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        

@login_required
def my_reviews(request):
    reviews = ProductReview.objects.filter(user=request.user)
    return render(request, 'my_reviews.html', {'reviews': reviews})


@login_required
def add_product_review(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    # Check if the user bought the product
    has_purchased = OrderItem.objects.filter(order__user=request.user, product=product).exists()
    if not has_purchased:
        messages.error(request, "You can only review products you have purchased.")
        return redirect('product_detail', product_id=product_id)

    # Check if user already reviewed
    if ProductReview.objects.filter(user=request.user, product=product).exists():
        messages.warning(request, "You have already reviewed this product.")
        return redirect('product_detail', product_id=product_id)

    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            messages.success(request, "Thanks for reviewing!")
            return redirect('product_detail', product_id=product.id)
    else:
        form = ProductReviewForm()

    return render(request, 'add_review.html', {'form': form, 'product': product})