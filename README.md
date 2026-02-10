# User Management System

A full-stack web application for managing users with authentication, profile management, and admin panel.

## 🚀 Tech Stack

### Frontend
- **React** 19.2.0 - UI library
- **React Router** - Navigation
- **Tailwind CSS** - Styling
- **React Hook Form** + **Yup** - Form validation
- **Axios** - API requests
- **Vite** - Build tool

### Backend
- **Flask** 3.0.0 - Web framework
- **SQLAlchemy** - ORM
- **Flask-JWT-Extended** - Authentication
- **Flask-CORS** - Cross-origin support
- **Cloudinary** - Image storage
- **bcrypt** - Password hashing
- **PyMySQL** - MySQL driver

## 📁 Project Structure

```
user_management_system/
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/   # Reusable components
│   │   ├── pages/        # Page components
│   │   ├── context/      # React context (Auth)
│   │   ├── config/       # API configuration
│   │   └── utils/        # Utility functions
│   ├── public/           # Static assets
│   └── package.json
│
├── backend/              # Flask backend
│   ├── controllers/      # Request handlers
│   ├── models/          # Database models
│   ├── routes/          # API routes
│   ├── middleware/      # Auth middleware
│   ├── utils/           # Helper functions
│   ├── app.py           # Main application
│   ├── config.py        # Configuration
│   ├── database.py      # Database setup
│   └── requirements.txt
│
├── wsgi.py              # WSGI config for PythonAnywhere
└── README.md
```

## ✨ Features

- **User Authentication**
  - Register with email and phone
  - Login with JWT tokens
  - Secure password hashing

- **Profile Management**
  - View and edit profile
  - Upload profile images (Cloudinary)
  - Update personal information

- **Admin Panel**
  - View all users
  - Delete users
  - Pagination and search
  - User statistics

- **Security**
  - JWT-based authentication
  - Password validation
  - Protected routes
  - CORS configuration

## 🛠️ Local Development

### Prerequisites
- Python 3.8+
- Node.js 18+
- MySQL (optional, SQLite works too)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python init_db.py

# Run server
python app.py
```

Backend runs at: `http://localhost:5000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend runs at: `http://localhost:5173`

### Default Admin Credentials

After running `init_db.py`:
- **Email:** admin@example.com
- **Password:** admin123

## 🌐 Deployment

### Backend - PythonAnywhere

See [PYTHONANYWHERE_DEPLOYMENT.md](PYTHONANYWHERE_DEPLOYMENT.md) for detailed instructions.

**Quick Steps:**
1. Upload backend files to PythonAnywhere
2. Set up virtual environment and install dependencies
3. Configure `.env` file
4. Set up WSGI configuration
5. Initialize database
6. Reload web app

**Live Backend:** `http://divyanand.pythonanywhere.com`

### Frontend - Vercel

See [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) for detailed instructions.

**Quick Steps:**
1. Push code to GitHub
2. Connect GitHub repo to Vercel
3. Set root directory to `frontend`
4. Add environment variable: `VITE_API_URL`
5. Deploy!

**Environment Variable:**
```
VITE_API_URL=http://divyanand.pythonanywhere.com/api
```

## 📝 Environment Variables

### Backend (.env)

```env
FLASK_ENV=production
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=sqlite:///users.db
CORS_ORIGIN=https://your-frontend.vercel.app
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

### Frontend (.env.production)

```env
VITE_API_URL=http://divyanand.pythonanywhere.com/api
```

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Logout user

### Users
- `GET /api/users/profile` - Get current user profile
- `PUT /api/users/profile` - Update profile
- `POST /api/users/profile/image` - Upload profile image
- `GET /api/users` - Get all users (admin only)
- `GET /api/users/:id` - Get user by ID (admin only)
- `DELETE /api/users/:id` - Delete user (admin only)

### Health
- `GET /health` - Health check
- `GET /` - API information

## 🧪 Testing

```bash
# Backend
cd backend
python -m pytest

# Frontend
cd frontend
npm run test
```

## 🔒 Security Features

- Password hashing with bcrypt
- JWT token-based authentication
- Token refresh mechanism
- Protected routes with middleware
- Input validation with Yup
- CORS configuration
- File upload restrictions

## 📦 Database Schema

### User Model
```python
{
    "id": int,
    "name": string,
    "email": string (unique),
    "phone": string (unique),
    "password_hash": string,
    "role": enum("user", "admin"),
    "profile_image_url": string,
    "state": string,
    "city": string,
    "country": string,
    "pincode": string,
    "address": string,
    "created_at": datetime,
    "updated_at": datetime
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

**Divyanand L**

## 🙏 Acknowledgments

- Flask documentation
- React documentation
- Tailwind CSS
- Cloudinary
- PythonAnywhere
- Vercel

## 📞 Support

For issues and questions:
- Create an issue in this repository
- Check the deployment guides:
  - [PythonAnywhere Deployment](PYTHONANYWHERE_DEPLOYMENT.md)
  - [Vercel Deployment](VERCEL_DEPLOYMENT.md)

---

**Built with ❤️ using React and Flask**
