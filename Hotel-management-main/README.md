# Hotel Management System

Hệ thống quản lý khách sạn/nhà hàng được xây dựng với FastAPI + MongoDB (Backend) và React (Frontend).

## 🚀 Tính năng chính

### 1. Quản lý phòng
- ✅ Danh sách phòng với trạng thái (trống, đã đặt, đang sử dụng)
- ✅ Check-in/Check-out với nhiều loại booking (theo giờ, ngày, tháng)
- ✅ Tính toán chi phí tự động theo thời gian
- ✅ Cập nhật giá phòng theo từng loại

### 2. Quản lý khách hàng
- ✅ Tạo, sửa, xóa thông tin khách hàng
- ✅ Lưu trữ thông tin: họ tên, điện thoại, email, CMND/CCCD
- ✅ Tìm kiếm và quản lý database khách hàng

### 3. Hệ thống đặt phòng
- ✅ Tạo đặt phòng trước với thông tin khách hàng
- ✅ Kiểm tra tình trạng phòng và xung đột lịch
- ✅ Chuyển đổi đặt phòng thành check-in
- ✅ Quản lý trạng thái đặt phòng (chờ xác nhận, đã xác nhận, đã hủy, đã check-in)

### 4. Quản lý món ăn & đơn hàng
- ✅ Thêm, sửa, xóa món ăn
- ✅ Tạo đơn hàng theo phòng
- ✅ Tính tổng hóa đơn bao gồm phòng + đồ ăn

### 5. Hệ thống hóa đơn nâng cao
- ✅ Hóa đơn chi tiết với itemization (phòng, dịch vụ, đồ ăn)
- ✅ Trạng thái thanh toán (chưa thanh toán, đã thanh toán)
- ✅ Xuất hóa đơn PDF với thông tin đầy đủ
- ✅ Lịch sử hóa đơn

### 6. Phân quyền người dùng
- ✅ 3 cấp độ: Admin, Manager, Receptionist
- ✅ Kiểm soát quyền truy cập từng tính năng
- ✅ System decorator cho phân quyền API

### 7. Báo cáo & thống kê
- ✅ Báo cáo doanh thu theo thời gian (ngày, tuần, tháng)
- ✅ Thống kê món ăn phổ biến
- ✅ Tỷ lệ sử dụng phòng theo loại
- ✅ Dashboard tổng quan

### 8. Xuất PDF
- ✅ Tạo hóa đơn PDF với thiết kế chuyên nghiệp
- ✅ Bao gồm thông tin khách hàng, phòng, chi tiết chi phí
- ✅ Có thể tải xuống trực tiếp từ hệ thống

## 🛠️ Công nghệ sử dụng

### Backend
- **FastAPI**: Modern, fast web framework for Python
- **MongoDB**: NoSQL database cho flexibility
- **Motor**: Async MongoDB driver
- **Pydantic**: Data validation và serialization
- **ReportLab**: PDF generation
- **python-multipart**: File upload support

### Frontend
- **React**: Component-based UI framework
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client cho API calls
- **Modern ES6+**: JavaScript features

## 📊 Cấu trúc Database

### Collections chính:
- `rooms`: Thông tin phòng, giá cả, trạng thái
- `guests`: Database khách hàng
- `reservations`: Đặt phòng với lịch trình
- `bills`: Hóa đơn cơ bản
- `enhanced_bills`: Hóa đơn nâng cao với itemization
- `orders`: Đơn hàng đồ ăn
- `dishes`: Menu món ăn
- `admins`: Tài khoản quản trị với phân quyền

## 🚀 Cài đặt và chạy

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm start
```

### Environment Variables
Tạo file `.env` trong thư mục `backend`:
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=hotel_management
CORS_ORIGINS=http://localhost:3000
```

## 📱 Sử dụng hệ thống

### Đăng nhập mặc định:
- Username: `admin`
- Password: `admin123`

### Workflow cơ bản:
1. **Thêm khách hàng** vào hệ thống
2. **Tạo đặt phòng** hoặc **check-in trực tiếp**
3. **Đặt đồ ăn** cho phòng (nếu có)
4. **Check-out** và tạo hóa đơn
5. **Xuất PDF** hóa đơn cho khách hàng

## 🔧 API Endpoints

### Quản lý phòng
- `GET /api/rooms` - Danh sách phòng
- `POST /api/rooms/checkin` - Check-in
- `POST /api/rooms/checkout` - Check-out

### Quản lý khách hàng  
- `GET /api/guests` - Danh sách khách hàng
- `POST /api/guests` - Thêm khách hàng
- `PUT /api/guests/{id}` - Cập nhật khách hàng
- `DELETE /api/guests/{id}` - Xóa khách hàng

### Đặt phòng
- `GET /api/reservations` - Danh sách đặt phòng
- `POST /api/reservations` - Tạo đặt phòng
- `POST /api/reservations/{id}/checkin` - Chuyển đổi thành check-in

### Báo cáo
- `GET /api/reports/revenue` - Báo cáo doanh thu
- `GET /api/reports/popular-dishes` - Món ăn phổ biến
- `GET /api/reports/room-occupancy` - Tỷ lệ sử dụng phòng

### PDF
- `GET /api/bills/{id}/pdf` - Xuất hóa đơn PDF

## 🔐 Phân quyền

- **Admin**: Toàn quyền, quản lý tài khoản
- **Manager**: Quản lý phòng, báo cáo, xóa dữ liệu
- **Receptionist**: Check-in/out, tạo đơn hàng, xem báo cáo cơ bản

## 📈 Tính năng nâng cao

- **Real-time pricing**: Tính giá theo booking type và duration
- **Conflict detection**: Kiểm tra xung đột lịch đặt phòng  
- **Flexible booking**: Hỗ trợ đặt theo giờ/ngày/tháng
- **Enhanced billing**: Hóa đơn chi tiết với breakdown
- **Professional PDF**: Thiết kế hóa đơn chuyên nghiệp
- **Permission system**: Kiểm soát truy cập chi tiết

## 🎯 Mục tiêu phát triển

- [ ] Real-time notifications
- [ ] Mobile app
- [ ] Payment gateway integration  
- [ ] Multi-language support
- [ ] Advanced analytics
- [ ] Backup & restore system
