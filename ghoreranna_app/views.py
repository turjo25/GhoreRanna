from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Sum
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
import uuid
from .models import User, Menu, Order, OrderDetails, Coupon, Payment, Delivery
from .forms import RegistrationForm, LoginForm, MenuForm, ProfileUpdateForm, CookManagementForm, CheckoutForm, CouponForm

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            if user.role == 'Admin':
                messages.error(request, "Registration as Admin is not allowed.")
                return redirect('register')
            user.password = make_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = RegistrationForm()
    
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            
            try:
                user = User.objects.get(email=email)
                if check_password(password, user.password):
                    if user.status == 'Active':
                        request.session['user_id'] = user.user_id
                        request.session['user_role'] = user.role
                        request.session['user_name'] = user.name
                        messages.success(request, f"Welcome back, {user.name}!")
                        if user.role == 'Delivery Staff':
                            return redirect('delivery_dashboard')
                        return redirect('home')
                    else:
                        messages.error(request, "Your account is inactive. Please contact support.")
                else:
                    messages.error(request, "Invalid email or password.")
            except User.DoesNotExist:
                messages.error(request, "Invalid email or password.")
    else:
        form = LoginForm()
        
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    request.session.flush() # Clear the session data
    messages.success(request, "You have been logged out.")
    return redirect('login')

def home_view(request):
    return render(request, 'home.html')

def menu_list(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    cook_filter = request.GET.get('cook_filter', '')
    
    base_menus = Menu.objects.all()
    if request.session.get('user_role') == 'Home Cook' and cook_filter == 'mine':
        base_menus = base_menus.filter(homecook_id=request.session.get('user_id'))

    menus = base_menus
    if query:
        menus = menus.filter(item_name__icontains=query) | menus.filter(description__icontains=query)
    if category:
        menus = menus.filter(meal_type__iexact=category)
    raw_categories = base_menus.values_list('meal_type', flat=True).distinct()
    categories = sorted(list(set(cat.strip().title() for cat in raw_categories if cat)))
    
    context = {
        'menus': menus,
        'query': query,
        'selected_category': category,
        'categories': categories,
        'cook_filter': cook_filter,
    }
    return render(request, 'menu_list.html', context)

def menu_detail(request, pk):
    menu = get_object_or_404(Menu, pk=pk)
    
    total_ordered = menu.order_details.filter(
        order__order_status='Delivered'
    ).aggregate(total=Sum('quantity'))['total'] or 0
    context = {
        'menu': menu,
        'total_ordered': total_ordered,
    }
    return render(request, 'menu_detail.html', context)

def cart_add(request, pk):
    if not request.session.get('user_id'):
        messages.info(request, "Please log in to add items to your cart.")
        return redirect('login')
    
    menu = get_object_or_404(Menu, pk=pk)
    cart = request.session.get('cart', {})
    str_pk = str(pk)
    if str_pk in cart:
        cart[str_pk] += 1
    else:
        cart[str_pk] = 1
        
    request.session['cart'] = cart
    request.session.modified = True
    
    messages.success(request, f'"{menu.item_name}" added to your cart!')
    redirect_to = request.GET.get('next', 'cart')
    if redirect_to == 'menu_detail':
        return redirect('menu_detail', pk=pk)
    elif redirect_to == 'menu_list':
        return redirect('menu_list')
    
    return redirect('cart')

def cart_view(request):
    if not request.session.get('user_id'):
        messages.info(request, "Please log in to view your cart.")
        return redirect('login')
        
    cart = request.session.get('cart', {})
    cart_items = []
    total_amount = 0
    
    for menu_id, quantity in cart.items():
        try:
            menu = Menu.objects.get(pk=int(menu_id))
            subtotal = menu.price * quantity
            total_amount += subtotal
            cart_items.append({
                'menu': menu,
                'quantity': quantity,
                'subtotal': subtotal
            })
        except Menu.DoesNotExist:
            continue
            
    order_history = Order.objects.filter(user_id=request.session['user_id']).order_by('-order_date')
    
    context = {
        'cart_items': cart_items,
        'total_amount': total_amount,
        'cart_count': sum(cart.values()),
        'order_history': order_history
    }
    return render(request, 'cart.html', context)

def cart_remove(request, pk):
    cart = request.session.get('cart', {})
    str_pk = str(pk)
    if str_pk in cart:
        del cart[str_pk]
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, "Item removed from cart.")
    return redirect('cart')

