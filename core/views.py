from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, AddressForm, CustomToyForm
from .models import Address, User, UserContactDetail, Role, UserRole, Staff, ToyType, Toy, Order, OrderItem, Review, Complaint, Payment, ProductionReport
from django import forms
from django.utils import timezone
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from core.decorators import require_role, require_staff_type
from django.contrib import messages
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from django.utils import timezone

def register(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST, request.FILES)
        address_form = AddressForm(request.POST)

        if user_form.is_valid() and address_form.is_valid():
            address = address_form.save()
            user = user_form.save(commit=False)
            user.save()

            UserContactDetail.objects.create(
                user=user,
                phone_number=request.POST.get('phone_number'),
                address=address
            )

            # Assign default customer role to the user
            customer_role, _ = Role.objects.get_or_create(role_name='customer')
            UserRole.objects.create(
                user=user,
                role=customer_role,
                granted_by=None,
                assigned_at=timezone.now()
            )

            print("✅ USER CREATED:", user.username)
            return redirect('login')
        else:
            print("❌ USER FORM ERRORS:", user_form.errors)
            print("❌ ADDRESS FORM ERRORS:", address_form.errors)


    else:
        user_form = CustomUserCreationForm()
        address_form = AddressForm()

    return render(request, 'core/register.html', {
        'user_form': user_form,
        'address_form': address_form
    })

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                print("✅ LOGIN SUCCESSFUL:", username)
                return redirect('home')
            else:
                print("❌ INVALID PASSWORD")
        except User.DoesNotExist:
            print("❌ USER NOT FOUND")

    return render(request, 'core/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).exclude(status='Draft').order_by('-order_date')
    contact_details = UserContactDetail.objects.get(user=request.user)
    return render(request, 'core/profile.html', {'orders': orders, 'user': request.user, 'contact_details': contact_details})


@login_required
def toy_list(request):
    toys_regular = Toy.objects.filter(is_customized=False)
    toys_custom = Toy.objects.filter(is_customized=True, customized_by=request.user)

    return render(request, 'core/toys.html', {
        'toys_regular': toys_regular,
        'toys_custom': toys_custom
    })

@login_required
def create_custom_toy(request):
    if request.method == 'POST':
        form = CustomToyForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data

            Toy.objects.create(
                name=data['name'],
                specification=data['specification'],
                size=data['size'],
                cost_of_production='0.00',  # To be updated later
                type=data['type'],
                is_customized=True,
                customized_by=request.user
            )
            return redirect('toy_list')
    else:
        form = CustomToyForm()

    return render(request, 'core/custom_toy_form.html', {'form': form})


@login_required
def add_to_cart(request, toy_id):
    toy = Toy.objects.get(id=toy_id)
    address = UserContactDetail.objects.get(user=request.user).address

    # Get or create an unplaced order for this user
    order, created = Order.objects.get_or_create(
        user=request.user,
        status='Draft', # Unplaced order
        defaults={'address': address}
    )

    # Check if toy already in cart
    item, item_created = OrderItem.objects.get_or_create(order=order, toy=toy, quantity=1)
    if not item_created:
        item.quantity += 1
        item.save()

        messages.success(request, f"'{toy.name}' was added to your cart.")


    return redirect('cart')

@login_required
def cart(request):
    order = Order.objects.filter(user=request.user, status='Draft').first()
    if order:
        items = order.orderitem_set.select_related('toy')

        for item in items:
            item.subtotal = item.toy.price * item.quantity

        total = sum(item.subtotal for item in items)
    else:
        items = []
        total = 0

    return render(request, 'core/cart.html', {
        'order': order,
        'items': items,
        'total': total
    })

@login_required
def place_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, status="Draft")

    if request.method == 'POST':
        order.status = "Placed"
        order.order_date = timezone.now()
        order.save()
        return redirect('profile')

    return redirect('cart')

@login_required
def update_cart_item(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, order__user=request.user, order__status="Draft")

    if request.method == "POST":
        quantity = int(request.POST.get('quantity', 1))
        item.quantity = max(1, quantity)
        item.save()
        messages.success(request, f"Quantity updated for '{item.toy.name}'.")

    return redirect('cart')

@login_required
def remove_cart_item(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, order__user=request.user, order__status="Draft")

    if request.method == "POST":
        item.delete()
        messages.warning(request, f"'{item.toy.name}' was removed from your cart.")

    return redirect('cart')

@require_role('administrator')
def staff_list(request):
    staff_role = Role.objects.get(role_name='staff')
    admin_role = Role.objects.get(role_name='administrator')

    staff_users = User.objects.filter(userrole__role=staff_role).distinct()
    admin_users = User.objects.filter(userrole__role=admin_role).distinct()


    return render(request, 'core/staff_list.html', {
        'staff_users': staff_users,
        'admin_users': admin_users,
    })


@require_role('administrator')
def grant_admin(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        admin_role = Role.objects.get(role_name='administrator')
        UserRole.objects.get_or_create(
            user=user,
            role=admin_role,
            granted_by=request.user,
            defaults={'assigned_at': now()}
        )
    return redirect('staff_list')

@require_role('administrator')
def revoke_admin(request, user_id):
    if request.method == 'POST':
        admin_role = Role.objects.get(role_name='administrator')
        user_role = UserRole.objects.filter(user_id=user_id, role=admin_role).first()

        if user_role:
            user_role.delete()
            messages.success(request, "Administrator role revoked.")
        else:
            messages.warning(request, "User is not an administrator.")

    return redirect('staff_list')

@require_staff_type('manager')
def manage_orders(request):
    # TODO
    return

@require_staff_type('production_expert')
def submit_production_report(request):
    # TODO
    return

@require_role('administrator')
def validate_reports(request):
    # TODO
    return

