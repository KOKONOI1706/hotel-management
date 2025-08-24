# 📋 HƯỚNG DẪN DEPLOY LÊN VERCEL CHI TIẾT

## 🎯 Bước 1: Chuẩn bị GitHub Repository

### 1.1 Tạo repository trên GitHub:
1. Đi tới https://github.com
2. Click "New repository"
3. Đặt tên: `hotel-management`
4. Chọn "Public" hoặc "Private"
5. **KHÔNG** check "Add a README file"
6. Click "Create repository"

### 1.2 Liên kết local với GitHub:
```bash
# Mở terminal tại thư mục project
cd "d:\FPT\Summer 2025\hotel management"

# Chạy script setup (Windows)
.\deploy-setup.bat

# Hoặc thực hiện thủ công:
git init
git add .
git commit -m "Initial commit: Hotel Management System"

# Thay YOUR_USERNAME bằng username GitHub của bạn
git remote add origin https://github.com/YOUR_USERNAME/hotel-management.git
git branch -M main
git push -u origin main
```

## 🎯 Bước 2: Deploy lên Vercel

### 2.1 Đăng ký/Đăng nhập Vercel:
1. Đi tới https://vercel.com
2. Click "Sign Up" hoặc "Login"
3. Chọn "Continue with GitHub"
4. Authorize Vercel để truy cập GitHub

### 2.2 Tạo project mới:
1. Trong Vercel Dashboard, click "New Project"
2. Chọn "Import Git Repository"
3. Tìm và chọn repository `hotel-management`
4. Click "Import"

### 2.3 Cấu hình build settings:
```
Framework Preset: Other
Root Directory: Hotel-management-main/frontend
Build Command: npm run build
Output Directory: build
Install Command: npm install
```

### 2.4 Cấu hình Environment Variables:
1. Trong project settings, click "Environment Variables"
2. Thêm biến:
   - Name: `REACT_APP_BACKEND_URL`
   - Value: `https://your-project-name.vercel.app` (sẽ có sau khi deploy)

### 2.5 Deploy:
1. Click "Deploy"
2. Đợi quá trình build hoàn tất (2-5 phút)
3. Nhận được URL của ứng dụng

## 🎯 Bước 3: Cập nhật Environment Variables

### 3.1 Lấy URL đã deploy:
- Sau khi deploy thành công, copy URL (vd: https://hotel-management-abc123.vercel.app)

### 3.2 Cập nhật Environment Variables:
1. Quay lại Vercel Dashboard > Project Settings > Environment Variables
2. Sửa `REACT_APP_BACKEND_URL` thành URL thực tế
3. Click "Save"
4. Redeploy project (click "Redeploy" button)

## 🎯 Bước 4: Setup CI/CD với GitHub Actions

### 4.1 Lấy Vercel Token:
1. Đi tới https://vercel.com/account/tokens
2. Click "Create Token"
3. Đặt tên: "GitHub Actions"
4. Copy token (lưu lại để dùng)

### 4.2 Lấy Organization ID và Project ID:
```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Trong thư mục project
vercel link

# Lấy thông tin
vercel project ls
```

### 4.3 Thêm GitHub Secrets:
1. Đi tới GitHub repository > Settings > Secrets and variables > Actions
2. Click "New repository secret"
3. Thêm các secrets:

```
VERCEL_TOKEN = <token-từ-bước-4.1>
ORG_ID = <org-id-từ-bước-4.2>
PROJECT_ID = <project-id-từ-bước-4.2>
VERCEL_ORG_ID = <org-id-từ-bước-4.2>
```

## 🎯 Bước 5: Test CI/CD Pipeline

### 5.1 Tạo thay đổi nhỏ:
```bash
# Sửa title trong frontend/src/App.js
# Commit và push
git add .
git commit -m "Test CI/CD: Update title"
git push
```

### 5.2 Kiểm tra GitHub Actions:
1. Đi tới GitHub repository > Actions
2. Xem workflow đang chạy
3. Kiểm tra log để đảm bảo không có lỗi

## 🎯 Bước 6: Kiểm tra ứng dụng

### 6.1 Truy cập ứng dụng:
- URL: https://your-project-name.vercel.app
- Login: admin / admin123

### 6.2 Test các tính năng:
- ✅ Room Management
- ✅ Guest Management  
- ✅ Order Management
- ✅ Company Check-in
- ✅ Reporting

## 🔧 Troubleshooting

### Lỗi build frontend:
```bash
# Kiểm tra build locally
cd Hotel-management-main/frontend
npm install
npm run build
```

### Lỗi API không hoạt động:
1. Kiểm tra file `api/index.py`
2. Xem Vercel Functions logs
3. Đảm bảo routes trong `vercel.json` đúng

### Lỗi CORS:
- Kiểm tra CORS settings trong `api/index.py`
- Đảm bảo frontend gọi đúng API endpoint

## 📞 Support

Nếu gặp vấn đề:
1. Kiểm tra Vercel Function logs
2. Xem GitHub Actions logs
3. Test API endpoints trực tiếp
4. Kiểm tra Network tab trong DevTools

## 🎉 Hoàn thành!

Sau khi hoàn tất tất cả bước:
- ✅ Frontend deployed trên Vercel
- ✅ Backend API hoạt động với serverless functions
- ✅ CI/CD pipeline tự động
- ✅ Environment variables configured
- ✅ Domain accessible publicly

Project của bạn đã sẵn sàng cho production! 🚀
