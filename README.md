# Quick Response Coordination System (QRCS)

A comprehensive Django-based emergency response coordination system that enables quick reporting, tracking, and management of incidents with real-time coordination between responders and administrators.

## Features

- **User Authentication**: Role-based access control (Admin, Responder, Reporter)
- **Incident Management**: Report, track, and manage incidents with location tracking
- **Real-time Updates**: WebSocket-based notifications for real-time status updates
- **Response Team Assignment**: Assign and manage response teams for incidents
- **Dashboard Analytics**: Comprehensive analytics and statistics
- **Notification System**: Real-time and email notifications
- **RESTful API**: Complete REST API with JWT authentication
- **Map Integration**: Location-based incident visualization

## Tech Stack

- Django 5.0+
- Django REST Framework
- PostgreSQL (with PostGIS support)
- Celery (async tasks)
- Redis (caching & task queue)
- Django Channels (WebSockets)
- JWT Authentication

## Project Structure

```
qrcs_project/
├── accounts/          # User management
├── incidents/         # Incident reporting and tracking
├── responses/         # Response team management
├── notifications/     # Notification system
├── dashboard/         # Analytics and statistics
└── qrcs_project/     # Project settings
```

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis
- Virtual environment (recommended)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd QR
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the project root:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   DB_NAME=qrcs_db
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_HOST=localhost
   DB_PORT=5432
   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND=redis://localhost:6379/0
   ```

5. **Set up database**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

8. **Run Celery worker** (in separate terminal)
   ```bash
   celery -A qrcs_project worker -l info
   ```

9. **Run Celery beat** (in separate terminal, for scheduled tasks)
   ```bash
   celery -A qrcs_project beat -l info
   ```

## Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **Run migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

3. **Create superuser**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

## API Documentation

Once the server is running, access the API documentation at:
- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/schema/`

## API Endpoints

### Authentication
- `POST /api/auth/login/` - Login and get JWT tokens
- `POST /api/auth/refresh/` - Refresh JWT token

### Incidents
- `GET /api/incidents/` - List incidents
- `POST /api/incidents/` - Create incident
- `GET /api/incidents/{id}/` - Get incident details
- `PUT /api/incidents/{id}/` - Update incident
- `POST /api/incidents/{id}/update_status/` - Update incident status
- `GET /api/incidents/nearby/` - Get nearby incidents

### Response Teams
- `GET /api/response-teams/` - List response teams
- `POST /api/response-teams/` - Assign responder to incident
- `GET /api/response-logs/` - List response logs
- `POST /api/response-logs/` - Create response log

### Notifications
- `GET /api/notifications/` - List notifications
- `POST /api/notifications/{id}/mark_read/` - Mark notification as read
- `GET /api/notifications/unread_count/` - Get unread count

### Dashboard
- `GET /api/dashboard/stats/` - Get dashboard statistics
- `GET /api/dashboard/trends/` - Get incident trends

## Testing

Run tests:
```bash
python manage.py test
```

## License

This project is licensed under the MIT License.


