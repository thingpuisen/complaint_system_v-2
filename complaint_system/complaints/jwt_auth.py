"""
JWT Authentication utilities for authority/admin access control.
Ensures strict department-based access with JWT tokens.
"""
from functools import wraps
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import redirect
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from .models import DEPARTMENT_CHOICES


def generate_jwt_tokens(user, department):
    """
    Generate JWT tokens for a user with department information.
    Only call this after verifying user has correct department access.
    """
    refresh = RefreshToken()
    refresh['user_id'] = user.id
    refresh['username'] = user.username
    refresh['department'] = department
    refresh['is_staff'] = user.is_staff
    
    access = refresh.access_token
    access['user_id'] = user.id
    access['username'] = user.username
    access['department'] = department
    access['is_staff'] = user.is_staff
    
    return {
        'refresh': str(refresh),
        'access': str(access),
    }


def get_user_from_token(request):
    """
    Extract and validate user from JWT token in request.
    Returns (user, department, error_message) tuple.
    """
    # Try to get token from cookie first (more secure)
    access_token = request.COOKIES.get('authority_access_token')
    
    # Fallback to Authorization header
    if not access_token:
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            access_token = auth_header.split(' ')[1]
    
    if not access_token:
        return None, None, "No authentication token provided"
    
    try:
        token = AccessToken(access_token)
        user_id = token.get('user_id')
        department = token.get('department')
        is_staff = token.get('is_staff', False)
        
        from .models import User
        try:
            user = User.objects.get(id=user_id, is_active=True)
            # Verify token claims match current user state
            if user.is_staff != is_staff or user.department != department:
                return None, None, "Token claims do not match user state"
            return user, department, None
        except User.DoesNotExist:
            return None, None, "User not found"
    except (TokenError, InvalidToken) as e:
        return None, None, f"Invalid token: {str(e)}"


def jwt_authority_required(required_department=None):
    """
    Decorator to require JWT authentication and department access.
    
    Args:
        required_department: Specific department required, or None for any department
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            # Get user from JWT token
            user, department, error = get_user_from_token(request)
            
            if user is None or error:
                messages.error(request, "Authentication required. Please log in.")
                return redirect('authority_login')
            
            # Verify user is staff
            if not user.is_staff:
                messages.error(request, "You do not have permission to access this area.")
                return redirect('authority_landing')
            
            # Verify department access
            if required_department:
                if required_department == "admin":
                    if department != "admin":
                        messages.error(
                            request, 
                            "You are not authorised for the central authority dashboard. "
                            "You must be assigned to the 'admin' department."
                        )
                        return redirect('authority_landing')
                else:
                    if department != required_department:
                        dept_name = dict(DEPARTMENT_CHOICES).get(required_department, required_department)
                        messages.error(
                            request,
                            f"You are not authorised for the {dept_name} department. "
                            "Your department assignment does not match."
                        )
                        return redirect('authority_landing')
            elif not department:
                messages.error(
                    request,
                    "Your account is not assigned to any department. "
                    "Please contact the administrator."
                )
                return redirect('authority_landing')
            
            # Attach user and department to request for use in view
            request.jwt_user = user
            request.jwt_department = department
            
            return view_func(request, *args, **kwargs)
        
        return wrapped_view
    return decorator


def set_jwt_cookies(response, tokens):
    """Set JWT tokens as httpOnly cookies for security."""
    response.set_cookie(
        'authority_access_token',
        tokens['access'],
        max_age=8 * 60 * 60,  # 8 hours
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite='Lax'
    )
    response.set_cookie(
        'authority_refresh_token',
        tokens['refresh'],
        max_age=24 * 60 * 60,  # 1 day
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite='Lax'
    )
    return response


def clear_jwt_cookies(response):
    """Clear JWT cookies on logout."""
    response.delete_cookie('authority_access_token')
    response.delete_cookie('authority_refresh_token')
    return response

