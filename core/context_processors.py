def role_flags(request):
    if request.user.is_authenticated:
        roles = request.user.roles.values_list('role__role_name', flat=True)

        return {
            'is_staff': 'staff' in roles,
            'is_admin': 'administrator' in roles,
            'is_manager': getattr(request.user, 'staff', None) and request.user.staff.staff_type == 'manager'
        }
    return {}
