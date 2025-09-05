# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the FastAPI backend component of the Sk8Brigade Social Skate Network. It provides RESTful API endpoints for user authentication, spot discovery, session management, and social features for the React Native mobile application.

## Development Commands

### Core Development
- `python main.py` - Start FastAPI development server on http://localhost:8000
- `uvicorn main:app --reload --host 0.0.0.0 --port 8000` - Alternative start command with uvicorn directly

### Database Management
- `alembic revision --autogenerate -m "Description"` - Generate new database migration
- `alembic upgrade head` - Apply all pending migrations
- `alembic downgrade -1` - Rollback one migration
- `alembic current` - Show current migration version
- `alembic history` - Show migration history

### Dependencies
- `pip install -r requirements.txt` - Install Python dependencies
- `pip freeze > requirements.txt` - Update requirements file

### Testing & Code Quality
- `pytest` - Run all tests
- `pytest -v` - Run tests with verbose output
- `black .` - Format code with Black
- `isort .` - Sort imports

## Architecture Overview

### Directory Structure
```
backend/
├── app/
│   ├── api/v1/           # API route handlers organized by domain
│   │   ├── auth.py       # Authentication endpoints (/auth/*)
│   │   ├── users.py      # User management endpoints (/users/*)
│   │   └── spots.py      # Spot management endpoints (/spots/*)
│   ├── core/             # Core application functionality
│   │   ├── auth.py       # JWT token creation/validation logic
│   │   ├── config.py     # Pydantic settings management
│   │   ├── database.py   # Async SQLAlchemy engine and session factory
│   │   └── database_sync.py  # Synchronous database utilities for migrations
│   ├── models/           # SQLAlchemy database models
│   │   ├── user.py       # User, SkaterProfile, ShopProfile, UserFollow models
│   │   ├── spot.py       # Spot, SpotImage, SpotRating models
│   │   ├── session.py    # Session, SessionParticipant models
│   │   └── post.py       # Post, PostLike, PostComment models
│   └── schemas/          # Pydantic request/response schemas
├── migrations/           # Alembic database migration files
│   └── versions/         # Auto-generated migration scripts
├── main.py              # FastAPI application entry point and configuration
├── alembic.ini          # Alembic migration configuration
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
└── .env                # Local environment variables (not in git)
```

### Key Architecture Patterns

**Async-First Design**: All database operations use async/await with asyncpg driver for PostgreSQL connectivity.

**Layered Architecture**: 
- API layer handles HTTP requests/responses and validation
- Core layer contains business logic and utilities
- Models layer defines database schema and relationships
- Schemas layer handles data serialization/validation

**JWT Authentication**: Token-based auth with configurable expiration, using passlib for password hashing.

**Database Session Management**: FastAPI dependency injection provides async database sessions to route handlers.

## Database Schema

### Core Tables
- **users**: Base user accounts (UUID primary keys)
- **skater_profiles**: Skater-specific data (JSON setup, skills, preferences)
- **shop_profiles**: Skateshop-specific data (address, brands, contact info)
- **spots**: Skate spots with location data (PostGIS-ready for geo queries)
- **sessions**: Organized skate sessions with participant tracking
- **posts**: Social media posts with like/comment support
- **user_follows**: Many-to-many user relationships

### Key Model Relationships
- Users have optional skater_profile OR shop_profile (account_type field determines)
- Users can create spots, sessions, and posts (creator relationships)
- UserFollow enables bidirectional following with follower/following counts
- All models use UUID primary keys and include created_at/updated_at timestamps

## Configuration & Environment

### Required Environment Variables (.env)
```env
# Neon.tech Database (must use postgresql+asyncpg:// prefix)
DATABASE_URL=postgresql+asyncpg://user:pass@host.neon.tech/db?sslmode=require

# JWT Authentication
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Origins (comma-separated for production)
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8081", "exp://localhost:19000"]

# Environment
ENVIRONMENT=development
DEBUG=true
```

### Settings Management
Configuration is managed via Pydantic Settings in `app/core/config.py` with automatic .env file loading and type validation.

## API Documentation

When running, interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Authentication Flow
1. POST `/api/v1/auth/register` - Create account (returns JWT token)
2. POST `/api/v1/auth/login` - Authenticate user (returns JWT token)
3. Include `Authorization: Bearer {token}` header in subsequent requests
4. GET `/api/v1/auth/me` - Get current authenticated user profile

### Key API Patterns
- All endpoints use `/api/v1/` prefix for versioning
- UUIDs used for all resource identifiers
- Consistent error responses with HTTP status codes
- Request/response validation via Pydantic schemas
- Pagination available for list endpoints

## Development Setup

### Prerequisites
- Python 3.9+ (recommend Python 3.11+)
- Neon.tech PostgreSQL database account
- Git for version control

### Initial Setup
1. **Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

2. **Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**:
   ```bash
   cp .env.example .env
   # Edit .env with your Neon.tech credentials
   ```

4. **Database Migrations**:
   ```bash
   alembic upgrade head
   ```

### Database Migration Workflow
1. Modify models in `app/models/` directory
2. Generate migration: `alembic revision --autogenerate -m "Description"`
3. Review generated migration in `migrations/versions/`
4. Apply migration: `alembic upgrade head`
5. Test changes thoroughly before committing

## Tech Stack Details

**Core Framework**: FastAPI 0.104+ with async request handling and automatic OpenAPI documentation generation.

**Database**: PostgreSQL via Neon.tech with async SQLAlchemy 2.0+ and asyncpg driver for optimal performance.

**Authentication**: JWT tokens using python-jose with bcrypt password hashing via passlib.

**Validation**: Pydantic v2 for request/response validation and settings management.

**Migrations**: Alembic for database schema versioning and migration management.

**ASGI Server**: Uvicorn with hot-reloading for development.

## Integration Notes

This backend is designed to integrate with the React Native mobile app in the `/mobile` directory. The mobile app uses React Query for API state management and expects:
- JWT token authentication
- JSON request/response format
- RESTful endpoint patterns
- UUID-based resource identification
- Location-based queries for spots and sessions