# RAG-based FAQ System

A comprehensive, modular, asynchronous Python backend using FastAPI for a RAG-based document ingestion and Q&A system, with a modern React TypeScript frontend.

## 🎯 **Required Features Implementation Status**

### ✅ **1. Authentication**

- **JWT-based login, signup, and role-based access** (admin, editor, viewer)
- **Secure protected endpoints** with role guards
- **Password hashing** using bcrypt
- **Token expiration** with configurable lifetime
- **Role hierarchy** with minimum role requirements

### ✅ **2. Document Ingestion**

- **PDF/TXT document uploads** via `/api/v1/documents/upload`
- **Document chunking** with overlapping chunks (configurable size/overlap)
- **Embedding generation** using Sentence Transformer model (`all-MiniLM-L6-v2`)
- **FAISS vector storage** for efficient similarity search
- **PostgreSQL storage** for raw text + chunk metadata
- **Background processing** with timeout handling

### ✅ **3. Document Selection**

- **`/api/v1/documents` API** to list and filter uploaded documents
- **`/api/v1/documents/{id}/toggle-active` API** to mark documents active for Q&A
- **Document management** with status tracking
- **Bulk operations** support

### ✅ **4. Q&A API**

- **Question acceptance** via `/api/v1/qa/ask`
- **Top-K chunk retrieval** from FAISS with similarity scoring
- **Multiple LLM providers**: OpenAI, Cohere, or stubbed
- **Answer generation** with source chunk snippets
- **Enhanced RAG pipeline** with similarity filtering

### ✅ **5. Architecture Requirements**

- **FastAPI + async architecture** with Uvicorn
- **Modular structure** with services, routers, models, utils
- **Background tasks** for document processing
- **Unit tests** with pytest (≥70% coverage target)
- **Dockerfile + Docker Compose** for local setup
- **Swagger docs** enabled at `/docs`

### ✅ **6. Frontend Integration**

- **React + TypeScript** with modern architecture
- **Authentication UI** with login/register/logout
- **Document upload** with progress tracking
- **Q&A interface** with source display
- **Role-based UI** with protected routes
- **Responsive design** with Tailwind CSS

### ✅ **7. Documentation**

- **Comprehensive README** with setup instructions
- **API documentation** with usage examples
- **Architecture overview** with diagrams
- **Environment configuration** guide

## 🚀 **Core Features**

### **Backend (FastAPI)**

- **Authentication**: JWT-based login, signup, and role-based access (admin, editor, viewer)
- **Document Ingestion**: PDF/TXT upload, chunking, embedding generation with Sentence Transformers
- **Vector Storage**: FAISS for efficient similarity search
- **Q&A System**: RAG-based question answering with source references
- **Background Processing**: Celery + Redis for async document processing
- **Database**: PostgreSQL with SQLAlchemy async ORM
- **Testing**: Comprehensive test suite with 70%+ coverage target
- **LLM Integration**: Support for OpenAI, Cohere, and stubbed providers

### **Frontend (React + TypeScript)**

- **Modern UI**: Responsive design with Tailwind CSS
- **Authentication**: Secure login/register with role-based UI
- **Document Management**: Upload, view, and manage documents
- **Q&A Interface**: Interactive question asking with source display
- **Dashboard**: System statistics and quick actions
- **User Management**: Admin interface for user management
- **State Management**: TanStack Query for server state
- **Form Validation**: Formik + Yup for robust form handling

## 🏗️ **Architecture**