def cart_update(request, pk):
    action = request.GET.get('action')
    cart = request.session.get('cart', {})
    str_pk = str(pk)
    
    if str_pk in cart:
        if action == 'increment':
            cart[str_pk] += 1
        elif action == 'decrement':
            if cart[str_pk] > 1:
                cart[str_pk] -= 1
            else:
                del cart[str_pk]
        request.session['cart'] = cart
        request.session.modified = True
        
    return redirect('cart')

def menu_add(request):
    user_role = request.session.get('user_role')
    if user_role not in ['Admin', 'Home Cook']:
        messages.error(request, "Only Admins and Home Cooks can add menus.")
        return redirect('menu_list')
        
    try:
        user = User.objects.get(pk=request.session['user_id'])
    except User.DoesNotExist:
        messages.error(request, "Invalid user context.")
        return redirect('menu_list')

    if request.method == 'POST':
        form = MenuForm(request.POST, request.FILES, user=user)
        if form.is_valid():
            menu = form.save(commit=False)
            if user_role == 'Admin':
                menu.homecook = form.cleaned_data['homecook']
            else:
                menu.homecook = user
            menu.save()
            messages.success(request, 'Menu item added successfully!')
            return redirect('menu_list')
    else:
        form = MenuForm(user=user)
    
    return render(request, 'menu_form.html', {'form': form, 'action': 'Add'})

def menu_update(request, pk):
    # Restrict to Admin or Home Cook
    user_role = request.session.get('user_role')
    if user_role not in ['Admin', 'Home Cook']:
        messages.error(request, "Only Admins and Home Cooks can update menus.")
        return redirect('menu_list')
        
    menu = get_object_or_404(Menu, pk=pk)
    
    if user_role == 'Home Cook' and menu.homecook_id != request.session.get('user_id'):
        messages.error(request, "You can only edit your own menu items.")
        return redirect('menu_list')

    try:
        user = User.objects.get(pk=request.session['user_id'])
    except User.DoesNotExist:
        messages.error(request, "Invalid user context.")
        return redirect('menu_list')

    if request.method == 'POST':
        form = MenuForm(request.POST, request.FILES, instance=menu, user=user)
        if form.is_valid():
            if user_role == 'Admin' and 'homecook' in form.cleaned_data:
                menu.homecook = form.cleaned_data['homecook']
            form.save()
            messages.success(request, 'Menu item updated successfully!')
            return redirect('menu_list')
    else:
        form = MenuForm(instance=menu, user=user)
        if user_role == 'Admin':
            form.fields['homecook'].initial = menu.homecook
        
    return render(request, 'menu_form.html', {'form': form, 'action': 'Update', 'menu': menu})

def menu_delete(request, pk):
    # Restrict to Admin or Home Cook
    user_role = request.session.get('user_role')
    if user_role not in ['Admin', 'Home Cook']:
        messages.error(request, "Only Admins and Home Cooks can delete menus.")
        return redirect('menu_list')
        
    menu = get_object_or_404(Menu, pk=pk)

    if user_role == 'Home Cook' and menu.homecook_id != request.session.get('user_id'):
        messages.error(request, "You can only delete your own menu items.")
        return redirect('menu_list')

    if request.method == 'POST':
        menu.delete()
        messages.success(request, 'Menu item deleted successfully!')
        return redirect('menu_list')
        
    return render(request, 'menu_confirm_delete.html', {'menu': menu})

