# Sk8Brigade Backend API

FastAPI backend for the Sk8Brigade Social Skate Network mobile application.

## Features

- **User Management**: Authentication, profiles for skaters and skateshops
- **Spot Discovery**: Location-based skate spot management with ratings and images
- **Social Features**: Follow/unfollow users, posts, comments, likes
- **Session Management**: Organize and join skate sessions
- **Geographic Search**: Location-based spot and session discovery
- **JWT Authentication**: Secure token-based authentication
- **PostgreSQL Database**: Async database operations with SQLAlchemy

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **PostgreSQL**: Database hosted on Neon.tech
- **SQLAlchemy**: Async ORM with Alembic migrations
- **JWT**: Token-based authentication
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server

## Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL database (Neon.tech account)

### Installation

1. **Clone and navigate to backend**:
```bash
cd backend
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Environment setup**:
```bash
cp .env.example .env
# Edit .env with your Neon.tech database credentials
```

5. **Initialize database**:
```bash
# Generate initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

6. **Start development server**:
```bash
python main.py
# Or with uvicorn directly:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## Database Setup (Neon.tech)

1. **Create Neon Project**:
   - Go to [neon.tech](https://neon.tech)
   - Create a new project
   - Note your database connection string

2. **Configure Environment**:
   ```env
   DATABASE_URL=postgresql+asyncpg://username:password@ep-cool-name-123456.us-east-2.aws.neon.tech/sk8brigade?sslmode=require
   ```

3. **Run Migrations**:
   ```bash
   alembic upgrade head
   ```

## API Documentation

Once running, visit:
- **Interactive Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/auth/me` - Get current user

### Users
- `GET /api/v1/users/` - List users with filtering
- `GET /api/v1/users/{user_id}` - Get user profile
- `PUT /api/v1/users/profile` - Update profile
- `POST /api/v1/users/{user_id}/follow` - Follow user
- `DELETE /api/v1/users/{user_id}/follow` - Unfollow user

### Spots
- `GET /api/v1/spots/` - List spots with location filtering
- `POST /api/v1/spots/` - Create new spot
- `GET /api/v1/spots/{spot_id}` - Get spot details
- `PUT /api/v1/spots/{spot_id}` - Update spot
- `POST /api/v1/spots/{spot_id}/ratings` - Rate spot
- `POST /api/v1/spots/{spot_id}/images` - Add spot image

## Project Structure

```
backend/
├── app/
│   ├── api/v1/           # API route handlers
│   │   ├── auth.py       # Authentication endpoints
│   │   ├── users.py      # User management
│   │   └── spots.py      # Spot management
│   ├── core/             # Core functionality
│   │   ├── auth.py       # Authentication logic
│   │   ├── config.py     # Configuration settings
│   │   └── database.py   # Database connection
│   ├── models/           # SQLAlchemy models
│   │   ├── user.py       # User models
│   │   ├── spot.py       # Spot models
│   │   ├── session.py    # Session models
│   │   └── post.py       # Post models
│   └── schemas/          # Pydantic schemas
├── migrations/           # Alembic database migrations
├── main.py              # FastAPI application entry point
├── requirements.txt     # Python dependencies
└── .env.example        # Environment variables template
```

## Authentication

The API uses JWT tokens for authentication:

1. Register or login to get an access token
2. Include token in Authorization header: `Bearer {token}`
3. Tokens expire after 30 minutes (configurable)

## Development

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
isort .
```

## Deployment

### Environment Variables

For production, ensure these are set:
- `DATABASE_URL`: Your Neon.tech connection string
- `SECRET_KEY`: Strong JWT secret key
- `ENVIRONMENT=production`
- `DEBUG=false`

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Security Features

- Password hashing with bcrypt
- JWT token authentication
- SQL injection protection via SQLAlchemy
- Input validation with Pydantic
- CORS configuration for frontend access

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Run linting and tests
5. Submit a pull request