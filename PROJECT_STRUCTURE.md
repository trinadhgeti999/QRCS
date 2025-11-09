# Project Structure

This document outlines the complete structure of the QRCS (Quick Response Coordination System) Django project.

## Directory Structure

```
QR/
├── qrcs_project/              # Main project directory
│   ├── __init__.py           # Celery app initialization
│   ├── settings.py            # Development settings
│   ├── settings_prod.py       # Production settings
│   ├── urls.py                # Main URL configuration
│   ├── wsgi.py                # WSGI configuration
│   ├── asgi.py                # ASGI configuration (WebSockets)
│   ├── routing.py             # WebSocket routing
│   └── celery.py              # Celery configuration
│
├── accounts/                  # User management app
│   ├── models.py             # Custom User model
│   ├── serializers.py        # User serializers
│   ├── views.py              # User views
│   ├── urls.py               # Account URLs
│   ├── admin.py              # Admin configuration
│   └── tests.py              # Unit tests
│
├── incidents/                 # Incident management app
│   ├── models.py             # Incident and Category models
│   ├── serializers.py        # Incident serializers
│   ├── views.py              # Incident views
│   ├── urls.py               # Incident URLs
│   ├── admin.py              # Admin configuration
│   └── tests.py              # Unit tests
│
├── responses/                 # Response team management app
│   ├── models.py             # ResponseTeam and ResponseLog models
│   ├── serializers.py       # Response serializers
│   ├── views.py              # Response views
│   ├── urls.py               # Response URLs
│   ├── admin.py              # Admin configuration
│   └── tests.py              # Unit tests
│
├── notifications/             # Notification system app
│   ├── models.py             # Notification model
│   ├── serializers.py        # Notification serializers
│   ├── views.py              # Notification views
│   ├── urls.py               # Notification URLs
│   ├── consumers.py          # WebSocket consumers
│   ├── utils.py              # Notification utilities
│   ├── admin.py              # Admin configuration
│   └── tests.py              # Unit tests
│
├── dashboard/                 # Dashboard and analytics app
│   ├── views.py              # Dashboard views
│   ├── urls.py               # Dashboard URLs
│   └── tests.py              # Unit tests
│
├── manage.py                  # Django management script
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose configuration
├── .gitignore                 # Git ignore rules
├── README.md                  # Project documentation
└── Main                       # Original documentation file
```

## Key Features

### 1. User Management (accounts)
- Custom User model with role-based access (Admin, Responder, Reporter)
- JWT authentication
- User registration and profile management
- Availability toggle for responders

### 2. Incident Management (incidents)
- Incident reporting with location tracking
- Incident categories with priority levels
- Status tracking (reported, assigned, in_progress, resolved, closed)
- Severity levels (low, medium, high, critical)
- Nearby incidents search
- Statistics and trends

### 3. Response Management (responses)
- Response team assignment
- Team lead designation
- Response logging with location and images
- Activity tracking

### 4. Notifications (notifications)
- Real-time WebSocket notifications
- Email notifications (configurable)
- Notification types: incident_created, incident_assigned, status_update, message
- Read/unread status tracking

### 5. Dashboard (dashboard)
- Comprehensive statistics
- Incident trends
- Response metrics
- Role-based data filtering

## API Endpoints

### Authentication
- `POST /api/auth/login/` - Get JWT tokens
- `POST /api/auth/refresh/` - Refresh JWT token

### Accounts
- `GET /api/accounts/users/` - List users
- `POST /api/accounts/users/` - Register new user
- `GET /api/accounts/users/me/` - Get current user
- `PUT /api/accounts/users/me/` - Update current user

### Incidents
- `GET /api/incidents/` - List incidents
- `POST /api/incidents/` - Create incident
- `GET /api/incidents/{id}/` - Get incident details
- `PUT /api/incidents/{id}/` - Update incident
- `POST /api/incidents/{id}/update_status/` - Update status
- `GET /api/incidents/nearby/` - Get nearby incidents
- `GET /api/incidents/statistics/` - Get statistics

### Response Teams
- `GET /api/response-teams/` - List response teams
- `POST /api/response-teams/` - Assign responder
- `POST /api/response-teams/{id}/set_lead/` - Set team lead

### Response Logs
- `GET /api/response-logs/` - List response logs
- `POST /api/response-logs/` - Create response log

### Notifications
- `GET /api/notifications/` - List notifications
- `POST /api/notifications/{id}/mark_read/` - Mark as read
- `POST /api/notifications/mark_all_read/` - Mark all as read
- `GET /api/notifications/unread_count/` - Get unread count

### Dashboard
- `GET /api/dashboard/stats/` - Get dashboard statistics
- `GET /api/dashboard/trends/` - Get incident trends

## Database Models

### User (accounts.User)
- Extends AbstractUser
- Fields: role, phone, address, avatar, is_available

### IncidentCategory
- Fields: name, description, priority_level, icon

### Incident
- Fields: incident_id, title, description, category, reporter, status, severity, latitude, longitude, location_address, image

### ResponseTeam
- Fields: incident, responder, assigned_at, assigned_by, notes, is_lead

### ResponseLog
- Fields: incident, responder, action, details, latitude, longitude, image, timestamp

### Notification
- Fields: recipient, incident, notification_type, title, message, is_read, created_at

## WebSocket

WebSocket endpoint: `ws://localhost:8000/ws/notifications/`

Connects authenticated users to receive real-time notifications.

## Security Features

- JWT authentication
- Role-based access control
- CORS configuration
- CSRF protection
- Secure password hashing
- Production security settings

## Testing

Run tests with:
```bash
python manage.py test
```

Each app includes test files for models and views.