def profile_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please set login to access your profile.")
        return redirect('login')

    if request.session.get('user_role') == 'Delivery Staff':
        return redirect('delivery_dashboard')

    user = get_object_or_404(User, pk=user_id)
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            request.session['user_name'] = form.cleaned_data.get('name')
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=user)

    context = {'form': form, 'user': user}

    # Role-based stats calculation
    if user.role == 'Admin':
        # Master Stats
        context['total_cooks'] = User.objects.filter(role='Home Cook').count()
        context['total_students'] = User.objects.filter(role__in=['Student', 'Bachelor Employee']).count()
        context['food_available'] = Menu.objects.filter(availability_status=True).count()
        context['total_completed_orders'] = Order.objects.filter(order_status='Delivered').count()
        context['total_revenue'] = Order.objects.filter(order_status='Delivered').aggregate(total=Sum('total_amount'))['total'] or 0
        
        # System Management Context
        context['all_system_orders'] = Order.objects.all().prefetch_related(
            'order_details__menu__homecook', 'user', 'delivery'
        ).select_related('coupon', 'payment').order_by('-order_date')
        
        context['all_cooks'] = User.objects.filter(role='Home Cook').order_by('-status', 'name')
        context['all_coupons'] = Coupon.objects.all().order_by('-status', '-expiry_date')
    elif user.role == 'Home Cook':
        context['food_available'] = Menu.objects.filter(homecook=user, availability_status=True).count()
        context['food_sold'] = OrderDetails.objects.filter(menu__homecook=user, order__order_status='Delivered').aggregate(total=Sum('quantity'))['total'] or 0
        context['total_revenue'] = OrderDetails.objects.filter(menu__homecook=user, order__order_status='Delivered').aggregate(total=Sum('subtotal'))['total'] or 0
        
        # Cook order context
        cook_all_orders = Order.objects.filter(
            order_details__menu__homecook=user
        ).distinct().prefetch_related('order_details__menu', 'delivery', 'user').select_related('payment').order_by('-order_date')
        
        context['cook_active_orders'] = cook_all_orders.exclude(order_status='Delivered')
        context['cook_order_history'] = cook_all_orders.filter(order_status='Delivered')
        context['delivery_staff_list'] = User.objects.filter(role='Delivery Staff', status='Active')
    else:
        # Customer stats
        all_orders = (
            Order.objects
            .filter(user=user)
            .prefetch_related('order_details__menu', 'delivery')
            .select_related('coupon', 'payment')
            .order_by('-order_date')
        )
        context['ordered_food_count']    = all_orders.count()
        context['successful_order_count'] = all_orders.filter(order_status='Delivered').count()
        context['cancelled_order_count']  = all_orders.filter(order_status='Cancelled').count()
        context['total_spent'] = (
            all_orders.filter(order_status='Delivered')
            .aggregate(total=Sum('total_amount'))['total'] or 0
        )
        context['order_history'] = all_orders
        # Latest order that is still active (not delivered / cancelled)
        context['active_order'] = all_orders.exclude(
            order_status__in=['Delivered', 'Cancelled']
        ).first()
        # Available coupons
        context['available_coupons'] = Coupon.objects.filter(
            status=True, expiry_date__gt=timezone.now()
        ).order_by('expiry_date')
    
    return render(request, 'profile.html', context)

# Admin Cook Management Views
def cook_list(request):
    if request.session.get('user_role') != 'Admin':
        messages.error(request, "Access denied.")
        return redirect('home')
    
    cooks = User.objects.filter(role='Home Cook')
    return render(request, 'cook_list.html', {'cooks': cooks})

def cook_create(request):
    if request.session.get('user_role') != 'Admin':
        messages.error(request, "Access denied.")
        return redirect('home')
        
    if request.method == 'POST':
        form = CookManagementForm(request.POST)
        if form.is_valid():
            cook = form.save(commit=False)
            cook.role = 'Home Cook'
            if form.cleaned_data.get('password'):
                cook.password = make_password(form.cleaned_data['password'])
            else:
                # Default password if not provided
                cook.password = make_password('cook123')
            cook.save()
            messages.success(request, f"Cook '{cook.name}' created successfully.")
            return redirect('cook_list')
    else:
        form = CookManagementForm()
    
    return render(request, 'cook_form.html', {'form': form, 'action': 'Add'})

def cook_update(request, pk):
    if request.session.get('user_role') != 'Admin':
        messages.error(request, "Access denied.")
        return redirect('home')
        
    cook = get_object_or_404(User, pk=pk, role='Home Cook')
    if request.method == 'POST':
        form = CookManagementForm(request.POST, instance=cook)
        if form.is_valid():
            updated_cook = form.save(commit=False)
            if form.cleaned_data.get('password'):
                updated_cook.password = make_password(form.cleaned_data['password'])
            updated_cook.save()
            messages.success(request, f"Cook '{updated_cook.name}' updated successfully.")
            return redirect('cook_list')
    else:
        form = CookManagementForm(instance=cook)
        
    return render(request, 'cook_form.html', {'form': form, 'action': 'Update', 'cook': cook})

