#!/bin/bash

# Hotel Management Backend Deployment Script

echo "🚀 Deploying Hotel Management Backend to Vercel..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Login to Vercel (if not already logged in)
echo "🔐 Checking Vercel authentication..."
vercel whoami || vercel login

# Set environment variables in Vercel
echo "⚙️ Setting up environment variables..."
echo "Please set these environment variables in Vercel dashboard:"
echo "1. MONGO_URL (your MongoDB Atlas connection string)"
echo "2. DB_NAME (hotel_management)"
echo "3. CORS_ORIGINS (your frontend URLs)"

# Deploy to Vercel
echo "🚀 Deploying to Vercel..."
vercel --prod

echo "✅ Deployment complete!"
echo "📝 Don't forget to:"
echo "   1. Set environment variables in Vercel dashboard"
echo "   2. Update frontend API URL to point to your new backend"
echo "   3. Test all endpoints"
