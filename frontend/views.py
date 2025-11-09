"""
Frontend views for QRCS user-facing website.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone

from incidents.models import Incident, IncidentCategory
from responses.models import ResponseTeam, ResponseLog
from notifications.models import Notification
from accounts.models import User


def homepage(request):
    """Homepage showing active incidents."""
    # Get active incidents (not resolved or closed)
    active_incidents = Incident.objects.filter(
        status__in=['reported', 'assigned', 'in_progress']
    ).select_related('category', 'reporter').order_by('-created_at')
    
    # Get all categories
    categories = IncidentCategory.objects.all().order_by('priority_level')
    
    # Pagination
    paginator = Paginator(active_incidents, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'incidents': page_obj,
        'categories': categories,
        'total_active': active_incidents.count(),
    }
    return render(request, 'frontend/homepage.html', context)


def incident_detail(request, incident_id):
    """Detail page for a single incident."""
    incident = get_object_or_404(
        Incident.objects.select_related('category', 'reporter'),
        id=incident_id
    )
    
    # Get response teams
    response_teams = ResponseTeam.objects.filter(
        incident=incident
    ).select_related('responder', 'assigned_by')
    
    # Get response logs
    response_logs = ResponseLog.objects.filter(
        incident=incident
    ).select_related('responder').order_by('-timestamp')
    
    # Check if current user can update status (admins/responders only)
    # - Admins/staff: Can update any incident
    # - Responders: Can only update if assigned to this incident
    # - Reporters: Cannot update
    can_update_status = False
    if request.user.is_authenticated:
        is_admin = request.user.is_staff or request.user.role == 'admin'
        is_responder = request.user.role == 'responder'
        is_assigned = response_teams.filter(responder=request.user).exists()
        can_update_status = is_admin or (is_responder and is_assigned)
    
    context = {
        'incident': incident,
        'response_teams': response_teams,
        'response_logs': response_logs,
        'can_update_status': can_update_status,
    }
    return render(request, 'frontend/incident_detail.html', context)


@login_required
def report_incident(request):
    """Form to report a new incident."""
    if request.method == 'POST':
        try:
            category_id = request.POST.get('category')
            category = get_object_or_404(IncidentCategory, id=category_id)
            
            incident = Incident.objects.create(
                title=request.POST.get('title'),
                description=request.POST.get('description'),
                category=category,
                severity=request.POST.get('severity', 'medium'),
                latitude=float(request.POST.get('latitude', 0)),
                longitude=float(request.POST.get('longitude', 0)),
                location_address=request.POST.get('location_address', ''),
                reporter=request.user,
                image=request.FILES.get('image'),
            )
            
            messages.success(request, f'Incident {incident.incident_id} reported successfully!')
            return redirect('frontend:incident_detail', incident_id=incident.id)
        except Exception as e:
            messages.error(request, f'Error reporting incident: {str(e)}')
    
    categories = IncidentCategory.objects.all().order_by('name')
    context = {
        'categories': categories,
        'severity_choices': Incident.SEVERITY_CHOICES,
    }
    return render(request, 'frontend/report_incident.html', context)


@login_required
def my_incidents(request):
    """Show all incidents reported by current user."""
    incidents = Incident.objects.filter(
        reporter=request.user
    ).select_related('category').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(incidents, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'incidents': page_obj,
        'total_count': incidents.count(),
    }
    return render(request, 'frontend/my_incidents.html', context)


@login_required
def notifications_list(request):
    """Show all notifications for current user."""
    notifications = Notification.objects.filter(
        recipient=request.user
    ).select_related('incident').order_by('-created_at')
    
    # Mark as read when viewed
    unread = notifications.filter(is_read=False)
    unread.update(is_read=True)
    
    # Pagination
    paginator = Paginator(notifications, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'notifications': page_obj,
        'unread_count': unread.count() if request.method == 'GET' else 0,
    }
    return render(request, 'frontend/notifications.html', context)


def register(request):
    """User registration page."""
    if request.user.is_authenticated:
        return redirect('frontend:homepage')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Validation
        if not username or not email or not password1 or not password2:
            messages.error(request, 'All fields are required.')
            return render(request, 'frontend/register.html')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'frontend/register.html')
        
        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'frontend/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'frontend/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'frontend/register.html')
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                role='reporter'  # Default role
            )
            messages.success(request, 'Registration successful! You are now logged in.')
            login(request, user)
            return redirect('frontend:homepage')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
    
    return render(request, 'frontend/register.html')


def user_login(request):
    """User login page."""
    if request.user.is_authenticated:
        return redirect('frontend:homepage')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
            return render(request, 'frontend/login.html')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'frontend/login.html')


def user_logout(request):
    """User logout view."""
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('frontend:homepage')


@login_required
def update_incident_status(request, incident_id):
    """Update incident status page (for admins and responders only)."""
    incident = get_object_or_404(Incident, id=incident_id)
    
    # Check if user is admin/staff (can update any incident)
    is_admin = request.user.is_staff or request.user.role == 'admin'
    
    # Check if user is a responder AND assigned to this incident
    is_responder = request.user.role == 'responder'
    is_assigned = ResponseTeam.objects.filter(
        incident=incident,
        responder=request.user
    ).exists()
    
    # Permission logic:
    # - Admins/staff: Can update any incident
    # - Responders: Can only update incidents they're assigned to
    # - Reporters: Cannot update (explicitly denied)
    has_permission = is_admin or (is_responder and is_assigned)
    
    if not has_permission:
        messages.error(
            request, 
            'Access denied. Only administrators and assigned responders can update incident status.'
        )
        return redirect('frontend:incident_detail', incident_id=incident.id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        new_severity = request.POST.get('severity')
        
        if new_status in dict(Incident.STATUS_CHOICES):
            old_status = incident.status
            incident.status = new_status
            
            if new_severity in dict(Incident.SEVERITY_CHOICES):
                incident.severity = new_severity
            
            if new_status == 'resolved' and not incident.resolved_at:
                incident.resolved_at = timezone.now()
            
            incident.save()
            messages.success(request, f'Incident updated successfully! Status: {old_status} → {new_status}')
            
            # Create notification
            from notifications.utils import create_notification
            create_notification(
                recipient=incident.reporter,
                incident=incident,
                notification_type='status_update',
                title='Incident Status Updated',
                message=f'Your incident {incident.incident_id} status changed to {new_status}'
            )
            
            return redirect('frontend:incident_detail', incident_id=incident.id)
    
    context = {
        'incident': incident,
        'status_choices': Incident.STATUS_CHOICES,
        'severity_choices': Incident.SEVERITY_CHOICES,
    }
    return render(request, 'frontend/update_status.html', context)


def team_list(request):
    """List all response teams."""
    # Get all response teams with details
    response_teams = ResponseTeam.objects.select_related(
        'responder', 'incident', 'assigned_by'
    ).order_by('-assigned_at')
    
    # Group by responder
    teams_by_responder = {}
    for team in response_teams:
        responder_id = team.responder.id
        if responder_id not in teams_by_responder:
            teams_by_responder[responder_id] = {
                'responder': team.responder,
                'teams': [],
                'total_assignments': 0,
            }
        teams_by_responder[responder_id]['teams'].append(team)
        teams_by_responder[responder_id]['total_assignments'] += 1
    
    # Convert to list for pagination
    teams_list = list(teams_by_responder.values())
    
    # Pagination
    paginator = Paginator(teams_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'teams': page_obj,
        'total_teams': len(teams_by_responder),
    }
    return render(request, 'frontend/team_list.html', context)


def team_detail(request, team_id):
    """Detail page for a response team assignment."""
    team = get_object_or_404(
        ResponseTeam.objects.select_related('responder', 'incident', 'assigned_by'),
        id=team_id
    )
    
    # Get all teams for this responder
    responder_teams = ResponseTeam.objects.filter(
        responder=team.responder
    ).select_related('incident', 'assigned_by').order_by('-assigned_at')
    
    # Get response logs for this team's incident
    response_logs = ResponseLog.objects.filter(
        incident=team.incident,
        responder=team.responder
    ).order_by('-timestamp')
    
    context = {
        'team': team,
        'responder_teams': responder_teams,
        'response_logs': response_logs,
        'can_edit': request.user.is_staff or request.user.role == 'admin',
    }
    return render(request, 'frontend/team_detail.html', context)
