from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(Address)
admin.site.register(UserContactDetail)
admin.site.register(Role)
admin.site.register(UserRole)
admin.site.register(Staff)
admin.site.register(ToyType)
admin.site.register(Toy)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Review)
admin.site.register(Complaint)
admin.site.register(Payment)
admin.site.register(ProductionReport)
