from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, AddressForm, CustomToyForm, ProductionReportForm, ToyEditForm, ReviewForm, ToyReviewForm
from .models import User, UserContactDetail, Role, UserRole, Staff, Toy, Order, OrderItem, ProductionReport, ToyReview
from django.utils import timezone
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from core.decorators import require_role, require_staff_type
from django.contrib import messages
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Sum

def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('toy_list')
    else:
        return redirect('register')

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
    orders = Order.objects.filter(user=request.user).exclude(status='Draft').order_by('-order_date') # Order by most recent
    contact_details = UserContactDetail.objects.get(user=request.user)

    try:
        staff = Staff.objects.get(user=request.user)
    except Staff.DoesNotExist:
        staff = None

    return render(request, 'core/profile.html', {
        'orders': orders,
        'user': request.user,
        'contact_details': contact_details,
        'staff': staff
    })


@login_required
def toy_list(request):
    toys_regular = Toy.objects.filter(is_customized=False).order_by('-created_at')
    toys_custom = Toy.objects.filter(is_customized=True).order_by('-created_at')
    visible_toys = [toy for toy in toys_regular if not toy.is_bad()]

    try:
        staff = Staff.objects.get(user=request.user)
    except Staff.DoesNotExist:
        staff = None

    for toy in toys_regular:
        toy.user_review = ToyReview.objects.filter(user=request.user, toy=toy).first()

    for toy in toys_custom:
        toy.user_review = ToyReview.objects.filter(user=request.user, toy=toy).first()

    return render(request, 'core/toys.html', {
        'toys_regular': visible_toys,
        'toys_custom': toys_custom,
        'staff': staff,
        "star_range": range(5, 0, -1),
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
                cost_of_production='0.00',  # Staff can update later
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
    status='Draft',
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
        items = order.orderitem_set.select_related('toy') # Joins Toy table to get toy details

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
        order.cost = sum(item.toy.price * item.quantity for item in order.orderitem_set.all())
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

    staff_users = User.objects.filter(roles__role=staff_role).distinct()
    admin_users = User.objects.filter(roles__role=admin_role).distinct()
    admin_roles = UserRole.objects.filter(role=admin_role).select_related('user', 'granted_by') # Join UserRole to get user and granted_by details

    return render(request, 'core/staff_list.html', {
        'staff_users': staff_users,
        'admin_users': admin_users,
        'admin_roles': admin_roles
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

@require_staff_type('production_expert')
def production_report(request, toy_id):
    if request.method == 'POST':
        form = ProductionReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.expert = request.user
            report.save()
            messages.success(request, "Production report submitted successfully.")
            return redirect('profile')
    else:
        toy = get_object_or_404(Toy, id=toy_id)
        form = ProductionReportForm(initial={'toy': toy})

    return render(request, 'core/production_report.html', {'form': form, toy: toy})

@require_role('staff')
def production_reports_list(request):
    all_reports = ProductionReport.objects.select_related('toy', 'expert', 'validated_by')

    is_manager = request.user.staff.staff_type == 'manager'

    if request.method == 'POST' and is_manager:
        report_id = request.POST.get('report_id')
        report = ProductionReport.objects.get(id=report_id)
        report.status = 'Approved'
        report.validated_by = request.user
        report.validation_date = timezone.now()
        report.save()

    return render(request, 'core/reports.html', {
        'reports': all_reports,
        'is_manager': is_manager
    })

@login_required
def edit_toy(request, toy_id):
    toy = get_object_or_404(Toy, id=toy_id)

    if request.method == 'POST':
        form = ToyEditForm(request.POST, request.FILES, instance=toy)
        if form.is_valid():
            form.save()
            return redirect('toy_list')
    else:
        form = ToyEditForm(instance=toy)

    return render(request, 'core/edit_toy.html', {'form': form, 'toy': toy})

@login_required
def leave_review(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, status='Placed')

    if hasattr(order, 'review'):
        messages.warning(request, "You already submitted a review for this order.")
        return redirect('profile')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.order = order
            review.save()
            messages.success(request, "Thank you for your review!")
            return redirect('profile')
    else:
        form = ReviewForm()

    return render(request, 'core/leave_review.html', {'form': form, 'order': order})

@require_role('administrator')
def sales_report(request):
    today = now().date()

    # Daily
    daily_sales = Order.objects.filter(status='Placed', order_date=today)\
        .aggregate(total=Sum('orderitem__toy__price'))

    # Monthly
    first_of_month = today.replace(day=1)
    monthly_sales = Order.objects.filter(status='Placed', order_date__gte=first_of_month)\
        .aggregate(total=Sum('orderitem__toy__price'))

    # Yearly
    first_of_year = today.replace(month=1, day=1)
    yearly_sales = Order.objects.filter(status='Placed', order_date__gte=first_of_year)\
        .aggregate(total=Sum('orderitem__toy__price'))

    return render(request, 'core/sales_report.html', {
        'daily_sales': daily_sales['total'] or 0,
        'monthly_sales': monthly_sales['total'] or 0,
        'yearly_sales': yearly_sales['total'] or 0,
    })

@login_required
def review_toy(request, toy_id):
    toy = get_object_or_404(Toy, id=toy_id)

    if request.method == 'POST':
        form = ToyReviewForm(request.POST)
        if form.is_valid():
            ToyReview.objects.create(
                toy=toy,
                user=request.user,
                rating=form.cleaned_data['rating']
            )
            # Update toy's rating
            toy.rating = toy.average_rating()
            toy.save()
            messages.success(request, "Thank you for your review!")

            return redirect('toy_list')
    return redirect('toy_list')