# RAG-based FAQ System

A comprehensive, modular, asynchronous Python backend using FastAPI for a RAG-based document ingestion and Q&A system, with a modern React TypeScript frontend.

## 🚀 Features

### Backend (FastAPI)

- **Authentication**: JWT-based login, signup, and role-based access (admin, editor, viewer)
- **Document Ingestion**: PDF/TXT upload, chunking, embedding generation with Sentence Transformers
- **Vector Storage**: FAISS for efficient similarity search
- **Q&A System**: RAG-based question answering with source references
- **Background Processing**: Celery + Redis for async document processing
- **Database**: PostgreSQL with SQLAlchemy async ORM
- **Testing**: Comprehensive test suite with 70%+ coverage target

### Frontend (React + TypeScript)

- **Modern UI**: Responsive design with Tailwind CSS
- **Authentication**: Secure login/register with role-based UI
- **Document Management**: Upload, view, and manage documents
- **Q&A Interface**: Interactive question asking with source display
- **Dashboard**: System statistics and quick actions
- **User Management**: Admin interface for user management
- **State Management**: TanStack Query for server state

## 🏗️ Architecture

```
RAG-based-FAQ/
├── app/                    # FastAPI Backend
│   ├── api/               # API routers
│   ├── core/              # Configuration, database, security
│   ├── models/            # Database models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic services
│   ├── tasks/             # Background tasks
│   ├── utils/             # Utility functions
│   └── main.py            # FastAPI application
├── frontend/              # React Frontend
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── context/       # React context providers
│   │   ├── pages/         # Page components
│   │   ├── services/      # API service layer
│   │   ├── types/         # TypeScript types
│   │   └── App.tsx        # Main application
│   └── package.json
├── tests/                 # Backend tests
├── docker-compose.yml     # Local development setup
├── Dockerfile             # Backend container
├── requirements.txt       # Python dependencies
└── package.json           # Root package.json
```

## 🚀 Quick Start

### Option 1: Full Stack Development (Recommended)

1. **Clone and setup:**

   ```bash
   git clone <repository-url>
   cd RAG-based-FAQ
   npm install
   npm run install:all
   ```

2. **Start both backend and frontend:**

   ```bash
   npm run start:dev
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Option 2: Docker Setup

1. **Start all services:**

   ```bash
   docker-compose up -d
   ```

2. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

### Option 3: Backend Only

1. **Setup Python environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Start backend:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Option 4: Frontend Only

1. **Setup frontend:**

   ```bash
   cd frontend
   npm install
   ```

2. **Start frontend:**
   ```bash
   npm start
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Backend Configuration
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/rag_faq
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000/api/v1
```

### Database Setup

The system uses PostgreSQL. You can either:

1. **Use Docker (recommended):**

   ```bash
   docker-compose up postgres redis -d
   ```

2. **Install locally:**
   - Install PostgreSQL and Redis
   - Create database: `rag_faq`
   - Update DATABASE_URL in .env

## 📚 API Documentation

### Authentication Endpoints

- `POST /api/v1/auth/signup` - Register new user
- `POST /api/v1/auth/login` - Login user
- `GET /api/v1/auth/me` - Get current user

### Document Endpoints

- `POST /api/v1/documents/upload` - Upload document
- `GET /api/v1/documents` - List documents
- `PUT /api/v1/documents/{id}` - Update document
- `DELETE /api/v1/documents/{id}` - Delete document
- `POST /api/v1/documents/{id}/toggle-active` - Toggle document active status

### Q&A Endpoints

- `POST /api/v1/qa/ask` - Ask a question
- `GET /api/v1/qa/stats` - Get system statistics

## 🧪 Testing

### Backend Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 🚀 Deployment

### Production Build

1. **Build frontend:**

   ```bash
   cd frontend
   npm run build
   ```

2. **Deploy backend:**

   ```bash
   # Using Docker
   docker-compose -f docker-compose.prod.yml up -d

   # Or directly
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

### Docker Production

```bash
# Build and run production containers
docker-compose -f docker-compose.prod.yml up -d
```

## 🔐 Security Features

- **JWT Authentication** with configurable expiration
- **Role-based Access Control** (Admin, Editor, Viewer)
- **Password Hashing** using bcrypt
- **CORS Protection** with configurable origins
- **Input Validation** using Pydantic schemas
- **SQL Injection Protection** via SQLAlchemy ORM

## 📊 Performance Features

- **Async Architecture** for non-blocking I/O
- **Background Processing** for heavy tasks
- **Caching** with Redis
- **Vector Search** with FAISS
- **Connection Pooling** for database
- **React Query** for frontend caching

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:

1. Check the documentation
2. Review the API docs at `/docs`
3. Check the test files for usage examples
4. Open an issue on GitHub

## 🔮 Roadmap

- [ ] Real-time notifications
- [ ] Advanced document search
- [ ] Document versioning
- [ ] Multi-language support
- [ ] Advanced analytics
- [ ] API rate limiting
- [ ] WebSocket support
- [ ] Mobile app