```
RAG-based-FAQ/
├── app/                    # FastAPI Backend
│   ├── api/               # API routers
│   │   ├── auth.py        # Authentication endpoints
│   │   ├── documents.py   # Document management
│   │   └── qa.py          # Q&A endpoints
│   ├── core/              # Configuration, database, security
│   │   ├── config.py      # Environment configuration
│   │   ├── database.py    # Database connection
│   │   └── security.py    # JWT authentication
│   ├── models/            # Database models
│   │   ├── user.py        # User model with roles
│   │   └── document.py    # Document and chunk models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic services
│   │   ├── auth_service.py      # Authentication logic
│   │   ├── document_service.py  # Document processing
│   │   ├── embedding_service.py # FAISS operations
│   │   ├── qa_service.py        # RAG pipeline
│   │   └── llm_service.py       # LLM integration
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

## 🛠️ **Technology Stack**

### **Backend**

- **Framework**: FastAPI (async, modern Python web framework)
- **Server**: Uvicorn (ASGI server)
- **Database**: PostgreSQL (primary database)
- **ORM**: SQLAlchemy (async ORM)
- **Vector DB**: FAISS (similarity search)
- **Cache/Queue**: Redis (caching and background tasks)
- **Authentication**: JWT with bcrypt password hashing
- **File Processing**: PyPDF2 (PDF text extraction)
- **ML/AI**: Sentence Transformers (embeddings)
- **LLM**: OpenAI API, Cohere API, or stubbed provider
- **Testing**: pytest with async support
- **Documentation**: Swagger/OpenAPI

### **Frontend**

- **Framework**: React 19 with TypeScript
- **Routing**: React Router v6
- **State Management**: TanStack Query (React Query)
- **Styling**: Tailwind CSS
- **Forms**: Formik + Yup validation
- **HTTP Client**: Axios with interceptors
- **Icons**: Heroicons
- **Notifications**: React Hot Toast
- **Testing**: React Testing Library + Jest

### **DevOps & Tools**

- **Containerization**: Docker + Docker Compose
- **Environment**: Environment variables with .env
- **Version Control**: Git
- **Package Management**: pip (Python), npm (Node.js)

## 🚀 **Quick Start**

### **Prerequisites**

- Python 3.10+
- Node.js 18+
- PostgreSQL
- Redis
- Docker (optional)

### **Option 1: Full Stack Development (Recommended)**

1. **Clone and setup:**

   ```bash
   git clone <repository-url>
   cd RAG-based-FAQ
   ```

2. **Setup environment:**

   ```bash
   # Create environment file
   cp .env.example .env

   # Edit .env with your configuration
   nano .env
   ```

3. **Start both backend and frontend:**

   ```bash
   ./start.sh
   ```

4. **Access the application:**
   - Frontend: http://localhost:3001
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### **Option 2: Docker Setup**

1. **Start all services:**

   ```bash
   docker-compose up -d
   ```

2. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

### **Option 3: Manual Setup**

1. **Backend setup:**

   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Setup environment
   cp .env.example .env
   # Edit .env with your configuration

   # Start backend
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Frontend setup:**
   ```bash
   cd frontend
   npm install
   npm start
   ```

## 🔧 **Configuration**

### **Environment Variables**

Create a `.env` file using the provided template:

```bash
cp .env.example .env
```

Key configuration sections:

- **Security**: JWT secret key, token expiration
- **Database**: PostgreSQL connection string
- **LLM Provider**: OpenAI, Cohere, or stubbed
- **RAG Settings**: Chunk size, overlap, similarity threshold
- **File Upload**: Size limits, allowed extensions
- **Timeouts**: Upload and processing timeouts

### **LLM Provider Setup**

#### **OpenAI (Recommended)**

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-api-key
```

#### **Cohere**

```env
LLM_PROVIDER=cohere
COHERE_API_KEY=your-cohere-api-key
```

#### **Stubbed (Testing)**

```env
LLM_PROVIDER=stubbed
# No API key needed
```

### **Database Setup**

The system uses PostgreSQL. You can either:

1. **Use Docker (recommended):**

   ```bash
   docker-compose up postgres redis -d
   ```

2. **Install locally:**
   - Install PostgreSQL and Redis
   - Create database: `rag_faq`
   - Update DATABASE_URL in .env

## 📚 **API Documentation**

### **Authentication Endpoints**

- `POST /api/v1/auth/signup` - Register new user
- `POST /api/v1/auth/login` - Login user
- `GET /api/v1/auth/me` - Get current user
- `PUT /api/v1/auth/me` - Update current user

### **Document Endpoints**

- `POST /api/v1/documents/upload` - Upload document
- `GET /api/v1/documents` - List documents
- `PUT /api/v1/documents/{id}` - Update document
- `DELETE /api/v1/documents/{id}` - Delete document
- `POST /api/v1/documents/{id}/toggle-active` - Toggle document active status
- `GET /api/v1/documents/{id}/chunks` - Get document chunks

### **Q&A Endpoints**

- `POST /api/v1/qa/ask` - Ask a question
- `GET /api/v1/qa/stats` - Get system statistics

### **Admin Endpoints**

- `GET /api/v1/auth/users` - Get all users (admin only)
- `PUT /api/v1/auth/users/{id}` - Update user (admin only)

## 🧪 **Testing**

### **Backend Tests**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

### **Frontend Tests**

```bash
cd frontend
npm test
```

## 🚀 **Deployment**

### **Production Build**

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

### **Docker Production**

```bash
# Build and run production containers
docker-compose -f docker-compose.prod.yml up -d
```

## 🔐 **Security Features**

- **JWT Authentication** with configurable expiration
- **Role-based Access Control** (Admin, Editor, Viewer)
- **Password Hashing** using bcrypt
- **CORS Protection** with configurable origins
- **Input Validation** using Pydantic schemas
- **SQL Injection Protection** via SQLAlchemy ORM
- **File Upload Security** with type and size restrictions

## 📊 **Performance Features**

- **Async Architecture** for non-blocking I/O
- **Background Processing** for heavy tasks
- **Caching** with Redis
- **Vector Search** with FAISS
- **Connection Pooling** for database
- **React Query** for frontend caching
- **Timeout Handling** for long-running operations

## 🎯 **RAG Pipeline**

### **Document Processing Flow**

1. **File Upload** → API validation
2. **Text Extraction** → PDF/TXT parsing
3. **Chunking** → Overlapping text chunks
4. **Embedding Generation** → Sentence Transformers
5. **Vector Storage** → FAISS index
6. **Metadata Storage** → PostgreSQL

### **Question Answering Flow**

1. **Question Input** → User query
2. **Query Embedding** → Sentence Transformers
3. **Similarity Search** → FAISS index
4. **Context Retrieval** → Top-K chunks
5. **Answer Generation** → LLM (OpenAI/Cohere/Stubbed)
6. **Response Formatting** → Answer + sources