def cook_delete(request, pk):
    if request.session.get('user_role') != 'Admin':
        messages.error(request, "Access denied.")
        return redirect('home')
        
    cook = get_object_or_404(User, pk=pk, role='Home Cook')
    if request.method == 'POST':
        name = cook.name
        cook.delete()
        messages.success(request, f"Cook '{name}' deleted successfully.")
        return redirect('cook_list')
        
    return render(request, 'cook_confirm_delete.html', {'cook': cook})


# ─────────────────────────────────────────────
# Checkout & Payment
# ─────────────────────────────────────────────

def checkout_view(request):
    """Convert session cart into a real Order with demo payment processing."""
    if not request.session.get('user_id'):
        messages.info(request, "Please log in to proceed to checkout.")
        return redirect('login')

    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, "Your cart is empty. Add some items first!")
        return redirect('menu_list')

    # Build cart items preview
    cart_items = []
    subtotal = 0
    for menu_id, quantity in cart.items():
        try:
            menu = Menu.objects.get(pk=int(menu_id))
            item_subtotal = menu.price * quantity
            subtotal += item_subtotal
            cart_items.append({'menu': menu, 'quantity': quantity, 'subtotal': item_subtotal})
        except Menu.DoesNotExist:
            continue

    user = get_object_or_404(User, pk=request.session['user_id'])

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            coupon = None
            discount_amount = 0
            coupon_code = form.cleaned_data.get('coupon_code', '').strip().upper()

            # ── Coupon Validation ──
            if coupon_code:
                try:
                    coupon = Coupon.objects.get(code=coupon_code, status=True)
                    if coupon.expiry_date < timezone.now():
                        messages.error(request, f"Coupon '{coupon_code}' has expired.")
                        coupon = None
                    else:
                        discount_amount = (subtotal * coupon.discount_percentage / 100).quantize(
                            Decimal('0.01'), rounding=ROUND_HALF_UP
                        )
                except Coupon.DoesNotExist:
                    messages.error(request, f"Coupon '{coupon_code}' is not valid.")
                    return render(request, 'checkout.html', {
                        'form': form, 'cart_items': cart_items,
                        'subtotal': subtotal, 'user': user,
                    })

            total_amount = subtotal - discount_amount
            payment_method = form.cleaned_data['payment_method']

            # ── Create Order ──
            order = Order.objects.create(
                user=user,
                coupon=coupon,
                total_amount=total_amount,
                payment_method=payment_method,
                order_status='Pending',
                delivery_time=timezone.now() + timezone.timedelta(minutes=45),
            )

            # ── Create OrderDetails ──
            for item in cart_items:
                OrderDetails.objects.create(
                    order=order,
                    menu=item['menu'],
                    quantity=item['quantity'],
                    subtotal=item['subtotal'],
                )

            # ── Demo Payment Processing ──
            # Simulate: Cash → always completes; Card/Online → always completes (demo)
            demo_transaction_id = f"GR-{uuid.uuid4().hex[:10].upper()}"
            Payment.objects.create(
                order=order,
                payment_method=payment_method,
                payment_status='Completed',
                transaction_id=demo_transaction_id,
            )

            # ── Create Delivery record ──
            Delivery.objects.create(
                order=order,
                delivery_status='Pending',
            )

            # ── Clear Cart ──
            request.session['cart'] = {}
            request.session.modified = True

            # ── Store confirmation data in session briefly ──
            request.session['last_order_id'] = order.order_id

            return redirect('order_confirmation')

    else:
        # Pre-fill delivery address from user profile
        form = CheckoutForm(initial={'delivery_address': user.address})

    context = {
        'form': form,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'user': user,
    }
    return render(request, 'checkout.html', context)


def order_confirmation_view(request):
    """Show order success page. Reads the last order ID from session."""
    if not request.session.get('user_id'):
        return redirect('login')

    order_id = request.session.pop('last_order_id', None)
    if not order_id:
        messages.info(request, "No recent order found.")
        return redirect('cart')

    order = get_object_or_404(
        Order.objects.select_related('payment', 'coupon'),
        pk=order_id,
        user_id=request.session['user_id'],
    )
    order_details = order.order_details.select_related('menu')

    context = {
        'order': order,
        'order_details': order_details,
        'payment': getattr(order, 'payment', None),
    }
    return render(request, 'order_confirmation.html', context)

