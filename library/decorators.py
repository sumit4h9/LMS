from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied


def is_admin(user):
    """Check if user is admin or superuser"""
    return user.is_superuser or user.groups.filter(name='Admin').exists()


def is_member(user):
    """Check if user is member"""
    return user.groups.filter(name='Member').exists()


def admin_required(function=None):
    """Decorator to check if user is admin"""
    actual_decorator = user_passes_test(
        is_admin,
        login_url='accounts:login',
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def member_required(function=None):
    """Decorator to check if user is member"""
    actual_decorator = user_passes_test(
        is_member,
        login_url='accounts:login',
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
