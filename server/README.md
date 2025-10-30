# Study Assistant Backend

FastAPI backend for the LLM-Powered Study Assistant application with JWT authentication.

## Features

- JWT-based authentication (register, login, logout)
- User management with secure password hashing
- Material upload and processing (PDF/Text)
- LLM integration for summaries, quizzes, and concept extraction
- PostgreSQL database with SQLAlchemy ORM
- RESTful API design

## Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL database
- pip or conda for package management

### Local Development

1. **Clone and navigate to server directory**
   ```bash
   cd server
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   
   Update `.env` file with your database credentials:
   ```env
   DATABASE_URL=postgresql://username:password@localhost:5432/study_assistant
   JWT_SECRET=your-secret-key-change-this-in-production
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

4. **Create PostgreSQL database**
   ```sql
   CREATE DATABASE study_assistant;
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

   The API will be available at `http://localhost:8000`

6. **Test the authentication**
   ```bash
   python test_auth.py
   ```

### API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user info
- `POST /auth/logout` - Logout user

### Materials
- `POST /materials/upload-material` - Upload study material
- `GET /materials/history` - Get user's upload history
- `GET /materials/{material_id}` - Get specific material

### LLM Processing
- `POST /llm/generate-summary/{material_id}` - Generate summary
- `POST /llm/generate-quiz/{material_id}` - Generate quiz questions
- `POST /llm/extract-concepts/{material_id}` - Extract key concepts

## Database Schema

### Users Table
- `id` (Primary Key)
- `email` (Unique)
- `username` (Unique)
- `hashed_password`
- `is_active`
- `created_at`

### Materials Table
- `id` (Primary Key)
- `title`
- `content`
- `file_type`
- `uploaded_at`
- `user_id` (Foreign Key)

### Generated Data Table
- `id` (Primary Key)
- `material_id` (Foreign Key)
- `summary`
- `quiz_questions` (JSON)
- `key_concepts` (JSON)
- `generated_at`

## Security Features

- Password hashing with bcrypt
- JWT token authentication
- Protected routes with user authorization
- Input validation with Pydantic
- CORS configuration for frontend integration

## Docker Support

Build and run with Docker:

```bash
docker build -t study-assistant-backend .
docker run -p 8000:8000 study-assistant-backend
```

## Development Notes

- The LLM functions in `routers/llm.py` are currently mock implementations
- Replace mock functions with actual LLM API calls (OpenAI, Anthropic, etc.)
- Database migrations can be managed with Alembic
- Add proper logging and error handling for production use

## Testing

Run the authentication test:
```bash
python test_auth.py
```

This will test the complete auth flow: registration → login → protected route access.