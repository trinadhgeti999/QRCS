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

