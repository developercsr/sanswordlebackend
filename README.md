# Sanskrit Wordle Backend

Production-ready Django REST API for managing Sanskrit words with JWT authentication and role-based access control.

## Project Structure

```
sanswordlebackend/
├── manage.py
├── requirements.txt
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── core/
│   ├── exceptions.py    # Global error handling
│   ├── middleware.py    # Exception middleware
│   └── utils.py
├── apps/
│   ├── users/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views/
│   │   ├── urls/
│   │   ├── permissions.py
│   │   ├── admin.py
│   │   └── management/commands/create_default_admin.py
│   └── words/
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       ├── urls.py
│       ├── permissions.py
│       └── admin.py
└── db.sqlite3
```

## Technologies

- Django 5.x
- Django REST Framework
- SimpleJWT (JWT authentication)
- SQLite
- django-cors-headers
- django-filter

## Default Admin

On first migration, a default admin is created:
- **Email:** dhiyotek@gmail.com
- **Password:** Dhiyo@123
- **Role:** admin

## User Roles & Permissions

| Role | Permissions |
|------|-------------|
| **admin** | Full access, manage users, assign roles, manage all words |
| **word_manager** | Manage word uploaders/checkers, approve words, update/delete words |
| **word_checker** | Verify uploaded words |
| **word_uploader** | Upload words |

## API Endpoints

### Authentication
- `POST /api/auth/login/` - Login (email, password) → returns JWT tokens
- `POST /api/auth/refresh/` - Refresh access token

### Users (admin only)
- `GET /api/users/` - List users
- `POST /api/users/` - Create user
- `GET /api/users/<id>/` - Get user
- `PUT /api/users/<id>/` - Update user
- `DELETE /api/users/<id>/` - Delete user

### Profile
- `GET /api/profile/` - Get own profile
- `PUT /api/profile/` - Update own profile

### Words
- `GET /api/words/` - List words (paginated, search, filter by is_verified)
- `POST /api/words/` - Upload word
- `GET /api/words/<id>/` - Get word
- `PUT /api/words/<id>/` - Update word (manager/admin)
- `DELETE /api/words/<id>/` - Delete word (manager/admin)
- `POST /api/words/<id>/verify/` - Verify word (checker/manager/admin)

### Query params for words list
- `search` - Search in word and meaning
- `is_verified` - Filter (true/false)
- `page` - Page number (default 1)
- `page_size` - Items per page (default 20)

## Setup & Run

```bash
# Create virtual environment (optional)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create default admin (runs automatically via post_migrate)
python manage.py create_default_admin

# Start server
python manage.py runserver
```

Server runs at http://127.0.0.1:8000/

## Authentication

Include JWT token in requests:
```
Authorization: Bearer <access_token>
```

Login request:
```json
POST /api/auth/login/
{
  "email": "dhiomXXXXXXXXX",
  "password": "D23XXXXXXXXX"
}
```