def update_order_status(request, pk):
    """Allow Home Cooks to update the order status, delivery time, and dispatch a rider."""
    if request.method == 'POST':
        user_role = request.session.get('user_role')
        if user_role != 'Home Cook':
            messages.error(request, "Permission denied.")
            return redirect('home')

        order = get_object_or_404(Order, pk=pk)
        
        # In a real app we'd verify this cook owns items in this order
        
        new_status = request.POST.get('order_status')
        new_delivery_time = request.POST.get('delivery_time')
        delivery_staff_id = request.POST.get('delivery_staff')
        
        if new_status:
            order.order_status = new_status
            if new_status == 'Cancelled':
                order.cancellation_status = True
        
        if new_delivery_time:
            order.delivery_time = new_delivery_time
            
        order.save()
        
        # Update delivery assignment
        if delivery_staff_id:
            try:
                staff = User.objects.get(pk=delivery_staff_id, role='Delivery Staff')
                delivery, created = Delivery.objects.get_or_create(
                    order=order,
                    defaults={'delivery_status': 'Assigned'}
                )
                delivery.delivery_staff = staff
                # Update status
                if new_status == 'Preparing':
                    delivery.delivery_status = 'Assigned'
                elif new_status == 'Out for Delivery':
                    delivery.delivery_status = 'Picked Up'
                elif new_status == 'Delivered':
                    delivery.delivery_status = 'Delivered'
                    delivery.delivery_date = timezone.now()
                delivery.save()
            except User.DoesNotExist:
                pass
                
        messages.success(request, f"Order #{order.order_id} updated successfully.")
        
        # Determine which tab to return to
        target_tab = 'cook-history' if new_status == 'Delivered' else 'incoming-orders'
        return redirect(reverse('profile') + f'?tab={target_tab}')
        
    return redirect(reverse('profile') + '?tab=incoming-orders')

def mark_order_delivered(request, pk):
    """Allow Customers to acknowledge delivery of their order."""
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, "Please log in.")
            return redirect('login')

        order = get_object_or_404(Order, pk=pk, user_id=user_id)
        
        if order.order_status == 'Handed Over':
            order.order_status = 'Delivered'
            order.save()
            
            # Update delivery tracking if exists
            if hasattr(order, 'delivery'):
                order.delivery.delivery_status = 'Delivered'
                order.delivery.delivery_date = timezone.now()
                order.delivery.save()
                
            messages.success(request, f"Order #{order.order_id} marked as delivered. Enjoy your food!")
        else:
            messages.error(request, "Order cannot be marked as delivered yet.")
            
    return redirect(reverse('profile') + '?tab=history')

def cancel_order(request, pk):
    """Allow Customers to cancel their order if it hasn't started being prepared."""
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, "Please log in.")
            return redirect('login')

        order = get_object_or_404(Order, pk=pk, user_id=user_id)
        
        if order.order_status in ['Pending', 'Accepted']:
            order.order_status = 'Cancelled'
            order.save()
            
            messages.success(request, f"Order #{order.order_id} has been cancelled.")
        else:
            messages.error(request, "Order cannot be cancelled at this stage.")
            
    return redirect(reverse('profile') + '?tab=history')

def validate_coupon(request):
    """AJAX view to validate a coupon code and return discount details."""
    code = request.GET.get('code', '').strip().upper()
    cart = request.session.get('cart', {})
    
    if not cart:
        return JsonResponse({'success': False, 'message': 'Cart is empty.'})
        
    # Calculate current subtotal
    subtotal = 0
    for menu_id, quantity in cart.items():
        try:
            menu = Menu.objects.get(pk=int(menu_id))
            subtotal += menu.price * quantity
        except Menu.DoesNotExist:
            continue
            
    try:
        coupon = Coupon.objects.get(code=code, status=True)
        if coupon.expiry_date < timezone.now():
            return JsonResponse({'success': False, 'message': 'Coupon has expired.'})
            
        discount_amount = (subtotal * coupon.discount_percentage / 100).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        new_total = subtotal - discount_amount
        
        return JsonResponse({
            'success': True,
            'discount': f"{discount_amount:.2f}",
            'new_total': f"{new_total:.2f}",
            'message': f"Success! {coupon.discount_percentage}% discount applied."
        })
    except Coupon.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Invalid coupon code.'})

