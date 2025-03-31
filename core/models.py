from django.db import models
from django.contrib.auth.models import AbstractUser

# -------------------------------
# Custom User with address ref
# -------------------------------

class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

class User(AbstractUser):
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)

class UserContactDetail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)

# -------------------------------
# Roles & Permissions
# -------------------------------

class Role(models.Model):
    role_name = models.CharField(max_length=50)

    def __str__(self):
        return self.role_name

class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='granted_roles')
    assigned_at = models.DateTimeField(auto_now_add=True)

# -------------------------------
# Staff Types
# -------------------------------

class StaffType(models.Model):
    type_name = models.CharField(max_length=50)

class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    staff_type = models.ForeignKey(StaffType, on_delete=models.SET_NULL, null=True)

# -------------------------------
# Toy & ToyType
# -------------------------------

class ToyType(models.Model):
    type_name = models.CharField(max_length=50)

class Toy(models.Model):
    name = models.CharField(max_length=100)
    picture = models.ImageField(upload_to='toys/')
    type = models.ForeignKey(ToyType, on_delete=models.SET_NULL, null=True)
    size = models.CharField(max_length=50)
    cost_of_production = models.DecimalField(max_digits=8, decimal_places=2)
    rating = models.FloatField(default=0.0)
    purchase_count = models.IntegerField(default=0)
    is_customised = models.BooleanField(default=False)

# -------------------------------
# Orders
# -------------------------------

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    order_date = models.DateField(auto_now_add=True)
    is_customised = models.BooleanField(default=False)
    specification = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, default='Draft')

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    toy = models.ForeignKey(Toy, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

# -------------------------------
# Review
# -------------------------------

class Review(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comments = models.TextField(blank=True)

# -------------------------------
# Complaint
# -------------------------------

class Complaint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    complaint_text = models.TextField()
    complaint_date = models.DateField(auto_now_add=True)

# -------------------------------
# Payment
# -------------------------------

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=50)

# -------------------------------
# Production Report
# -------------------------------

class ProductionReport(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    expert = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reports_written')
    report_text = models.TextField()
    validated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reports_validated')
    validation_date = models.DateField(blank=True, null=True)
