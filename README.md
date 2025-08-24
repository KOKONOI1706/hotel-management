# 🏨 Hotel Management System

A comprehensive hotel management system built with React (frontend) and FastAPI (backend), deployed on Vercel with CI/CD.

## 🚀 Features

- **Room Management**: Check-in/check-out, pricing, room status
- **Guest Management**: Individual and company guest management
- **Order Management**: Food orders with filtering and reporting
- **Reservation System**: Room reservations and booking management
- **Real-time Cost Calculation**: Hourly, daily, and monthly rates
- **Company Reporting**: Detailed analytics and reports

## 🛠 Tech Stack

- **Frontend**: React 18, Tailwind CSS, Axios
- **Backend**: FastAPI (Serverless), Python 3.9
- **Database**: JSON file storage (temporary for Vercel)
- **Deployment**: Vercel with CI/CD
- **Authentication**: Simple admin login system

## 📁 Project Structure

```
hotel-management/
├── Hotel-management-main/
│   ├── frontend/           # React application
│   └── backend/           # Original FastAPI server
├── api/                   # Vercel serverless functions
├── .github/workflows/     # GitHub Actions CI/CD
├── vercel.json           # Vercel configuration
├── package.json          # Root package.json
└── README.md
```

## 🚀 Deployment Steps

### Prerequisites
- GitHub account
- Vercel account
- Node.js 18+
- Git

### 1. Clone and Setup
```bash
git clone <your-repo>
cd hotel-management
npm install
```

### 2. Deploy to Vercel

#### Option A: Vercel CLI
```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

#### Option B: GitHub Integration
1. Push code to GitHub
2. Go to [Vercel Dashboard](https://vercel.com/dashboard)
3. Click "New Project"
4. Import your GitHub repository
5. Configure build settings:
   - **Framework Preset**: Other
   - **Root Directory**: `Hotel-management-main/frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`

### 3. Environment Variables
Set these in Vercel Dashboard > Settings > Environment Variables:

```
REACT_APP_BACKEND_URL = https://your-project-name.vercel.app
```

### 4. GitHub Secrets (for CI/CD)
Add these secrets in GitHub repository settings:

```
VERCEL_TOKEN = <your-vercel-token>
ORG_ID = <your-vercel-org-id>
PROJECT_ID = <your-vercel-project-id>
VERCEL_ORG_ID = <your-vercel-org-id>
```

## 🔧 Local Development

### Frontend
```bash
cd Hotel-management-main/frontend
npm install
npm start
```

### Backend (Original)
```bash
cd Hotel-management-main/backend
pip install -r requirements.txt
python server.py
```

### API (Serverless)
```bash
cd api
pip install -r requirements.txt
uvicorn index:app --reload
```

## 📱 Usage

### Default Login
- **Username**: `admin`
- **Password**: `admin123`

### Main Features
1. **Room Management**: Manage hotel rooms, check-in/check-out
2. **Guest Management**: Add and manage guest information
3. **Orders**: Create and track food orders
4. **Reservations**: Handle room reservations
5. **Reports**: View analytics and company reports

## 🔄 CI/CD Pipeline

The project uses GitHub Actions for automated deployment:

1. **On Pull Request**: Deploy preview version
2. **On Push to Main**: Deploy to production
3. **Tests**: Run frontend build tests
4. **Auto-deploy**: Automatic deployment to Vercel

## 📊 Database

Currently uses JSON file storage for simplicity on Vercel. For production, consider:

- **Vercel KV** (Redis)
- **PlanetScale** (MySQL)
- **Supabase** (PostgreSQL)
- **MongoDB Atlas**

## 🛡 Security

- Basic authentication system
- CORS configured for security
- Environment variables for sensitive data
- Input validation and error handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🚀 Live Demo

Visit: [Your deployed application URL]

## 📞 Support

For issues and questions, please create an issue in the GitHub repository.