# ═══ Admin Coupon Management ═══
def coupon_add(request):
    if request.session.get('user_role') != 'Admin':
        messages.error(request, "Access denied.")
        return redirect('home')
        
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Coupon created successfully!")
            return redirect(reverse('profile') + '?tab=coupons')
    else:
        form = CouponForm()
    
    return render(request, 'coupon_form.html', {'form': form, 'action': 'Add'})

def coupon_edit(request, pk):
    if request.session.get('user_role') != 'Admin':
        messages.error(request, "Access denied.")
        return redirect('home')
        
    coupon = get_object_or_404(Coupon, pk=pk)
    if request.method == 'POST':
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request, "Coupon updated successfully!")
            return redirect(reverse('profile') + '?tab=coupons')
    else:
        form = CouponForm(instance=coupon)
    
    return render(request, 'coupon_form.html', {'form': form, 'action': 'Update', 'coupon': coupon})

def coupon_delete(request, pk):
    if request.session.get('user_role') != 'Admin':
        messages.error(request, "Access denied.")
        return redirect('home')
        
    coupon = get_object_or_404(Coupon, pk=pk)
    if request.method == 'POST':
        code = coupon.code
        coupon.delete()
        messages.success(request, f"Coupon '{code}' deleted.")
        return redirect(reverse('profile') + '?tab=coupons')
    
    return render(request, 'coupon_confirm_delete.html', {'coupon': coupon})


def delivery_dashboard_view(request):
    user_id = request.session.get('user_id')
    if not user_id or request.session.get('user_role') != 'Delivery Staff':
        messages.error(request, "Access denied. Please log in as Delivery Staff.")
        return redirect('login')

    staff = get_object_or_404(User, pk=user_id, role='Delivery Staff')

    # Handle profile self-edit from the portal
    if request.method == 'POST' and request.POST.get('edit_profile'):
        name    = request.POST.get('name', '').strip()
        phone   = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        if name:
            staff.name    = name
            staff.phone   = phone
            staff.address = address
            staff.save()
            request.session['user_name'] = name
            messages.success(request, "Profile updated successfully!")
        else:
            messages.error(request, "Name cannot be empty.")
        return redirect(reverse('delivery_dashboard') + '?tab=profile')

    # Fetch only deliveries assigned to THIS staff member
    my_deliveries = (
        Delivery.objects
        .filter(delivery_staff=staff)
        .select_related('order__user', 'order__payment')
        .prefetch_related('order__order_details__menu')
        .order_by('-order__order_date')
    )

    # Split into active (not yet delivered) and history
    active_deliveries = my_deliveries.exclude(delivery_status='Delivered')
    past_deliveries   = my_deliveries.filter(delivery_status='Delivered')

    context = {
        'staff': staff,
        'active_deliveries': active_deliveries,
        'past_deliveries':   past_deliveries,
        'total_assigned':    my_deliveries.count(),
        'total_delivered':   past_deliveries.count(),
        'total_active':      active_deliveries.count(),
    }
    return render(request, 'delivery_dashboard.html', context)


def delivery_update_status(request, pk):
    """Allow a delivery staff member to update the status of their OWN delivery."""
    if request.method != 'POST':
        return redirect('delivery_dashboard')

    user_id = request.session.get('user_id')
    if not user_id or request.session.get('user_role') != 'Delivery Staff':
        messages.error(request, "Access denied.")
        return redirect('login')

    # Only let THIS staff update THEIR OWN delivery — ownership guard
    delivery = get_object_or_404(Delivery, pk=pk, delivery_staff_id=user_id)
    new_status = request.POST.get('delivery_status')

    allowed_transitions = {
        'Assigned': 'Picked Up',
        'Picked Up': 'Handed Over',
    }

    if new_status not in allowed_transitions.values():
        messages.error(request, "Invalid status transition.")
        return redirect('delivery_dashboard')

    # Validate forward-only transition
    expected = allowed_transitions.get(delivery.delivery_status)
    if new_status != expected:
        messages.error(request, f"Cannot change status from '{delivery.delivery_status}' to '{new_status}'.")
        return redirect('delivery_dashboard')

    delivery.delivery_status = new_status
    if new_status == 'Handed Over':
        # Mirror on the parent Order
        delivery.order.order_status = 'Handed Over'
        delivery.order.save()

    delivery.save()
    messages.success(request, f"Order #{delivery.order.order_id} marked as '{new_status}'.")
    return redirect('delivery_dashboard')
    return render(request, 'delivery_staff_profile.html', context)