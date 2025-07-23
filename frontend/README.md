# RAG FAQ System - React Frontend

A modern, responsive React frontend for the RAG-based document ingestion and Q&A system. Built with TypeScript, Tailwind CSS, and React Query for optimal performance and developer experience.

## 🚀 Features

### Authentication & Authorization

- **JWT-based authentication** with secure token storage
- **Role-based access control** (Admin, Editor, Viewer)
- **Protected routes** with automatic redirects
- **Form validation** using Formik and Yup
- **Password visibility toggle** for better UX

### Document Management

- **File upload** with progress tracking (PDF, TXT)
- **Document listing** with filtering (All, Active, Inactive)
- **Document activation/deactivation** for Q&A scope control
- **File size and type validation**
- **Responsive document cards** with metadata display

### Q&A Interface

- **Intelligent question input** with character limits
- **Configurable source count** (3, 5, 10 sources)
- **Answer display** with copy-to-clipboard functionality
- **Source references** with similarity scores
- **Loading states** and error handling

### Dashboard & Analytics

- **System statistics** overview
- **Quick action buttons** for common tasks
- **Recent documents** display
- **Role-based UI** showing relevant information

### User Management (Admin)

- **User listing** with role and status information
- **Role hierarchy** visualization
- **Current user** information display

## 🛠️ Technology Stack

- **React 19** with TypeScript
- **React Router v6** for navigation
- **TanStack Query** for server state management
- **Formik + Yup** for form handling and validation
- **Tailwind CSS** for styling
- **Heroicons** for icons
- **React Hot Toast** for notifications
- **Axios** for API communication

## 📁 Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Navigation.tsx   # Main navigation bar
│   └── ProtectedRoute.tsx # Route protection wrapper
├── context/             # React context providers
│   └── AuthContext.tsx  # Authentication state management
├── pages/               # Page components
│   ├── Login.tsx        # Login page
│   ├── Register.tsx     # Registration page
│   ├── Dashboard.tsx    # Main dashboard
│   ├── Documents.tsx    # Document management
│   ├── QA.tsx          # Q&A interface
│   └── Users.tsx       # User management (admin)
├── services/            # API service layer
│   └── api.ts          # Axios configuration and API calls
├── types/               # TypeScript type definitions
│   └── index.ts        # Application types and interfaces
├── App.tsx             # Main application component
└── index.tsx           # Application entry point
```

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

### Installation

1. **Install dependencies:**

   ```bash
   npm install
   ```

2. **Start the development server:**

   ```bash
   npm start
   ```

3. **Open your browser:**
   Navigate to `http://localhost:3000`

### Environment Configuration

Create a `.env` file in the frontend directory:

```env
REACT_APP_API_URL=http://localhost:8000/api/v1
```

## 🔧 Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

## 🎨 UI Components

### Custom CSS Classes

The application uses custom Tailwind CSS classes defined in `src/index.css`:

- `.btn-primary` - Primary button styling
- `.btn-secondary` - Secondary button styling
- `.btn-danger` - Danger button styling
- `.input-field` - Form input styling
- `.card` - Card container styling

### Color Scheme

- **Primary**: Blue (`primary-600`, `primary-700`)
- **Success**: Green (`green-500`, `green-600`)
- **Warning**: Yellow (`yellow-500`, `yellow-600`)
- **Error**: Red (`red-500`, `red-600`)

## 🔐 Authentication Flow

1. **Login/Register** - User authenticates via forms
2. **Token Storage** - JWT stored in localStorage
3. **Route Protection** - ProtectedRoute component checks authentication
4. **API Interceptors** - Axios automatically adds auth headers
5. **Token Refresh** - Automatic logout on token expiry

## 📱 Responsive Design

The application is fully responsive with breakpoints:

- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px

## 🔄 State Management

- **Authentication State**: React Context (AuthContext)
- **Server State**: TanStack Query for API data
- **Form State**: Formik for form management
- **UI State**: React useState for local component state

## 🧪 Testing

The application is set up for testing with:

- **React Testing Library** for component testing
- **Jest** for test runner
- **TypeScript** support for tests

## 🚀 Deployment

### Production Build

```bash
npm run build
```

### Docker Deployment

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## 🔧 Configuration

### API Configuration

The API base URL can be configured via environment variables:

```env
REACT_APP_API_URL=http://localhost:8000/api/v1
```

### Feature Flags

You can add feature flags for conditional rendering:

```typescript
const FEATURES = {
  USER_MANAGEMENT: process.env.REACT_APP_ENABLE_USER_MANAGEMENT === "true",
  ADVANCED_QA: process.env.REACT_APP_ENABLE_ADVANCED_QA === "true",
};
```

## 🤝 Contributing

1. Follow the existing code style and patterns
2. Add TypeScript types for new features
3. Include proper error handling
4. Test your changes thoroughly
5. Update documentation as needed

## 📄 License

This project is part of the RAG FAQ System and follows the same license terms.

## 🆘 Support

For issues and questions:

1. Check the backend API is running
2. Verify environment variables are set correctly
3. Check browser console for errors
4. Ensure all dependencies are installed

## 🔮 Future Enhancements

- **Dark mode** support
- **Real-time notifications** using WebSockets
- **Advanced search** with filters
- **Document preview** functionality
- **Bulk operations** for documents
- **Export functionality** for Q&A results
- **Advanced analytics** dashboard
- **Multi-language** support
