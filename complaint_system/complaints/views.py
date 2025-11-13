from urllib.parse import urlparse

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from functools import wraps

from .forms import ComplaintAdminForm, ComplaintForm, UserRegistrationForm
from .models import DEPARTMENT_CHOICES, Complaint, User
from .jwt_auth import generate_jwt_tokens, set_jwt_cookies, clear_jwt_cookies, jwt_authority_required, get_user_from_token

STATUS_DISPLAY = {
    "pending": {"label": "Pending Review", "badge": "badge-status-pending"},
    "in_progress": {"label": "In Progress", "badge": "badge-status-progress"},
    "resolved": {"label": "Resolved", "badge": "badge-status-resolved"},
}

PRIORITY_DISPLAY = {
    "low": {"label": "Low", "badge": "badge-priority-low"},
    "medium": {"label": "Medium", "badge": "badge-priority-medium"},
    "high": {"label": "High", "badge": "badge-priority-high"},
    "urgent": {"label": "Urgent", "badge": "badge-priority-urgent"},
}


def user_login_required(view_func):
    """
    Decorator to ensure users are authenticated through regular user login (not Django admin).
    Even superusers must log in through the regular login form to access citizen pages.
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to access this page.")
            return redirect('login')
        
        # Check if user logged in through regular user login (not Django admin)
        # We track this with a session variable set during regular login
        if not request.session.get('user_logged_in', False):
            # User is authenticated but didn't log in through regular login
            # This means they're logged in via Django admin or another method
            messages.error(
                request, 
                "You must log in through the citizen portal to access this page. "
                "Django admin login does not grant access to citizen pages."
            )
            return redirect('login')
        
        return view_func(request, *args, **kwargs)
    
    return wrapped_view


@csrf_protect
@require_http_methods(["GET", "POST"])
def authority_login(request):
    """
    JWT-based authority login. Only logs in users with correct department assignment.
    Failed logins do NOT authenticate the user.
    """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        next_url = request.POST.get("next") or request.GET.get("next", "")

        # Authenticate user credentials
        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, "Invalid credentials. Please try again.")
            # DO NOT log in - stay on login page
        else:
            # Only staff members can access authority dashboards
            if not user.is_staff:
                messages.error(
                    request, "You do not have permission to access the authority dashboard."
                )
                # DO NOT log in - just show error and stay on login page
                next_param = request.POST.get("next") or request.GET.get("next", "")
                return render(request, "complaints/authority_login.html", {
                    "next": next_param,
                    "department_label": None,
                    "is_authenticated": False,
                    "current_user": None,
                })
            
            # Determine requested department from `next_url` (if present)
            requested_dept = None
            if next_url:
                parsed = urlparse(next_url)
                path = parsed.path or parsed.geturl()
                if path.startswith("/authority/"):
                    parts = [p for p in path.split("/") if p]
                    if len(parts) >= 2:
                        key = parts[1]
                        if key == "dashboard":
                            requested_dept = "admin"
                        else:
                            requested_dept = key

            # All users (including superusers) must have correct department assignment
            # If a specific department/dashboard was requested, ensure user belongs to it
            if requested_dept:
                if requested_dept == "admin":
                    if user.department == "admin":
                        # Generate JWT tokens with department info
                        tokens = generate_jwt_tokens(user, user.department)
                        response = redirect(next_url if next_url else "authority_dashboard")
                        set_jwt_cookies(response, tokens)
                        return response
                    else:
                        messages.error(
                            request, "This account is not authorised for the authority dashboard. You must be assigned to the 'admin' department."
                        )
                        # DO NOT log in - just show error and stay on login page
                        return render(request, "complaints/authority_login.html", {
                            "next": next_url,
                            "department_label": dict(DEPARTMENT_CHOICES).get("admin", "Central Administration"),
                            "is_authenticated": False,
                            "current_user": None,
                        })
                else:
                    if user.department == requested_dept:
                        # Generate JWT tokens with department info
                        tokens = generate_jwt_tokens(user, user.department)
                        response = redirect("department_dashboard", department_slug=requested_dept)
                        set_jwt_cookies(response, tokens)
                        return response
                    else:
                        dept_name = dict(DEPARTMENT_CHOICES).get(requested_dept, requested_dept)
                        messages.error(
                            request, f"This account is not authorised for the {dept_name} dashboard. Your department assignment does not match."
                        )
                        # DO NOT log in - just show error and stay on login page
                        return render(request, "complaints/authority_login.html", {
                            "next": next_url,
                            "department_label": dept_name,
                            "is_authenticated": False,
                            "current_user": None,
                        })
            else:
                # No specific dashboard requested — check if user has a department and redirect accordingly
                if user.department:
                    if user.department == "admin":
                        tokens = generate_jwt_tokens(user, user.department)
                        response = redirect("authority_dashboard")
                        set_jwt_cookies(response, tokens)
                        return response
                    elif user.department in dict(DEPARTMENT_CHOICES):
                        tokens = generate_jwt_tokens(user, user.department)
                        response = redirect("department_dashboard", department_slug=user.department)
                        set_jwt_cookies(response, tokens)
                        return response
                # If no department assigned, don't log in - show error
                messages.error(
                    request, "Your account is not assigned to any department. Please contact the administrator."
                )
                return render(request, "complaints/authority_login.html", {
                    "next": next_url,
                    "department_label": None,
                    "is_authenticated": False,
                    "current_user": None,
                })

    # Determine a friendly department label from the `next` parameter so the login
    # page can show which dashboard the user will be returned to after sign-in.
    next_param = request.POST.get("next") or request.GET.get("next", "")
    department_label = None
    department_slug = None
    if next_param:
        parsed = urlparse(next_param)
        path = parsed.path or parsed.geturl()
        # Expecting paths like: /authority/ (landing), /authority/dashboard/, /authority/<slug>/
        if path.startswith("/authority/"):
            parts = [p for p in path.split("/") if p]
            # parts[0] == 'authority'
            if len(parts) >= 2:
                key = parts[1]
                if key == "dashboard":
                    department_label = dict(DEPARTMENT_CHOICES).get(
                        "admin", "Central Administration"
                    )
                    department_slug = "admin"
                else:
                    department_label = dict(DEPARTMENT_CHOICES).get(key)
                    department_slug = key

    # Check if user has valid JWT token (authority authentication)
    jwt_user, jwt_dept, jwt_error = get_user_from_token(request)
    has_jwt_auth = jwt_user is not None
    
    context = {
        "next": next_param,
        "department_label": department_label,
        "department_slug": department_slug,
        "jwt_authenticated": has_jwt_auth,  # Only true if authenticated via JWT
        "jwt_user": jwt_user if has_jwt_auth else None,  # Only show JWT-authenticated user
        "is_authenticated": False,  # Explicitly set to False to avoid Django session confusion
        "current_user": jwt_user if has_jwt_auth else None,  # Only show JWT-authenticated user
    }
    return render(request, "complaints/authority_login.html", context)


def authority_landing(request):
    """Landing page for authority users to choose their department before logging in."""
    # Use the defined DEPARTMENT_CHOICES from models to build links
    department_choices = list(DEPARTMENT_CHOICES)
    context = {
        "department_choices": department_choices,
    }
    return render(request, "complaints/authority_landing.html", context)


def _redirect_after_login(request, user, fallback=None):
    if fallback:
        return redirect(fallback)
    # Only redirect to authority dashboards if user is staff and has department assignment
    # No superuser bypass - all users must have correct department
    if user.is_staff and user.department:
        if (
            user.department in dict(DEPARTMENT_CHOICES)
            and user.department != "admin"
        ):
            return redirect("department_dashboard", department_slug=user.department)
        elif user.department == "admin":
            return redirect("authority_dashboard")
    # Non-staff users or users without department should be redirected to the regular home page
    return redirect("home")


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Set session flag to indicate user logged in through regular login
            request.session['user_logged_in'] = True
            request.session.set_expiry(0)  # Session expires when browser closes
            messages.success(request, "Registration successful!")
            return redirect("home")
    else:
        form = UserRegistrationForm()
    return render(
        request, "complaints/register.html", {"form": form, "hide_navbar": True}
    )


def user_login(request):
    # If user is already logged in through regular login, redirect to home
    if request.user.is_authenticated and request.session.get('user_logged_in', False):
        return redirect('home')
    
    if request.method == "POST":
        contact = request.POST.get("contact")
        password = request.POST.get("password")

        if not contact or not password:
            messages.error(request, "Please provide both contact number and password")
        else:
            # Find user by contact number
            try:
                user = User.objects.get(contact=contact)
                # Authenticate using the username and password
                user = authenticate(request, username=user.username, password=password)
                if user is not None:
                    login(request, user)
                    # Set session flag to indicate user logged in through regular login
                    request.session['user_logged_in'] = True
                    request.session.set_expiry(0)  # Session expires when browser closes
                    messages.success(request, "Login successful!")
                    return redirect("home")
                else:
                    messages.error(request, "Invalid contact number or password")
            except User.DoesNotExist:
                messages.error(request, "Invalid contact number or password")
    return render(request, "complaints/login.html", {"hide_navbar": True})


def forgot_password(request):
    if request.method == "POST":
        contact = request.POST.get("contact")

        if not contact:
            messages.error(request, "Please provide your contact number")
        else:
            # Check if user exists with this contact number
            try:
                user = User.objects.get(contact=contact)
                # In a real application, you would:
                # 1. Generate a password reset token
                # 2. Send the reset link via SMS/Email
                # For now, we'll just show a success message
                messages.success(
                    request,
                    f"Password reset instructions have been sent to {contact}. Please check your messages.",
                )
                return redirect("login")
            except User.DoesNotExist:
                messages.error(request, "No account found with this contact number")

    return render(request, "complaints/forgot_password.html", {"hide_navbar": True})


def user_logout(request):
    # Clear the user login session flag
    if 'user_logged_in' in request.session:
        del request.session['user_logged_in']
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("login")


def authority_logout(request):
    """Logout from authority dashboard and clear JWT tokens."""
    response = redirect("authority_landing")
    clear_jwt_cookies(response)
    messages.success(request, "Logged out successfully!")
    return response


@user_login_required
def home(request):
    return render(request, "complaints/home.html")


@user_login_required
def submit_complaint(request):
    if request.method == "POST":
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            if not complaint.location:
                complaint.location = getattr(request.user, "address", "")
            complaint.save()
            messages.success(request, "Complaint submitted successfully!")
            return redirect("my_complaints")
    else:
        form = ComplaintForm()
    return render(request, "complaints/submit_complaint.html", {"form": form})


@user_login_required
def my_complaints(request):
    complaints = Complaint.objects.filter(user=request.user)
    return render(request, "complaints/my_complaints.html", {"complaints": complaints})


def _ensure_staff(request):
    if not request.user.is_staff:
        messages.error(
            request, "You do not have permission to access the authority dashboard."
        )
        return False
    return True


def _apply_filters(
    queryset, request, include_department=False, default_department=None
):
    filters = {
        "q": request.GET.get("q", "").strip(),
        "status": request.GET.get("status", "all"),
        "priority": request.GET.get("priority", "all"),
    }
    if include_department:
        filters["department"] = request.GET.get(
            "department", default_department or "all"
        )

    if filters["q"]:
        search_term = filters["q"]
        queryset = queryset.filter(
            Q(title__icontains=search_term)
            | Q(description__icontains=search_term)
            | Q(location__icontains=search_term)
            | Q(user__name__icontains=search_term)
            | Q(user__username__icontains=search_term)
        )

    if filters["status"] != "all":
        queryset = queryset.filter(status=filters["status"])

    if filters["priority"] != "all":
        queryset = queryset.filter(priority=filters["priority"])

    if include_department:
        dept_filter = filters["department"]
        if dept_filter == "unassigned":
            queryset = queryset.filter(
                Q(assigned_department__isnull=True) | Q(assigned_department="")
            )
        elif dept_filter not in ("", "all", None):
            queryset = queryset.filter(assigned_department=dept_filter)

    return queryset, filters


def _build_stats(total, pending, forwarded, resolved, icon_set=None):
    icon_set = icon_set or {
        "total": {"icon": "📄", "tone": "tone-admin"},
        "pending": {"icon": "⚠️", "tone": "tone-status-pending"},
        "forwarded": {"icon": "📤", "tone": "tone-status-progress"},
        "resolved": {"icon": "✅", "tone": "tone-status-resolved"},
    }

    return [
        {
            "title": "Total Complaints",
            "value": total,
            "icon": icon_set["total"]["icon"],
            "tone": icon_set["total"]["tone"],
            "description": "System-wide submissions",
        },
        {
            "title": "Pending Review",
            "value": pending,
            "icon": icon_set["pending"]["icon"],
            "tone": icon_set["pending"]["tone"],
            "description": "Awaiting initial action",
        },
        {
            "title": "Forwarded",
            "value": forwarded,
            "icon": icon_set["forwarded"]["icon"],
            "tone": icon_set["forwarded"]["tone"],
            "description": "Sent to departments",
        },
        {
            "title": "Resolved",
            "value": resolved,
            "icon": icon_set["resolved"]["icon"],
            "tone": icon_set["resolved"]["tone"],
            "description": "Closed cases",
        },
    ]


def _format_complaints(complaints, include_department):
    department_lookup = dict(DEPARTMENT_CHOICES)
    rows = []
    for complaint in complaints:
        priority_key = (
            complaint.priority if complaint.priority in PRIORITY_DISPLAY else "medium"
        )
        status_key = (
            complaint.status if complaint.status in STATUS_DISPLAY else "in_progress"
        )
        assigned = complaint.assigned_department
        rows.append(
            {
                "id": complaint.id,
                "reference": f"CMP-{complaint.id:05d}",
                "title": complaint.title,
                "department": department_lookup.get(assigned, "Unassigned")
                if include_department
                else department_lookup.get(assigned, "Unassigned"),
                "department_slug": assigned,
                "location": complaint.location
                or getattr(complaint.user, "address", "Not provided"),
                "priority": PRIORITY_DISPLAY[priority_key],
                "status": STATUS_DISPLAY[status_key],
                "created_at": complaint.created_at,
                "detail_url": reverse(
                    "authority_complaint_detail", args=[complaint.id]
                ),
            }
        )
    return rows


@jwt_authority_required(required_department="admin")
def authority_dashboard(request):
    # JWT authentication and department verification handled by decorator
    # Use request.jwt_user instead of request.user
    user = request.jwt_user

    all_complaints = Complaint.objects.select_related("user").order_by("-created_at")
    filtered, filters = _apply_filters(all_complaints, request, include_department=True)

    total = all_complaints.count()
    pending = all_complaints.filter(status="pending").count()
    forwarded = all_complaints.exclude(
        Q(assigned_department__isnull=True)
        | Q(assigned_department="")
        | Q(assigned_department="admin")
    ).count()
    resolved = all_complaints.filter(status="resolved").count()

    stats = _build_stats(total, pending, forwarded, resolved)

    # Evaluate queryset to list to ensure it's properly processed
    filtered_list = list(filtered)
    complaints_rows = _format_complaints(filtered_list, include_department=True)

    context = {
        "stats": stats,
        "complaints": complaints_rows,
        "filters": filters,
        "status_choices": [("all", "All Status")]
        + [(key, value["label"]) for key, value in STATUS_DISPLAY.items()],
        "priority_choices": [("all", "All Priority")]
        + [(key, info["label"]) for key, info in PRIORITY_DISPLAY.items()],
        "department_choices": [("all", "All Departments"), ("unassigned", "Unassigned")]
        + list(DEPARTMENT_CHOICES),
        "show_department": True,
        "dashboard_tone": "tone-admin",
        "dashboard_icon": "🛡️",
        "dashboard_title": "Local Admin Authority",
        "dashboard_subtitle": "City-wide complaint routing",
        "jwt_user": user,  # Pass JWT user to template
    }
    return render(request, "complaints/authority_dashboard.html", context)


@jwt_authority_required(required_department=None)  # Will check department in view
def department_dashboard(request, department_slug):
    # JWT authentication handled by decorator
    user = request.jwt_user
    department = request.jwt_department
    
    department_lookup = dict(DEPARTMENT_CHOICES)
    if department_slug not in department_lookup:
        messages.error(request, "Unknown department selected.")
        return redirect("authority_landing")

    # Verify department matches (decorator ensures user is staff, but we need exact match)
    if department != department_slug:
        dept_name = department_lookup.get(department_slug, department_slug)
        messages.error(request, f"You are not authorised for the {dept_name} department. Your department assignment does not match.")
        return redirect("authority_landing")

    base_queryset = Complaint.objects.select_related("user").order_by("-created_at")
    # User's department must match (already verified above), so filter accordingly
    base_queryset = base_queryset.filter(
        Q(assigned_department=department_slug)
        | Q(assigned_department__isnull=True)
        | Q(assigned_department="")
    )

    filtered, filters = _apply_filters(base_queryset, request)

    total = base_queryset.count()
    pending = base_queryset.filter(status="pending").count()
    in_progress = base_queryset.filter(status="in_progress").count()
    resolved = base_queryset.filter(status="resolved").count()

    icon_palette = {
        "total": {"icon": "📘", "tone": f"tone-{department_slug}"},
        "pending": {"icon": "⚠️", "tone": "tone-status-pending"},
        "forwarded": {"icon": "🚚", "tone": "tone-status-progress"},
        "resolved": {"icon": "✅", "tone": "tone-status-resolved"},
    }
    stats = _build_stats(total, pending, in_progress, resolved, icon_set=icon_palette)
    stats[2]["title"] = "In Progress"
    stats[2]["description"] = "Currently being handled"

    complaints_rows = _format_complaints(filtered, include_department=False)

    context = {
        "stats": stats,
        "complaints": complaints_rows,
        "filters": filters,
        "status_choices": [("all", "All Status")]
        + [(key, value["label"]) for key, value in STATUS_DISPLAY.items()],
        "priority_choices": [("all", "All Priority")]
        + [(key, info["label"]) for key, info in PRIORITY_DISPLAY.items()],
        "show_department": False,
        "dashboard_tone": f"tone-{department_slug}",
        "dashboard_icon": "🏢",
        "dashboard_title": f"{department_lookup[department_slug]}",
        "dashboard_subtitle": "Operational workload overview",
        "department_slug": department_slug,
        "jwt_user": user,  # Pass JWT user to template
    }
    return render(request, "complaints/authority_dashboard.html", context)


@jwt_authority_required(required_department=None)  # Will check department in view
def authority_complaint_detail(request, pk):
    # JWT authentication handled by decorator
    user = request.jwt_user
    department = request.jwt_department
    
    # Admin users can access all complaints; other departments can only access their assigned complaints
    complaint = get_object_or_404(Complaint.objects.select_related("user"), pk=pk)

    # Admin department has access to all complaints
    if department == "admin":
        # Admin can view/manage any complaint
        pass
    else:
        # Non-admin departments can only access complaints assigned to them
        allowed_departments = set()
        if complaint.assigned_department:
            allowed_departments.add(complaint.assigned_department)
        else:
            # Unassigned complaints may be picked up by a user from their own department
            if department:
                allowed_departments.add(department)

        if department not in allowed_departments:
            messages.error(request, "You are not authorised to manage this complaint. Your department assignment does not match the complaint's assigned department.")
            return redirect("authority_landing")

    redirect_target = (
        request.POST.get("next")
        or request.GET.get("next")
        or request.META.get("HTTP_REFERER")
        or reverse("authority_dashboard")
    )

    if request.method == "POST":
        form = ComplaintAdminForm(request.POST, instance=complaint)
        if form.is_valid():
            updated_complaint = form.save()
            messages.success(
                request, f"Complaint {updated_complaint.id} updated successfully."
            )
            return redirect(redirect_target)
        else:
            messages.error(
                request,
                "Unable to update complaint. Please correct the highlighted fields.",
            )
    else:
        form = ComplaintAdminForm(instance=complaint)

    department_lookup = dict(DEPARTMENT_CHOICES)
    context = {
        "complaint": complaint,
        "form": form,
        "department_lookup": department_lookup,
        "status_display": STATUS_DISPLAY.get(
            complaint.status,
            {"label": complaint.get_status_display(), "badge": "badge-status-progress"},
        ),
        "priority_display": PRIORITY_DISPLAY.get(
            complaint.priority, PRIORITY_DISPLAY["medium"]
        ),
        "dashboard_tone": f"tone-{complaint.assigned_department or 'admin'}",
        "dashboard_icon": "📝",
        "dashboard_title": "Complaint Detail",
        "dashboard_subtitle": f"Reference CMP-{complaint.id:05d}",
        "return_url": redirect_target,
        "jwt_user": user,  # Pass JWT user to template
    }
    return render(request, "complaints/authority_complaint_detail.html", context)
