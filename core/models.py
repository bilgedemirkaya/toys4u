from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Avg

# -------------------------------
# Custom User with address ref
# -------------------------------

class User(AbstractUser):
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def has_role(self, role_name):
        return self.userrole_set.filter(role__role_name=role_name).exists()

class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

class UserContactDetail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)

# -------------------------------
# Roles & Permissions
# -------------------------------

class Role(models.Model):
    class RoleType(models.TextChoices):
        CUSTOMER = 'customer', 'Customer'
        ADMINISTRATOR = 'administrator', 'Administrator'
        STAFF = 'staff', 'Staff'

    role_name = models.CharField(
        max_length=20,
        choices=RoleType.choices,
        default=RoleType.CUSTOMER,)

    def __str__(self):
        return self.get_role_name_display()

class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='granted_roles')
    assigned_at = models.DateTimeField(auto_now_add=True)

class Staff(models.Model):
    class StaffType(models.TextChoices):
        MANAGER = 'manager', 'Manager'
        PRODUCTION_EXPERT = 'production_expert', 'Production Expert'
        REGULAR_STAFF = 'regular_staff', 'Regular Staff'

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    staff_type = models.CharField(
        max_length=20,
        choices=StaffType.choices,
        default=StaffType.REGULAR_STAFF
    )

    def __str__(self):
        return f"{self.user.username} – {self.get_staff_type_display()}"

# -------------------------------
# Toy & ToyType
# -------------------------------

class ToyType(models.Model):
    type_name = models.CharField(max_length=50)

    def __str__(self):
        return self.type_name

class Toy(models.Model):
    name = models.CharField(max_length=100)
    picture = models.ImageField(upload_to='toys/')
    type = models.ForeignKey(ToyType, on_delete=models.SET_NULL, null=True)
    size = models.CharField(max_length=50)
    cost_of_production = models.DecimalField(max_digits=8, decimal_places=2)
    rating = models.FloatField(default=0.0)
    purchase_count = models.IntegerField(default=0)
    is_customized = models.BooleanField(default=False)
    specification = models.TextField(blank=True, null=True, help_text="Custom specifications for the toy")
    customized_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='toys_created')
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)

    def average_rating(self):
        return self.toy_reviews.aggregate(avg=Avg('rating'))['avg'] or 0

    def is_bad(self):
        review_count = self.toy_reviews.count()

        if review_count == 0:
            return False

        return self.average_rating() < 2.5
# -------------------------------
# Orders
# -------------------------------

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    order_date = models.DateField(auto_now_add=True)
    is_customized = models.BooleanField(default=False)
    specification = models.TextField(blank=True, null=True, help_text="Custom specifications for the order")
    status = models.CharField(max_length=20, default='Draft')
    cost = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

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
# ToyReview
# -------------------------------
class ToyReview(models.Model):
    toy = models.ForeignKey(Toy, on_delete=models.CASCADE, related_name='toy_reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.toy.name} by {self.user.username}"

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
    toy = models.ForeignKey(Toy, on_delete=models.CASCADE, null=True)
    expert = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reports_written')
    report_text = models.TextField()
    status = models.CharField(max_length=20, default='Draft')
    validated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reports_validated')
    validation_date = models.DateField(blank=True, null=True)

    def is_validated(self):
        return self.validated_by is not None

    def __str__(self):
        return f"Report for Toy {self.toy.name} – Order #{self.order.id}"
