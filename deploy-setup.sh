#!/bin/bash

echo "🚀 Hotel Management - Deploy to Vercel Setup"
echo "============================================"

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
else
    echo "✅ Git repository already initialized"
fi

# Add all files
echo "📦 Adding files to Git..."
git add .

# Create initial commit
echo "💾 Creating initial commit..."
git commit -m "Initial commit: Hotel Management System ready for Vercel deployment

Features:
- React frontend with modern UI
- FastAPI backend converted to serverless functions
- Complete hotel management system
- CI/CD with GitHub Actions
- Vercel deployment configuration

Components:
- Room management with company check-in
- Guest management system
- Order management with filtering
- Reservation system
- Real-time cost calculation
- Company reporting and analytics"

# Instructions for user
echo ""
echo "🔧 Next Steps:"
echo "1. Create a new repository on GitHub"
echo "2. Copy the repository URL"
echo "3. Run: git remote add origin <your-github-repo-url>"
echo "4. Run: git branch -M main"
echo "5. Run: git push -u origin main"
echo ""
echo "📚 Then follow the Vercel deployment steps in README.md"
echo ""
echo "🌐 GitHub Repository Setup Commands:"
echo "git remote add origin https://github.com/your-username/hotel-management.git"
echo "git branch -M main"
echo "git push -u origin main"
