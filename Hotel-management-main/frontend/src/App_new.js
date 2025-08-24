import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

console.log("Backend URL:", BACKEND_URL);
console.log("API URL:", API);

// Login Component
const Login = ({ onLogin }) => {
  const [credentials, setCredentials] = useState({ username: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      if (credentials.username === "admin" && credentials.password === "admin123") {
        const mockResponse = { id: "1", username: "admin" };
        localStorage.setItem("admin", JSON.stringify(mockResponse));
        onLogin(mockResponse);
        return;
      }
      
      const response = await axios.post(`${API}/admin/login`, credentials);
      localStorage.setItem("admin", JSON.stringify(response.data));
      onLogin(response.data);
    } catch (error) {
      if (credentials.username === "admin" && credentials.password === "admin123") {
        const mockResponse = { id: "1", username: "admin" };
        localStorage.setItem("admin", JSON.stringify(mockResponse));
        onLogin(mockResponse);
      } else {
        setError("Thông tin đăng nhập không đúng hoặc server chưa khởi động");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 to-purple-900 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-xl shadow-2xl p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">🏨 Hotel Manager</h1>
          <p className="text-gray-600">Hệ thống quản lý khách sạn với tính năng công ty</p>
        </div>
        
        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tên đăng nhập
            </label>
            <input
              type="text"
              value={credentials.username}
              onChange={(e) => setCredentials({...credentials, username: e.target.value})}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Nhập tên đăng nhập"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Mật khẩu
            </label>
            <input
              type="password"
              value={credentials.password}
              onChange={(e) => setCredentials({...credentials, password: e.target.value})}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Nhập mật khẩu"
              required
            />
          </div>
          
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}
          
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition duration-200 font-medium disabled:opacity-50"
          >
            {loading ? "Đang đăng nhập..." : "Đăng nhập"}
          </button>
        </form>
        
        <div className="mt-6 text-center text-sm text-gray-500">
          <p>Mặc định: admin / admin123</p>
        </div>
      </div>
    </div>
  );
};

// Main Dashboard Component
const Dashboard = ({ admin, onLogout }) => {
  const [rooms, setRooms] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [showCheckInModal, setShowCheckInModal] = useState(false);
  const [selectedRoom, setSelectedRoom] = useState(null);
  const [isCompanyCheckIn, setIsCompanyCheckIn] = useState(false);

  // Form states
  const [checkInForm, setCheckInForm] = useState({
    guest_name: "",
    guest_phone: "",
    guest_id: "",
    booking_type: "hourly",
    duration: 1
  });
  
  const [companyCheckInForm, setCompanyCheckInForm] = useState({
    company_name: "",
    guests: [{ name: "", phone: "", email: "", id_card: "" }],
    booking_type: "hourly",
    duration: 1
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      console.log("Fetching data from API:", API);
      const [statsRes, roomsRes] = await Promise.all([
        axios.get(`${API}/dashboard/stats`),
        axios.get(`${API}/rooms`)
      ]);
      
      console.log("Stats response:", statsRes.data);
      console.log("Rooms response:", roomsRes.data);
      
      setStats(statsRes.data);
      setRooms(roomsRes.data);
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Guest management functions
  const addGuest = () => {
    setCompanyCheckInForm({
      ...companyCheckInForm,
      guests: [...companyCheckInForm.guests, { name: "", phone: "", email: "", id_card: "" }]
    });
  };

  const removeGuest = (index) => {
    if (companyCheckInForm.guests.length > 1) {
      const newGuests = companyCheckInForm.guests.filter((_, i) => i !== index);
      setCompanyCheckInForm({
        ...companyCheckInForm,
        guests: newGuests
      });
    }
  };

  const updateGuest = (index, field, value) => {
    const newGuests = [...companyCheckInForm.guests];
    newGuests[index][field] = value;
    setCompanyCheckInForm({
      ...companyCheckInForm,
      guests: newGuests
    });
  };

  const calculateEstimatedCost = () => {
    if (!selectedRoom) return 0;
    
    const form = isCompanyCheckIn ? companyCheckInForm : checkInForm;
    const duration = parseInt(form.duration || 1);
    const pricing = selectedRoom.pricing || {};
    
    if (form.booking_type === "hourly") {
      if (duration <= 1) {
        return pricing.hourly_first || 80000;
      } else if (duration <= 2) {
        return (pricing.hourly_first || 80000) + (pricing.hourly_second || 40000);
      } else {
        return (pricing.hourly_first || 80000) + (pricing.hourly_second || 40000) + 
               ((duration - 2) * (pricing.hourly_additional || 20000));
      }
    } else if (form.booking_type === "daily") {
      return duration * (pricing.daily_rate || 500000);
    } else if (form.booking_type === "monthly") {
      return duration * (pricing.monthly_rate || 12000000);
    }
    
    return 0;
  };

  const handleCheckIn = async (e) => {
    e.preventDefault();
    console.log("Check-in attempt started");
    console.log("Selected room:", selectedRoom);
    console.log("Is company check-in:", isCompanyCheckIn);
    
    try {
      let response;
      
      if (isCompanyCheckIn) {
        // Company check-in with multiple guests
        const payload = {
          company_name: companyCheckInForm.company_name,
          guests: companyCheckInForm.guests.filter(guest => guest.name.trim()),
          booking_type: companyCheckInForm.booking_type,
          duration: parseInt(companyCheckInForm.duration)
        };
        console.log("Company payload:", payload);
        response = await axios.post(`${API}/rooms/${selectedRoom.id}/checkin-company`, payload);
      } else {
        // Individual check-in (legacy)
        const payload = {
          guest_name: checkInForm.guest_name,
          guest_phone: checkInForm.guest_phone,
          guest_id: checkInForm.guest_id,
          booking_type: checkInForm.booking_type,
          duration: parseInt(checkInForm.duration)
        };
        console.log("Individual payload:", payload);
        response = await axios.post(`${API}/rooms/${selectedRoom.id}/checkin`, payload);
      }
      
      console.log("Check-in response:", response.data);
      
      setShowCheckInModal(false);
      setIsCompanyCheckIn(false);
      setCheckInForm({ 
        guest_name: "",
        guest_phone: "",
        guest_id: "",
        booking_type: "hourly",
        duration: 1
      });
      setCompanyCheckInForm({
        company_name: "",
        guests: [{ name: "", phone: "", email: "", id_card: "" }],
        booking_type: "hourly",
        duration: 1
      });
      fetchData();
      
      // Thông báo thành công
      const formData = isCompanyCheckIn ? companyCheckInForm : checkInForm;
      const bookingTypeText = formData.booking_type === 'hourly' ? 'giờ' : 
                             formData.booking_type === 'daily' ? 'ngày' : 'tháng';
      const totalCost = response.data.total_cost || 0;
      
      if (isCompanyCheckIn) {
        alert(`Check-in công ty thành công!
Công ty: ${companyCheckInForm.company_name}
Số khách: ${companyCheckInForm.guests.filter(g => g.name.trim()).length}
Loại đặt: ${formData.duration} ${bookingTypeText}
Tổng chi phí: ${totalCost.toLocaleString()} VND`);
      } else {
        alert(`Check-in thành công!
Khách: ${checkInForm.guest_name}
Loại đặt: ${formData.duration} ${bookingTypeText}
Tổng chi phí: ${totalCost.toLocaleString()} VND`);
      }
      
    } catch (error) {
      console.error("Check-in error:", error);
      let errorMessage = "Lỗi không xác định";
      
      if (error.response?.data) {
        if (typeof error.response.data === 'string') {
          errorMessage = error.response.data;
        } else if (error.response.data.detail) {
          errorMessage = error.response.data.detail;
        } else if (error.response.data.message) {
          errorMessage = error.response.data.message;
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      alert("Lỗi khi check-in: " + errorMessage);
    }
  };

  const handleCheckOut = async (room) => {
    try {
      const response = await axios.post(`${API}/rooms/${room.id}/checkout`);
      fetchData();
      
      const bill = response.data.bill || {};
      const company = response.data.company_name || "Cá nhân";
      const guests = response.data.guests || [];
      
      alert(`Check-out thành công!
Công ty: ${company}
Số khách: ${guests.length}
Tổng chi phí: ${(bill.total_cost || 0).toLocaleString()} VND`);
    } catch (error) {
      alert("Lỗi khi check-out: " + (error.response?.data?.detail || error.message));
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">🏨 Hotel Manager</h1>
              <span className="ml-4 text-sm text-gray-500">Xin chào, {admin.username}</span>
            </div>
            <button
              onClick={onLogout}
              className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition duration-200"
            >
              Đăng xuất
            </button>
          </div>
        </div>
      </header>

      {/* Stats Cards */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <span className="text-3xl">🏠</span>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Tổng phòng</dt>
                  <dd className="text-lg font-medium text-gray-900">{stats.total_rooms || 0}</dd>
                </dl>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <span className="text-3xl">🔴</span>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Đang sử dụng</dt>
                  <dd className="text-lg font-medium text-gray-900">{stats.occupied_rooms || 0}</dd>
                </dl>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <span className="text-3xl">🟢</span>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Phòng trống</dt>
                  <dd className="text-lg font-medium text-gray-900">{stats.empty_rooms || 0}</dd>
                </dl>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <span className="text-3xl">📊</span>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Tỷ lệ lấp đầy</dt>
                  <dd className="text-lg font-medium text-gray-900">{stats.occupancy_rate || 0}%</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Rooms Grid */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">🏠 Danh sách phòng</h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {rooms.map((room) => (
                <div key={room.id} className={`border rounded-lg p-4 ${
                  room.status === 'empty' ? 'border-green-200 bg-green-50' : 
                  room.status === 'occupied' ? 'border-red-200 bg-red-50' : 
                  'border-gray-200 bg-gray-50'
                }`}>
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-semibold text-lg">Phòng {room.number}</h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      room.status === 'empty' ? 'bg-green-100 text-green-800' :
                      room.status === 'occupied' ? 'bg-red-100 text-red-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {room.status === 'empty' ? 'Trống' : 
                       room.status === 'occupied' ? 'Đang sử dụng' : 'Bảo trì'}
                    </span>
                  </div>
                  
                  <div className="space-y-1 text-sm text-gray-600">
                    <p>Loại: {room.type === 'single' ? 'Đơn' : 'Đôi'}</p>
                    
                    {room.status === 'occupied' && (
                      <>
                        {room.company_name && (
                          <p className="font-medium text-blue-600">🏢 {room.company_name}</p>
                        )}
                        {room.guests && room.guests.length > 0 ? (
                          <div>
                            <p className="font-medium">👥 Khách ({room.guests.length}):</p>
                            {room.guests.slice(0, 2).map((guest, idx) => (
                              <p key={idx} className="ml-2 text-xs">• {guest.name}</p>
                            ))}
                            {room.guests.length > 2 && (
                              <p className="ml-2 text-xs text-gray-500">... và {room.guests.length - 2} khách khác</p>
                            )}
                          </div>
                        ) : room.guest_name && (
                          <p>👤 {room.guest_name}</p>
                        )}
                        
                        {room.total_cost && (
                          <p className="font-medium text-green-600">
                            💰 {room.total_cost.toLocaleString()} VND
                          </p>
                        )}
                      </>
                    )}
                  </div>
                  
                  <div className="mt-3 space-y-2">
                    {room.status === 'empty' ? (
                      <button
                        onClick={() => {
                          setSelectedRoom(room);
                          setShowCheckInModal(true);
                        }}
                        className="w-full bg-blue-600 text-white py-2 px-3 rounded-lg hover:bg-blue-700 transition duration-200 text-sm font-medium"
                      >
                        🏢 Check-in
                      </button>
                    ) : room.status === 'occupied' && (
                      <button
                        onClick={() => handleCheckOut(room)}
                        className="w-full bg-red-600 text-white py-2 px-3 rounded-lg hover:bg-red-700 transition duration-200 text-sm font-medium"
                      >
                        📤 Check-out
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Check-in Modal */}
      {showCheckInModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900">
                Check-in Phòng {selectedRoom?.number}
              </h3>
              <button
                onClick={() => setShowCheckInModal(false)}
                className="text-gray-500 hover:text-gray-700 text-2xl"
              >
                ×
              </button>
            </div>
            
            {/* Check-in Type Selection */}
            <div className="mb-6">
              <div className="flex space-x-4">
                <button
                  type="button"
                  onClick={() => setIsCompanyCheckIn(false)}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    !isCompanyCheckIn 
                      ? 'bg-blue-500 text-white' 
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  👤 Cá nhân
                </button>
                <button
                  type="button"
                  onClick={() => setIsCompanyCheckIn(true)}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    isCompanyCheckIn 
                      ? 'bg-blue-500 text-white' 
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  🏢 Công ty
                </button>
              </div>
            </div>
            
            <form onSubmit={handleCheckIn} className="space-y-4">
              {!isCompanyCheckIn ? (
                // Individual Check-in Form
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Tên khách hàng *
                    </label>
                    <input
                      type="text"
                      value={checkInForm.guest_name}
                      onChange={(e) => setCheckInForm({ ...checkInForm, guest_name: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      placeholder="Nhập tên khách hàng"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Số điện thoại
                    </label>
                    <input
                      type="tel"
                      value={checkInForm.guest_phone}
                      onChange={(e) => setCheckInForm({ ...checkInForm, guest_phone: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      placeholder="Nhập số điện thoại"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      CMND/CCCD
                    </label>
                    <input
                      type="text"
                      value={checkInForm.guest_id}
                      onChange={(e) => setCheckInForm({ ...checkInForm, guest_id: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      placeholder="Nhập số CMND/CCCD"
                    />
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Loại đặt phòng
                      </label>
                      <select
                        value={checkInForm.booking_type}
                        onChange={(e) => setCheckInForm({ ...checkInForm, booking_type: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="hourly">Theo giờ</option>
                        <option value="daily">Theo ngày</option>
                        <option value="monthly">Theo tháng</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Thời gian ({checkInForm.booking_type === 'hourly' ? 'giờ' : checkInForm.booking_type === 'daily' ? 'ngày' : 'tháng'})
                      </label>
                      <input
                        type="number"
                        min="1"
                        value={checkInForm.duration}
                        onChange={(e) => setCheckInForm({ ...checkInForm, duration: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        placeholder="Số lượng"
                        required
                      />
                    </div>
                  </div>
                </>
              ) : (
                // Company Check-in Form
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Tên công ty *
                    </label>
                    <input
                      type="text"
                      value={companyCheckInForm.company_name}
                      onChange={(e) => setCompanyCheckInForm({ ...companyCheckInForm, company_name: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      placeholder="Nhập tên công ty"
                      required
                    />
                  </div>
                  
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <label className="block text-sm font-medium text-gray-700">
                        Danh sách khách (tối thiểu 1 người) *
                      </label>
                      <button
                        type="button"
                        onClick={addGuest}
                        className="bg-green-500 text-white px-3 py-1 rounded-lg hover:bg-green-600 text-sm"
                      >
                        + Thêm khách
                      </button>
                    </div>
                    
                    <div className="space-y-3 max-h-60 overflow-y-auto">
                      {companyCheckInForm.guests.map((guest, index) => (
                        <div key={index} className="border border-gray-200 rounded-lg p-3 bg-gray-50">
                          <div className="flex justify-between items-center mb-2">
                            <span className="text-sm font-medium text-gray-700">Khách #{index + 1}</span>
                            {companyCheckInForm.guests.length > 1 && (
                              <button
                                type="button"
                                onClick={() => removeGuest(index)}
                                className="text-red-500 hover:text-red-700 text-sm"
                              >
                                × Xóa
                              </button>
                            )}
                          </div>
                          
                          <div className="grid grid-cols-2 gap-2">
                            <input
                              type="text"
                              value={guest.name}
                              onChange={(e) => updateGuest(index, 'name', e.target.value)}
                              className="px-2 py-1 border border-gray-300 rounded text-sm focus:ring-1 focus:ring-blue-500"
                              placeholder="Tên *"
                              required
                            />
                            <input
                              type="tel"
                              value={guest.phone}
                              onChange={(e) => updateGuest(index, 'phone', e.target.value)}
                              className="px-2 py-1 border border-gray-300 rounded text-sm focus:ring-1 focus:ring-blue-500"
                              placeholder="Số điện thoại"
                            />
                            <input
                              type="email"
                              value={guest.email}
                              onChange={(e) => updateGuest(index, 'email', e.target.value)}
                              className="px-2 py-1 border border-gray-300 rounded text-sm focus:ring-1 focus:ring-blue-500"
                              placeholder="Email"
                            />
                            <input
                              type="text"
                              value={guest.id_card}
                              onChange={(e) => updateGuest(index, 'id_card', e.target.value)}
                              className="px-2 py-1 border border-gray-300 rounded text-sm focus:ring-1 focus:ring-blue-500"
                              placeholder="CMND/CCCD"
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Loại đặt phòng
                      </label>
                      <select
                        value={companyCheckInForm.booking_type}
                        onChange={(e) => setCompanyCheckInForm({ ...companyCheckInForm, booking_type: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="hourly">Theo giờ</option>
                        <option value="daily">Theo ngày</option>
                        <option value="monthly">Theo tháng</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Thời gian ({companyCheckInForm.booking_type === 'hourly' ? 'giờ' : companyCheckInForm.booking_type === 'daily' ? 'ngày' : 'tháng'})
                      </label>
                      <input
                        type="number"
                        min="1"
                        value={companyCheckInForm.duration}
                        onChange={(e) => setCompanyCheckInForm({ ...companyCheckInForm, duration: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        placeholder="Số lượng"
                        required
                      />
                    </div>
                  </div>
                </>
              )}
              
              {/* Cost Estimation */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <div className="text-sm text-blue-800">
                  <strong>Dự kiến chi phí:</strong> {calculateEstimatedCost().toLocaleString()} VND
                </div>
              </div>
              
              <div className="flex space-x-3 pt-4">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition duration-200 font-medium"
                >
                  {isCompanyCheckIn ? '🏢 Check-in Công ty' : '👤 Check-in Cá nhân'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowCheckInModal(false)}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition duration-200"
                >
                  Hủy
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

// Main App Component
function App() {
  const [admin, setAdmin] = useState(null);

  useEffect(() => {
    const savedAdmin = localStorage.getItem("admin");
    if (savedAdmin) {
      setAdmin(JSON.parse(savedAdmin));
    }
  }, []);

  const handleLogin = (adminData) => {
    setAdmin(adminData);
  };

  const handleLogout = () => {
    localStorage.removeItem("admin");
    setAdmin(null);
  };

  if (!admin) {
    return <Login onLogin={handleLogin} />;
  }

  return <Dashboard admin={admin} onLogout={handleLogout} />;
}

export default App;
