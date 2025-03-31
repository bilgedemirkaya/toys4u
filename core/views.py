from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, AddressForm, CustomToyForm
from .models import Address, User, Role, UserRole, StaffType, Staff, ToyType, Toy, Order, OrderItem, Review, Complaint, Payment, ProductionReport
from django import forms
from django.utils import timezone

from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST, request.FILES)
        address_form = AddressForm(request.POST)

        if user_form.is_valid() and address_form.is_valid():
            address = address_form.save()
            user = user_form.save(commit=False)
            user.address = address
            user.save()

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
def profile(request):
    return render(request, 'core/profile.html', {
        'user': request.user
    })

@login_required
def toy_list(request):
    toys_regular = Toy.objects.filter(is_customised=False)
    return render(request, 'core/toys.html', {
        'toys_regular': toys_regular
    })

@login_required
def create_custom_toy(request):
    if request.method == 'POST':
        form = CustomToyForm(request.POST)
        if form.is_valid():
            spec = form.cleaned_data['specification']

            # Create the custom Toy (not public, only for this user’s order)
            toy = Toy.objects.create(
                name="Custom Toy",
                type=ToyType.objects.first(),  # fallback for now
                size="Custom",
                cost_of_production=50.00,
                rating=5.0,
                is_customised=True
            )

            # Get or create the draft order (cart)
            order, created = Order.objects.get_or_create(
                user=request.user,
                status="Draft",  # This means it's still in the cart stage
                defaults={'address': request.user.address}
            )

            # Add toy to the order as an item
            OrderItem.objects.create(
                order=order,
                toy=toy,
                quantity=1
            )

            return redirect('toy_list')  # or redirect to "View Cart"
    else:
        form = CustomToyForm()

    return render(request, 'core/custom_toy_form.html', {'form': form})