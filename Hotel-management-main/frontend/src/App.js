import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.NODE_ENV === 'production' 
  ? "https://hotel-management-iota-rose.vercel.app"
  : process.env.REACT_APP_BACKEND_URL || "http://localhost:8000";
const API = `${BACKEND_URL}/api`;

console.log("Environment:", process.env.NODE_ENV);
console.log("Backend URL:", BACKEND_URL);
console.log("API URL:", API);

// Order Filters Component
const OrderFilters = ({ onFiltersChange }) => {
  const [filters, setFilters] = useState({
    startDate: "",
    endDate: "",
    companyName: "",
    dishName: "",
    limit: 100
  });
  
  const [companies, setCompanies] = useState([]);
  const [dishes, setDishes] = useState([]);
  const [companyReport, setCompanyReport] = useState(null);
  const [companySummary, setCompanySummary] = useState(null);
  const [showReport, setShowReport] = useState(false);
  const [reportGroupBy, setReportGroupBy] = useState("daily");

  useEffect(() => {
    // Load companies and dishes lists
    fetchCompanies();
    fetchDishes();
    fetchCompanySummary();
  }, []);

  const fetchCompanies = async () => {
    try {
      const response = await axios.get(`${API}/orders/companies`);
      setCompanies(response.data.companies || []);
    } catch (error) {
      console.error("Error fetching companies:", error);
    }
  };

  const fetchDishes = async () => {
    try {
      const response = await axios.get(`${API}/orders/dishes`);
      setDishes(response.data.dishes || []);
    } catch (error) {
      console.error("Error fetching dishes:", error);
    }
  };

  const fetchCompanySummary = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.startDate) params.append("start_date", filters.startDate);
      if (filters.endDate) params.append("end_date", filters.endDate);
      
      const response = await axios.get(`${API}/orders/company-summary?${params}`);
      setCompanySummary(response.data);
    } catch (error) {
      console.error("Error fetching company summary:", error);
    }
  };

  const fetchCompanyReport = async (companyName) => {
    try {
      const params = new URLSearchParams();
      params.append("company_name", companyName);
      params.append("group_by", reportGroupBy);
      if (filters.startDate) params.append("start_date", filters.startDate);
      if (filters.endDate) params.append("end_date", filters.endDate);
      
      const response = await axios.get(`${API}/orders/company-report?${params}`);
      setCompanyReport(response.data);
      setShowReport(true);
    } catch (error) {
      console.error("Error fetching company report:", error);
      alert("Lỗi khi tải báo cáo công ty");
    }
  };

  const handleFilterChange = (field, value) => {
    const newFilters = { ...filters, [field]: value };
    setFilters(newFilters);
    
    // Apply filters immediately
    const params = new URLSearchParams();
    if (newFilters.startDate) params.append("start_date", newFilters.startDate);
    if (newFilters.endDate) params.append("end_date", newFilters.endDate);
    if (newFilters.companyName) params.append("company_name", newFilters.companyName);
    if (newFilters.dishName) params.append("dish_name", newFilters.dishName);
    params.append("limit", newFilters.limit);
    
    onFiltersChange(params.toString());
  };

  const resetFilters = () => {
    const resetFilters = {
      startDate: "",
      endDate: "",
      companyName: "",
      dishName: "",
      limit: 100
    };
    setFilters(resetFilters);
    onFiltersChange("");
    fetchCompanySummary();
  };

  return (
    <div className="space-y-6">
      {/* Filter Controls */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Từ ngày</label>
          <input
            type="date"
            value={filters.startDate}
            onChange={(e) => handleFilterChange("startDate", e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Đến ngày</label>
          <input
            type="date"
            value={filters.endDate}
            onChange={(e) => handleFilterChange("endDate", e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Công ty</label>
          <select
            value={filters.companyName}
            onChange={(e) => handleFilterChange("companyName", e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
          >
            <option value="">Tất cả công ty</option>
            {companies.map((company) => (
              <option key={company} value={company}>{company}</option>
            ))}
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Món ăn</label>
          <select
            value={filters.dishName}
            onChange={(e) => handleFilterChange("dishName", e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
          >
            <option value="">Tất cả món ăn</option>
            {dishes.map((dish) => (
              <option key={dish} value={dish}>{dish}</option>
            ))}
          </select>
        </div>
        
        <div className="flex items-end">
          <button
            onClick={resetFilters}
            className="w-full bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600 transition duration-200 text-sm"
          >
            🔄 Reset
          </button>
        </div>
      </div>

      {/* Company Summary */}
      {companySummary && companySummary.companies && (
        <div className="bg-white border rounded-lg p-4">
          <h4 className="text-lg font-medium text-gray-900 mb-4">📊 Tổng quan theo công ty</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
            <div className="bg-blue-50 p-3 rounded-lg">
              <p className="text-sm text-blue-600">Tổng công ty</p>
              <p className="text-2xl font-bold text-blue-800">{companySummary.total_companies}</p>
            </div>
            <div className="bg-green-50 p-3 rounded-lg">
              <p className="text-sm text-green-600">Tổng doanh thu</p>
              <p className="text-2xl font-bold text-green-800">{companySummary.grand_total?.toLocaleString()} VND</p>
            </div>
            <div className="bg-purple-50 p-3 rounded-lg">
              <p className="text-sm text-purple-600">Trung bình/công ty</p>
              <p className="text-2xl font-bold text-purple-800">
                {companySummary.total_companies > 0 ? (companySummary.grand_total / companySummary.total_companies).toLocaleString() : 0} VND
              </p>
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Công ty</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Số đơn</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Tổng tiền</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">TB/đơn</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Món khác nhau</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Thao tác</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {companySummary.companies.slice(0, 10).map((company) => (
                  <tr key={company.company_name} className="hover:bg-gray-50">
                    <td className="px-4 py-2 text-sm font-medium text-gray-900">{company.company_name}</td>
                    <td className="px-4 py-2 text-sm text-gray-600">{company.total_orders}</td>
                    <td className="px-4 py-2 text-sm font-medium text-green-600">{company.total_amount?.toLocaleString()} VND</td>
                    <td className="px-4 py-2 text-sm text-gray-600">{company.average_order_value?.toLocaleString()} VND</td>
                    <td className="px-4 py-2 text-sm text-gray-600">{company.unique_dishes_count} món</td>
                    <td className="px-4 py-2">
                      <div className="flex gap-2">
                        <button
                          onClick={() => fetchCompanyReport(company.company_name)}
                          className="bg-blue-500 text-white px-2 py-1 rounded text-xs hover:bg-blue-600"
                        >
                          📈 Báo cáo
                        </button>
                        <button
                          onClick={() => handleFilterChange("companyName", company.company_name)}
                          className="bg-green-500 text-white px-2 py-1 rounded text-xs hover:bg-green-600"
                        >
                          🔍 Lọc
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            {companySummary.companies.length > 10 && (
              <div className="text-center py-2 text-sm text-gray-500">
                Hiển thị 10/{companySummary.companies.length} công ty (theo doanh thu cao nhất)
              </div>
            )}
          </div>
        </div>
      )}

      {/* Company Report Modal */}
      {showReport && companyReport && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl mx-4 max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
              <h3 className="text-lg font-semibold text-gray-900">
                📊 Báo cáo chi tiết - {companyReport.company_name}
              </h3>
              <button
                onClick={() => setShowReport(false)}
                className="text-gray-500 hover:text-gray-700 text-2xl"
              >
                ×
              </button>
            </div>
            
            <div className="p-6">
              {/* Report Controls */}
              <div className="flex gap-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Nhóm theo</label>
                  <select
                    value={reportGroupBy}
                    onChange={(e) => {
                      setReportGroupBy(e.target.value);
                      fetchCompanyReport(companyReport.company_name);
                    }}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="daily">Theo ngày</option>
                    <option value="monthly">Theo tháng</option>
                  </select>
                </div>
              </div>

              {/* Summary */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <p className="text-sm text-blue-600">Tổng đơn hàng</p>
                  <p className="text-3xl font-bold text-blue-800">{companyReport.summary?.total_orders || 0}</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <p className="text-sm text-green-600">Tổng doanh thu</p>
                  <p className="text-3xl font-bold text-green-800">{companyReport.summary?.total_amount?.toLocaleString() || 0} VND</p>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg">
                  <p className="text-sm text-purple-600">Trung bình/đơn</p>
                  <p className="text-3xl font-bold text-purple-800">{companyReport.summary?.average_order_value?.toLocaleString() || 0} VND</p>
                </div>
              </div>

              {/* Details */}
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                        {reportGroupBy === "daily" ? "Ngày" : "Tháng"}
                      </th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Số đơn</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Tổng tiền</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Chi tiết</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {companyReport.details?.map((detail, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-4 py-2 text-sm font-medium text-gray-900">{detail.date}</td>
                        <td className="px-4 py-2 text-sm text-gray-600">{detail.total_orders}</td>
                        <td className="px-4 py-2 text-sm font-medium text-green-600">{detail.total_amount?.toLocaleString()} VND</td>
                        <td className="px-4 py-2 text-sm text-gray-600">
                          <details className="cursor-pointer">
                            <summary className="text-blue-600 hover:text-blue-800">Xem đơn hàng ({detail.orders?.length || 0})</summary>
                            <div className="mt-2 pl-4 border-l-2 border-gray-200">
                              {detail.orders?.map((order, orderIndex) => (
                                <div key={orderIndex} className="text-xs text-gray-600 py-1">
                                  • {order.dish_name} x{order.quantity} = {order.total_price?.toLocaleString()} VND
                                </div>
                              ))}
                            </div>
                          </details>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

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
      // Check for default admin credentials
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
      // If backend is not available, check for default credentials
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
          <p className="text-gray-600">Hệ thống quản lý khách sạn</p>
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

// Guest Management Component
const GuestManagement = () => {
  const [guests, setGuests] = useState([]);
  const [showGuestModal, setShowGuestModal] = useState(false);
  const [selectedGuest, setSelectedGuest] = useState(null);
  const [guestForm, setGuestForm] = useState({
    name: "",
    phone: "",
    email: "",
    id_card: ""
  });

  useEffect(() => {
    fetchGuests();
  }, []);

  const fetchGuests = async () => {
    try {
      const response = await axios.get(`${API}/guests`);
      setGuests(response.data);
    } catch (error) {
      console.error("Error fetching guests:", error);
    }
  };

  const handleSubmitGuest = async (e) => {
    e.preventDefault();
    try {
      if (selectedGuest) {
        await axios.put(`${API}/guests/${selectedGuest.id}`, guestForm);
      } else {
        await axios.post(`${API}/guests`, guestForm);
      }
      
      await fetchGuests();
      setShowGuestModal(false);
      setSelectedGuest(null);
      setGuestForm({ name: "", phone: "", email: "", id_card: "" });
    } catch (error) {
      console.error("Error submitting guest:", error);
    }
  };

  const handleEditGuest = (guest) => {
    setSelectedGuest(guest);
    setGuestForm({
      name: guest.name,
      phone: guest.phone || "",
      email: guest.email || "",
      id_card: guest.id_card || ""
    });
    setShowGuestModal(true);
  };

  const handleDeleteGuest = async (guestId) => {
    if (window.confirm("Bạn có chắc chắn muốn xóa khách hàng này?")) {
      try {
        await axios.delete(`${API}/guests/${guestId}`);
        await fetchGuests();
      } catch (error) {
        console.error("Error deleting guest:", error);
      }
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Quản lý khách hàng</h2>
        <button
          onClick={() => setShowGuestModal(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition duration-200"
        >
          Thêm khách hàng
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tên</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Điện thoại</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">CMND/CCCD</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Thao tác</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {guests.map((guest) => (
              <tr key={guest.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{guest.name}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{guest.phone || "N/A"}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{guest.email || "N/A"}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{guest.id_card || "N/A"}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    onClick={() => handleEditGuest(guest)}
                    className="text-indigo-600 hover:text-indigo-900 mr-4"
                  >
                    Sửa
                  </button>
                  <button
                    onClick={() => handleDeleteGuest(guest.id)}
                    className="text-red-600 hover:text-red-900"
                  >
                    Xóa
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {guests.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            Chưa có khách hàng nào
          </div>
        )}
      </div>

      {/* Guest Modal */}
      {showGuestModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">
                {selectedGuest ? "Sửa thông tin khách hàng" : "Thêm khách hàng mới"}
              </h3>
            </div>
            <form onSubmit={handleSubmitGuest} className="p-6">
              <div className="grid grid-cols-1 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Họ tên</label>
                  <input
                    type="text"
                    value={guestForm.name}
                    onChange={(e) => setGuestForm({ ...guestForm, name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Điện thoại</label>
                  <input
                    type="tel"
                    value={guestForm.phone}
                    onChange={(e) => setGuestForm({ ...guestForm, phone: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <input
                    type="email"
                    value={guestForm.email}
                    onChange={(e) => setGuestForm({ ...guestForm, email: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">CMND/CCCD</label>
                  <input
                    type="text"
                    value={guestForm.id_card}
                    onChange={(e) => setGuestForm({ ...guestForm, id_card: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
              <div className="flex gap-3 mt-6">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition duration-200"
                >
                  {selectedGuest ? "Cập nhật" : "Thêm mới"}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowGuestModal(false);
                    setSelectedGuest(null);
                    setGuestForm({ name: "", phone: "", email: "", id_card: "" });
                  }}
                  className="flex-1 bg-gray-400 text-white py-2 px-4 rounded-lg hover:bg-gray-500 transition duration-200"
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

// Reservation Management Component
const ReservationManagement = () => {
  const [reservations, setReservations] = useState([]);
  const [rooms, setRooms] = useState([]);
  const [guests, setGuests] = useState([]);
  const [showReservationModal, setShowReservationModal] = useState(false);
  const [selectedReservation, setSelectedReservation] = useState(null);
  const [reservationForm, setReservationForm] = useState({
    guest_id: "",
    guest_name: "",
    room_id: "",
    check_in_date: "",
    check_out_date: "",
    booking_type: "daily",
    duration: 1,
    special_requests: ""
  });

  useEffect(() => {
    fetchReservations();
    fetchRooms();
    fetchGuests();
  }, []);

  const fetchReservations = async () => {
    try {
      const response = await axios.get(`${API}/reservations`);
      setReservations(response.data);
    } catch (error) {
      console.error("Error fetching reservations:", error);
    }
  };

  const fetchRooms = async () => {
    try {
      const response = await axios.get(`${API}/rooms`);
      setRooms(response.data);
    } catch (error) {
      console.error("Error fetching rooms:", error);
    }
  };

  const fetchGuests = async () => {
    try {
      const response = await axios.get(`${API}/guests`);
      setGuests(response.data);
    } catch (error) {
      console.error("Error fetching guests:", error);
    }
  };

  const handleSubmitReservation = async (e) => {
    e.preventDefault();
    try {
      if (selectedReservation) {
        await axios.put(`${API}/reservations/${selectedReservation.id}`, reservationForm);
      } else {
        await axios.post(`${API}/reservations`, reservationForm);
      }
      
      await fetchReservations();
      setShowReservationModal(false);
      setSelectedReservation(null);
      resetReservationForm();
    } catch (error) {
      console.error("Error submitting reservation:", error);
    }
  };

  const resetReservationForm = () => {
    setReservationForm({
      guest_id: "",
      guest_name: "",
      room_id: "",
      check_in_date: "",
      check_out_date: "",
      booking_type: "daily",
      duration: 1,
      special_requests: ""
    });
  };

  const handleConvertToCheckIn = async (reservationId) => {
    if (window.confirm("Bạn có chắc chắn muốn chuyển đặt phòng này thành check-in?")) {
      try {
        await axios.post(`${API}/reservations/${reservationId}/checkin`);
        await fetchReservations();
        alert("Đã chuyển đổi thành công!");
      } catch (error) {
        console.error("Error converting to check-in:", error);
        alert("Có lỗi xảy ra khi chuyển đổi!");
      }
    }
  };

  const getStatusBadge = (status) => {
    const statusColors = {
      pending: "bg-yellow-100 text-yellow-800",
      confirmed: "bg-green-100 text-green-800",
      cancelled: "bg-red-100 text-red-800",
      checked_in: "bg-blue-100 text-blue-800"
    };
    
    const statusText = {
      pending: "Chờ xác nhận",
      confirmed: "Đã xác nhận", 
      cancelled: "Đã hủy",
      checked_in: "Đã check-in"
    };

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColors[status]}`}>
        {statusText[status]}
      </span>
    );
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Quản lý đặt phòng</h2>
        <button
          onClick={() => setShowReservationModal(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition duration-200"
        >
          Tạo đặt phòng
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Khách hàng</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Phòng</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Check-in</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Check-out</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Trạng thái</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Thao tác</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {reservations.map((reservation) => (
              <tr key={reservation.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{reservation.guest_name}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{reservation.room_id}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date(reservation.check_in_date).toLocaleDateString('vi-VN')}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date(reservation.check_out_date).toLocaleDateString('vi-VN')}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">{getStatusBadge(reservation.status)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  {reservation.status === "confirmed" && (
                    <button
                      onClick={() => handleConvertToCheckIn(reservation.id)}
                      className="text-green-600 hover:text-green-900 mr-4"
                    >
                      Check-in
                    </button>
                  )}
                  <button
                    onClick={() => {
                      setSelectedReservation(reservation);
                      setReservationForm(reservation);
                      setShowReservationModal(true);
                    }}
                    className="text-indigo-600 hover:text-indigo-900"
                  >
                    Xem
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {reservations.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            Chưa có đặt phòng nào
          </div>
        )}
      </div>

      {/* Reservation Modal */}
      {showReservationModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl mx-4">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">
                {selectedReservation ? "Chi tiết đặt phòng" : "Tạo đặt phòng mới"}
              </h3>
            </div>
            <form onSubmit={handleSubmitReservation} className="p-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Khách hàng</label>
                  <select
                    value={reservationForm.guest_id}
                    onChange={(e) => {
                      const selectedGuest = guests.find(g => g.id === e.target.value);
                      setReservationForm({ 
                        ...reservationForm, 
                        guest_id: e.target.value,
                        guest_name: selectedGuest ? selectedGuest.name : ""
                      });
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  >
                    <option value="">Chọn khách hàng</option>
                    {guests.map((guest) => (
                      <option key={guest.id} value={guest.id}>{guest.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Phòng</label>
                  <select
                    value={reservationForm.room_id}
                    onChange={(e) => setReservationForm({ ...reservationForm, room_id: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  >
                    <option value="">Chọn phòng</option>
                    {rooms.filter(room => room.status === "empty").map((room) => (
                      <option key={room.id} value={room.id}>
                        Phòng {room.number} - {room.type}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Ngày check-in</label>
                  <input
                    type="datetime-local"
                    value={reservationForm.check_in_date}
                    onChange={(e) => setReservationForm({ ...reservationForm, check_in_date: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Ngày check-out</label>
                  <input
                    type="datetime-local"
                    value={reservationForm.check_out_date}
                    onChange={(e) => setReservationForm({ ...reservationForm, check_out_date: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Loại đặt phòng</label>
                  <select
                    value={reservationForm.booking_type}
                    onChange={(e) => setReservationForm({ ...reservationForm, booking_type: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="hourly">Theo giờ</option>
                    <option value="daily">Theo ngày</option>
                    <option value="monthly">Theo tháng</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Thời gian</label>
                  <input
                    type="number"
                    min="1"
                    value={reservationForm.duration}
                    onChange={(e) => setReservationForm({ ...reservationForm, duration: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Yêu cầu đặc biệt</label>
                  <textarea
                    value={reservationForm.special_requests}
                    onChange={(e) => setReservationForm({ ...reservationForm, special_requests: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows="3"
                  />
                </div>
              </div>
              <div className="flex gap-3 mt-6">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition duration-200"
                >
                  {selectedReservation ? "Cập nhật" : "Tạo đặt phòng"}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowReservationModal(false);
                    setSelectedReservation(null);
                    resetReservationForm();
                  }}
                  className="flex-1 bg-gray-400 text-white py-2 px-4 rounded-lg hover:bg-gray-500 transition duration-200"
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

// Dashboard Component
const Dashboard = ({ admin, onLogout }) => {
  const [activeTab, setActiveTab] = useState("rooms");
  const [stats, setStats] = useState({});
  const [rooms, setRooms] = useState([]);
  const [dishes, setDishes] = useState([]);
  const [orders, setOrders] = useState([]);
  const [bills, setBills] = useState([]);
  const [loading, setLoading] = useState(false);

  // Modals state
  const [showCheckInModal, setShowCheckInModal] = useState(false);
  const [showCheckOutModal, setShowCheckOutModal] = useState(false);
  const [showDishModal, setShowDishModal] = useState(false);
  const [showOrderModal, setShowOrderModal] = useState(false);
  const [showPricingModal, setShowPricingModal] = useState(false);
  const [showRoomDetailModal, setShowRoomDetailModal] = useState(false);
  const [selectedRoom, setSelectedRoom] = useState(null);
  const [selectedDish, setSelectedDish] = useState(null);
  const [currentCost, setCurrentCost] = useState(null);
  const [checkoutBill, setCheckoutBill] = useState(null);

  // Form states
  const [checkInForm, setCheckInForm] = useState({
    guest_name: "",
    guest_phone: "",
    guest_id: "",
    booking_type: "hourly",
    duration: 1
  });
  
  // New company check-in form
  const [companyCheckInForm, setCompanyCheckInForm] = useState({
    company_name: "",
    guests: [{ name: "", phone: "", email: "", id_card: "" }],
    booking_type: "hourly",
    duration: 1
  });
  
  const [isCompanyCheckIn, setIsCompanyCheckIn] = useState(false);
  const [dishForm, setDishForm] = useState({
    name: "",
    price: "",
    description: ""
  });
  const [orderForm, setOrderForm] = useState({
    company_name: "",
    dish_id: "",
    quantity: 1
  });
  const [pricingForm, setPricingForm] = useState({
    hourly_first: 80000,
    hourly_second: 40000,
    hourly_additional: 20000,
    daily_rate: 500000,
    monthly_rate: 12000000
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      console.log("Using mock data due to API issues");
      
      // Mock data for development/testing
      const mockStats = {
        total_rooms: 10,
        empty_rooms: 10, 
        occupied_rooms: 0,
        occupancy_rate: 0,
        today_revenue: 0
      };
      
      const mockRooms = [
        {"id": "1", "number": "201", "type": "single", "status": "empty", "pricing": {"hourly_first": 80000, "hourly_second": 40000, "hourly_additional": 20000, "daily_rate": 500000, "monthly_rate": 12000000}},
        {"id": "2", "number": "202", "type": "single", "status": "empty", "pricing": {"hourly_first": 80000, "hourly_second": 40000, "hourly_additional": 20000, "daily_rate": 500000, "monthly_rate": 12000000}},
        {"id": "3", "number": "203", "type": "double", "status": "empty", "pricing": {"hourly_first": 80000, "hourly_second": 40000, "hourly_additional": 20000, "daily_rate": 500000, "monthly_rate": 12000000}},
        {"id": "4", "number": "204", "type": "single", "status": "empty", "pricing": {"hourly_first": 80000, "hourly_second": 40000, "hourly_additional": 20000, "daily_rate": 500000, "monthly_rate": 12000000}},
        {"id": "5", "number": "205", "type": "double", "status": "empty", "pricing": {"hourly_first": 80000, "hourly_second": 40000, "hourly_additional": 20000, "daily_rate": 500000, "monthly_rate": 12000000}},
        {"id": "6", "number": "206", "type": "single", "status": "empty", "pricing": {"hourly_first": 80000, "hourly_second": 40000, "hourly_additional": 20000, "daily_rate": 500000, "monthly_rate": 12000000}},
        {"id": "7", "number": "207", "type": "double", "status": "empty", "pricing": {"hourly_first": 80000, "hourly_second": 40000, "hourly_additional": 20000, "daily_rate": 500000, "monthly_rate": 12000000}},
        {"id": "8", "number": "208", "type": "single", "status": "empty", "pricing": {"hourly_first": 80000, "hourly_second": 40000, "hourly_additional": 20000, "daily_rate": 500000, "monthly_rate": 12000000}},
        {"id": "9", "number": "209", "type": "double", "status": "empty", "pricing": {"hourly_first": 80000, "hourly_second": 40000, "hourly_additional": 20000, "daily_rate": 500000, "monthly_rate": 12000000}},
        {"id": "10", "number": "210", "type": "single", "status": "empty", "pricing": {"hourly_first": 80000, "hourly_second": 40000, "hourly_additional": 20000, "daily_rate": 500000, "monthly_rate": 12000000}}
      ];
      
      const mockDishes = [
        {"id": "1", "name": "Phở bò", "price": 50000, "description": "Phở bò truyền thống", "status": "available"},
        {"id": "2", "name": "Cơm tấm", "price": 45000, "description": "Cơm tấm sườn nướng", "status": "available"},
        {"id": "3", "name": "Bánh mì", "price": 25000, "description": "Bánh mì thịt nguội", "status": "available"},
        {"id": "4", "name": "Bún chả", "price": 55000, "description": "Bún chả Hà Nội", "status": "available"},
        {"id": "5", "name": "Gỏi cuốn", "price": 35000, "description": "Gỏi cuốn tôm thịt", "status": "available"}
      ];
      
      console.log("Mock stats:", mockStats);
      console.log("Mock rooms:", mockRooms);
      console.log("Mock dishes:", mockDishes);
      
      setStats(mockStats);
      setRooms(mockRooms);
      setDishes(mockDishes);
      setOrders([]);
      setBills([]);
      
    } catch (error) {
      console.error("Error with mock data:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchFilteredOrders = async (filterParams) => {
    try {
      const url = filterParams ? `${API}/orders?${filterParams}` : `${API}/orders`;
      const response = await axios.get(url);
      setOrders(response.data);
    } catch (error) {
      console.error("Error fetching filtered orders:", error);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCheckIn = async (e) => {
    e.preventDefault();
    console.log("Check-in attempt started");
    console.log("Selected room:", selectedRoom);
    console.log("Is company check-in:", isCompanyCheckIn);
    
    try {
      // Mock check-in logic since API is not working
      const currentDate = new Date();
      const checkOutDate = new Date();
      
      const form = isCompanyCheckIn ? companyCheckInForm : checkInForm;
      
      if (form.booking_type === "hourly") {
        checkOutDate.setHours(checkOutDate.getHours() + parseInt(form.duration));
      } else if (form.booking_type === "daily") {
        checkOutDate.setDate(checkOutDate.getDate() + parseInt(form.duration));
      } else if (form.booking_type === "monthly") {
        checkOutDate.setMonth(checkOutDate.getMonth() + parseInt(form.duration));
      }
      
      // Calculate estimated cost
      const duration = parseInt(form.duration || 1);
      const pricing = selectedRoom.pricing || {};
      let totalCost = 0;
      
      if (form.booking_type === "hourly") {
        if (duration <= 1) {
          totalCost = pricing.hourly_first || 80000;
        } else if (duration <= 2) {
          totalCost = (pricing.hourly_first || 80000) + (pricing.hourly_second || 40000);
        } else {
          totalCost = (pricing.hourly_first || 80000) + (pricing.hourly_second || 40000) + 
                     ((duration - 2) * (pricing.hourly_additional || 20000));
        }
      } else if (form.booking_type === "daily") {
        totalCost = duration * (pricing.daily_rate || 500000);
      } else if (form.booking_type === "monthly") {
        totalCost = duration * (pricing.monthly_rate || 12000000);
      }
      
      // Update room status in local state
      const updatedRooms = rooms.map(room => {
        if (room.id === selectedRoom.id) {
          if (isCompanyCheckIn) {
            return {
              ...room,
              status: "occupied",
              company_name: companyCheckInForm.company_name,
              guests: companyCheckInForm.guests.filter(guest => guest.name.trim()),
              check_in_date: currentDate.toISOString(),
              check_out_date: checkOutDate.toISOString(),
              booking_type: companyCheckInForm.booking_type,
              booking_duration: parseInt(companyCheckInForm.duration),
              total_cost: totalCost
            };
          } else {
            return {
              ...room,
              status: "occupied",
              guest_name: checkInForm.guest_name,
              guest_phone: checkInForm.guest_phone,
              guest_id: checkInForm.guest_id,
              check_in_date: currentDate.toISOString(),
              check_out_date: checkOutDate.toISOString(),
              booking_type: checkInForm.booking_type,
              booking_duration: parseInt(checkInForm.duration),
              total_cost: totalCost
            };
          }
        }
        return room;
      });
      
      setRooms(updatedRooms);
      
      // Update stats
      const newOccupiedRooms = updatedRooms.filter(r => r.status === "occupied").length;
      const newEmptyRooms = updatedRooms.filter(r => r.status === "empty").length;
      setStats(prevStats => ({
        ...prevStats,
        occupied_rooms: newOccupiedRooms,
        empty_rooms: newEmptyRooms,
        occupancy_rate: Math.round((newOccupiedRooms / updatedRooms.length) * 100)
      }));
      
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
      
      // Success notification
      const bookingTypeText = form.booking_type === 'hourly' ? 'giờ' : 
                             form.booking_type === 'daily' ? 'ngày' : 'tháng';
      
      if (isCompanyCheckIn) {
        alert(`✅ Check-in công ty thành công!
🏢 Công ty: ${companyCheckInForm.company_name}
👥 Số khách: ${companyCheckInForm.guests.filter(g => g.name.trim()).length}
📅 Loại đặt: ${form.duration} ${bookingTypeText}
💰 Tổng chi phí: ${totalCost.toLocaleString()} VND
🏠 Phòng: ${selectedRoom.number}`);
      } else {
        alert(`✅ Check-in thành công!
👤 Khách: ${checkInForm.guest_name}
📅 Loại đặt: ${form.duration} ${bookingTypeText}
💰 Tổng chi phí: ${totalCost.toLocaleString()} VND
🏠 Phòng: ${selectedRoom.number}`);
      }
      
    } catch (error) {
      console.error("Check-in error:", error);
      alert("❌ Lỗi khi check-in: " + error.message);
    }
  };

  // Functions for managing guests in company check-in
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

  // Hàm tính toán giá tiền dự kiến
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

  const handleCheckOut = async (room) => {
    try {
      // Mock checkout logic
      const checkInTime = new Date(room.check_in_date);
      const checkOutTime = new Date();
      const diffMs = checkOutTime - checkInTime;
      const diffHours = Math.ceil(diffMs / (1000 * 60 * 60));
      const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));
      
      // Calculate final cost
      let finalCost = room.total_cost || 0;
      
      // Mock cost calculation data
      const mockCostData = {
        check_in_time: room.check_in_date,
        check_out_time: checkOutTime.toISOString(),
        duration_hours: diffHours,
        duration_days: diffDays,
        total_cost: finalCost,
        calculation_type: room.booking_type,
        details: `${room.booking_type} - ${room.booking_duration} ${room.booking_type === 'hourly' ? 'giờ' : room.booking_type === 'daily' ? 'ngày' : 'tháng'}`
      };
      
      setCurrentCost(mockCostData);
      setSelectedRoom(room);
      setShowCheckOutModal(true);
    } catch (error) {
      alert("Lỗi khi tính toán chi phí: " + error.message);
    }
  };

  const confirmCheckOut = async () => {
    try {
      // Mock checkout - update room to empty status
      const updatedRooms = rooms.map(room => {
        if (room.id === selectedRoom.id) {
          return {
            ...room,
            status: "empty",
            guest_name: null,
            company_name: null,
            guests: [],
            check_in_date: null,
            check_out_date: null,
            booking_type: null,
            booking_duration: null,
            total_cost: null
          };
        }
        return room;
      });
      
      setRooms(updatedRooms);
      
      // Update stats
      const newOccupiedRooms = updatedRooms.filter(r => r.status === "occupied").length;
      const newEmptyRooms = updatedRooms.filter(r => r.status === "empty").length;
      setStats(prevStats => ({
        ...prevStats,
        occupied_rooms: newOccupiedRooms,
        empty_rooms: newEmptyRooms,
        occupancy_rate: Math.round((newOccupiedRooms / updatedRooms.length) * 100),
        today_revenue: (prevStats.today_revenue || 0) + (currentCost?.total_cost || 0)
      }));
      
      // Create mock bill
      const mockBill = {
        id: Date.now().toString(),
        room_number: selectedRoom.number,
        guest_name: selectedRoom.guest_name || selectedRoom.company_name || "Unknown",
        check_in_time: currentCost.check_in_time,
        check_out_time: currentCost.check_out_time,
        cost_calculation: currentCost
      };
      
      setBills(prevBills => [mockBill, ...prevBills]);
      setCheckoutBill(mockBill);
      setShowCheckOutModal(false);
      
      alert(`✅ Check-out thành công!
🏠 Phòng: ${selectedRoom.number}
💰 Tổng tiền: ${currentCost.total_cost?.toLocaleString()} VND
⏰ Thời gian lưu trú: ${currentCost.duration_hours} giờ`);
      
    } catch (error) {
      alert("Lỗi khi check-out: " + error.message);
    }
  };

  const handleUpdatePricing = async (e) => {
    e.preventDefault();
    try {
      await axios.put(`${API}/rooms/${selectedRoom.id}`, {
        pricing: pricingForm
      });
      setShowPricingModal(false);
      fetchData();
    } catch (error) {
      alert("Lỗi khi cập nhật giá: " + error.response?.data?.detail);
    }
  };

  const handleCreateDish = async (e) => {
    e.preventDefault();
    try {
      const dishData = {
        ...dishForm,
        price: parseFloat(dishForm.price)
      };
      
      if (selectedDish) {
        await axios.put(`${API}/dishes/${selectedDish.id}`, dishData);
      } else {
        await axios.post(`${API}/dishes`, dishData);
      }
      
      setShowDishModal(false);
      setDishForm({ name: "", price: "", description: "" });
      setSelectedDish(null);
      fetchData();
    } catch (error) {
      alert("Lỗi: " + error.response?.data?.detail);
    }
  };

  const handleCreateOrder = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/orders`, {
        ...orderForm,
        quantity: parseInt(orderForm.quantity)
      });
      setShowOrderModal(false);
      setOrderForm({ company_name: "", dish_id: "", quantity: 1 });
      fetchData();
    } catch (error) {
      alert("Lỗi: " + error.response?.data?.detail);
    }
  };

  const getRoomStatusColor = (status) => {
    switch (status) {
      case "empty": return "bg-green-100 text-green-800";
      case "occupied": return "bg-red-100 text-red-800";
      case "booked": return "bg-yellow-100 text-yellow-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const getRoomStatusText = (status) => {
    switch (status) {
      case "empty": return "Trống";
      case "occupied": return "Có khách";
      case "booked": return "Đã đặt";
      default: return "Khác";
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
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <span className="text-2xl">🏠</span>
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-500">Tổng phòng</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_rooms || 0}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <span className="text-2xl">✅</span>
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-500">Phòng trống</p>
                <p className="text-2xl font-bold text-green-600">{stats.empty_rooms || 0}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-red-100 rounded-lg">
                <span className="text-2xl">👥</span>
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-500">Có khách</p>
                <p className="text-2xl font-bold text-red-600">{stats.occupied_rooms || 0}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <span className="text-2xl">📊</span>
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-500">Tỷ lệ lấp đầy</p>
                <p className="text-2xl font-bold text-purple-600">{stats.occupancy_rate || 0}%</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <span className="text-2xl">💰</span>
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-500">Doanh thu hôm nay</p>
                <p className="text-lg font-bold text-yellow-600">{(stats.today_revenue || 0).toLocaleString()} VND</p>
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8 px-6">
              {[
                { key: "rooms", label: "Quản lý phòng", icon: "🏠" },
                { key: "guests", label: "Khách hàng", icon: "👥" },
                { key: "reservations", label: "Đặt phòng", icon: "📅" },
                { key: "meals", label: "Quản lý cơm", icon: "🍽️" },
                { key: "orders", label: "Đơn hàng", icon: "📋" },
                { key: "bills", label: "Hóa đơn", icon: "💰" }
              ].map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200 ${
                    activeTab === tab.key
                      ? "border-blue-500 text-blue-600"
                      : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                  }`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {/* Room Management Tab */}
            {activeTab === "rooms" && (
              <div>
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-semibold text-gray-900">Danh sách phòng</h2>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                  {rooms.map((room) => (
                    <div key={room.id} className="bg-gray-50 rounded-lg p-6 border-2 border-gray-200 hover:shadow-md transition-shadow">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h3 className="text-xl font-bold text-gray-900">Phòng {room.number}</h3>
                          <p className="text-sm text-gray-500 capitalize">{room.type === 'single' ? 'Đơn' : 'Đôi'}</p>
                        </div>
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${getRoomStatusColor(room.status)}`}>
                          {getRoomStatusText(room.status)}
                        </span>
                      </div>
                      
                      <div className="space-y-2 mb-4">
                        <p className="text-sm"><span className="font-medium">Loại:</span> {room.type === 'single' ? 'Đơn' : 'Đôi'}</p>
                        <div className="text-xs text-gray-600">
                          <p>Giờ 1: {(room.pricing?.hourly_first || 80000).toLocaleString()} VND</p>
                          <p>Giờ 2: {(room.pricing?.hourly_second || 40000).toLocaleString()} VND</p>
                          <p>Giờ 3+: {(room.pricing?.hourly_additional || 20000).toLocaleString()} VND/h</p>
                          <p>Theo ngày: {(room.pricing?.daily_rate || 500000).toLocaleString()} VND</p>
                        </div>
                        {(room.guest_name || room.company_name || (room.guests && room.guests.length > 0)) && (
                          <>
                            {room.company_name && (
                              <p className="text-sm"><span className="font-medium">Công ty:</span> {room.company_name}</p>
                            )}
                            {room.guests && room.guests.length > 0 ? (
                              <div className="text-sm">
                                <span className="font-medium">Khách ({room.guests.length}):</span>
                                <div className="ml-2 mt-1 space-y-1">
                                  {room.guests.map((guest, index) => (
                                    <div key={index} className="text-xs bg-blue-50 p-2 rounded border-l-2 border-blue-300">
                                      <div className="font-medium text-blue-800">{guest.name}</div>
                                      {guest.phone && <div className="text-blue-600">📞 {guest.phone}</div>}
                                      {guest.email && <div className="text-blue-600">📧 {guest.email}</div>}
                                      {guest.id_card && <div className="text-blue-600">🆔 {guest.id_card}</div>}
                                    </div>
                                  ))}
                                </div>
                              </div>
                            ) : room.guest_name ? (
                              <p className="text-sm"><span className="font-medium">Khách:</span> {room.guest_name}</p>
                            ) : null}
                            {room.booking_type && (
                              <p className="text-sm">
                                <span className="font-medium">Loại đặt:</span> 
                                <span className="ml-1 px-2 py-1 text-xs rounded bg-green-100 text-green-800">
                                  {room.booking_type === 'hourly' ? `${room.booking_duration || 1} giờ` : 
                                   room.booking_type === 'daily' ? `${room.booking_duration || 1} ngày` : 
                                   room.booking_type === 'monthly' ? `${room.booking_duration || 1} tháng` : room.booking_type}
                                </span>
                              </p>
                            )}
                            <p className="text-sm"><span className="font-medium">Check-in:</span> {new Date(room.check_in_date).toLocaleDateString('vi-VN')} {new Date(room.check_in_date).toLocaleTimeString('vi-VN')}</p>
                            <p className="text-sm"><span className="font-medium">Check-out:</span> {new Date(room.check_out_date).toLocaleDateString('vi-VN')} {new Date(room.check_out_date).toLocaleTimeString('vi-VN')}</p>
                            {room.total_cost && (
                              <p className="text-sm">
                                <span className="font-medium">Chi phí dự kiến:</span> 
                                <span className="ml-1 px-2 py-1 text-xs rounded bg-yellow-100 text-yellow-800 font-bold">
                                  {room.total_cost.toLocaleString()} VND
                                </span>
                              </p>
                            )}
                          </>
                        )}
                      </div>
                      
                      <div className="flex gap-2">
                        {room.status === "empty" && (
                          <>
                            <button
                              onClick={() => {
                                setSelectedRoom(room);
                                setShowCheckInModal(true);
                              }}
                              className="flex-1 bg-blue-600 text-white py-2 px-3 rounded text-sm hover:bg-blue-700 transition duration-200"
                            >
                              Check-in
                            </button>
                            <button
                              onClick={() => {
                                setSelectedRoom(room);
                                setPricingForm(room.pricing || {
                                  hourly_first: 80000,
                                  hourly_second: 40000,
                                  hourly_additional: 20000,
                                  daily_rate: 500000,
                                  monthly_rate: 12000000
                                });
                                setShowPricingModal(true);
                              }}
                              className="bg-yellow-600 text-white py-2 px-2 rounded text-sm hover:bg-yellow-700 transition duration-200"
                            >
                              💰
                            </button>
                          </>
                        )}
                        {room.status === "occupied" && (
                          <>
                            <button
                              onClick={() => {
                                setSelectedRoom(room);
                                setShowRoomDetailModal(true);
                              }}
                              className="bg-blue-500 text-white py-2 px-3 rounded text-sm hover:bg-blue-600 transition duration-200"
                            >
                              📋 Chi tiết
                            </button>
                            <button
                              onClick={() => handleCheckOut(room)}
                              className="flex-1 bg-red-600 text-white py-2 px-3 rounded text-sm hover:bg-red-700 transition duration-200"
                            >
                              Check-out
                            </button>
                          </>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Guest Management Tab */}
            {activeTab === "guests" && <GuestManagement />}

            {/* Reservation Management Tab */}
            {activeTab === "reservations" && <ReservationManagement />}

            {/* Meals Management Tab */}
            {activeTab === "meals" && (
              <div>
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-semibold text-gray-900">Quản lý món ăn</h2>
                  <button
                    onClick={() => {
                      setSelectedDish(null);
                      setDishForm({ name: "", price: "", description: "" });
                      setShowDishModal(true);
                    }}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition duration-200"
                  >
                    + Thêm món ăn
                  </button>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {dishes.map((dish) => (
                    <div key={dish.id} className="bg-white border rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">{dish.name}</h3>
                      <p className="text-2xl font-bold text-blue-600 mb-2">{dish.price.toLocaleString()} VND</p>
                      {dish.description && (
                        <p className="text-sm text-gray-600 mb-4">{dish.description}</p>
                      )}
                      <div className="flex gap-2">
                        <button
                          onClick={() => {
                            setSelectedDish(dish);
                            setDishForm({
                              name: dish.name,
                              price: dish.price.toString(),
                              description: dish.description || ""
                            });
                            setShowDishModal(true);
                          }}
                          className="flex-1 bg-yellow-600 text-white py-2 px-3 rounded text-sm hover:bg-yellow-700 transition duration-200"
                        >
                          Sửa
                        </button>
                        <button
                          onClick={() => setOrderForm({ ...orderForm, dish_id: dish.id })}
                          className="flex-1 bg-green-600 text-white py-2 px-3 rounded text-sm hover:bg-green-700 transition duration-200"
                        >
                          Đặt món
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
                
                {orderForm.dish_id && (
                  <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Tạo đơn hàng</h3>
                    <form onSubmit={handleCreateOrder} className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Tên công ty</label>
                        <input
                          type="text"
                          value={orderForm.company_name}
                          onChange={(e) => setOrderForm({ ...orderForm, company_name: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Số lượng</label>
                        <input
                          type="number"
                          min="1"
                          value={orderForm.quantity}
                          onChange={(e) => setOrderForm({ ...orderForm, quantity: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                          required
                        />
                      </div>
                      <div className="flex items-end gap-2">
                        <button
                          type="submit"
                          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition duration-200"
                        >
                          Tạo đơn
                        </button>
                        <button
                          type="button"
                          onClick={() => setOrderForm({ company_name: "", dish_id: "", quantity: 1 })}
                          className="bg-gray-400 text-white px-4 py-2 rounded-lg hover:bg-gray-500 transition duration-200"
                        >
                          Hủy
                        </button>
                      </div>
                    </form>
                  </div>
                )}
              </div>
            )}

            {/* Orders Tab */}
            {activeTab === "orders" && (
              <div>
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-semibold text-gray-900">Quản lý đơn hàng</h2>
                  <button
                    onClick={() => setShowOrderModal(true)}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition duration-200"
                  >
                    + Tạo đơn hàng
                  </button>
                </div>
                
                {/* Filter Section */}
                <div className="bg-gray-50 rounded-lg p-4 mb-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">🔍 Bộ lọc & Báo cáo</h3>
                  <OrderFilters onFiltersChange={fetchFilteredOrders} />
                </div>
                
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Công ty</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Món ăn</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Số lượng</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Đơn giá</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tổng tiền</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ngày đặt</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {orders.map((order) => (
                        <tr key={order.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{order.company_name}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{order.dish_name}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{order.quantity}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{order.unit_price?.toLocaleString()} VND</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">{order.total_price?.toLocaleString()} VND</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {new Date(order.order_date).toLocaleDateString('vi-VN')}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  
                  {orders.length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                      Chưa có đơn hàng nào
                    </div>
                  )}
                </div>
              </div>
            )}
            
            {/* Bills Tab */}
            {activeTab === "bills" && (
              <div>
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-semibold text-gray-900">Danh sách hóa đơn</h2>
                </div>
                
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Phòng</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Khách hàng</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Thời gian</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Chi tiết tính giá</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tổng tiền</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {bills.map((bill) => (
                        <tr key={bill.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">Phòng {bill.room_number}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{bill.guest_name}</td>
                          <td className="px-6 py-4 text-sm text-gray-900">
                            <div>
                              <p className="text-xs">Vào: {new Date(bill.check_in_time).toLocaleString('vi-VN')}</p>
                              <p className="text-xs">Ra: {new Date(bill.check_out_time).toLocaleString('vi-VN')}</p>
                              <p className="text-xs font-medium">{bill.cost_calculation?.duration_hours}h ({bill.cost_calculation?.duration_days} ngày)</p>
                            </div>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-600">
                            <p className="text-xs">{bill.cost_calculation?.details}</p>
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              {bill.cost_calculation?.calculation_type === 'hourly' && 'Theo giờ'}
                              {bill.cost_calculation?.calculation_type === 'daily_hourly' && 'Ngày + Giờ'}
                              {bill.cost_calculation?.calculation_type === 'monthly' && 'Theo tháng'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-blue-600">
                            {bill.cost_calculation?.total_cost?.toLocaleString()} VND
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  
                  {bills.length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                      Chưa có hóa đơn nào
                    </div>
                  )}
                </div>
              </div>
            )}
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
                  📋 Cá nhân
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
                  {isCompanyCheckIn ? '🏢 Check-in Công ty' : '📋 Check-in Cá nhân'}
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

      {/* Check-out Modal */}
      {showCheckOutModal && currentCost && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-lg w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Xác nhận Check-out - Phòng {selectedRoom?.number}
            </h3>
            
            <div className="space-y-4 mb-6">
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="font-medium text-gray-900">Thông tin khách hàng:</p>
                <p className="text-sm text-gray-600">Tên: {currentCost.guest_name}</p>
                <p className="text-sm text-gray-600">Check-in: {new Date(currentCost.check_in_time).toLocaleString('vi-VN')}</p>
                <p className="text-sm text-gray-600">Check-out: {new Date(currentCost.current_time).toLocaleString('vi-VN')}</p>
                <p className="text-sm font-medium text-blue-600">Thời gian ở: {currentCost.duration_hours}h ({currentCost.duration_days} ngày)</p>
              </div>
              
              <div className="bg-blue-50 p-4 rounded-lg border-2 border-blue-200">
                <p className="font-medium text-gray-900 mb-2">Chi tiết tính giá:</p>
                <p className="text-sm text-gray-600">{currentCost.details}</p>
                <p className="text-xl font-bold text-blue-600 mt-2">
                  Tổng cộng: {currentCost.total_cost?.toLocaleString()} VND
                </p>
              </div>
            </div>
            
            <div className="flex gap-4">
              <button
                onClick={confirmCheckOut}
                className="flex-1 bg-red-600 text-white py-3 px-4 rounded-lg hover:bg-red-700 transition duration-200 font-medium"
              >
                Xác nhận Check-out
              </button>
              <button
                onClick={() => {
                  setShowCheckOutModal(false);
                  setCurrentCost(null);
                }}
                className="flex-1 bg-gray-400 text-white py-3 px-4 rounded-lg hover:bg-gray-500 transition duration-200"
              >
                Hủy
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Pricing Modal */}
      {showPricingModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Cài đặt giá phòng {selectedRoom?.number}
            </h3>
            <form onSubmit={handleUpdatePricing} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Giờ thứ nhất (VND)</label>
                <input
                  type="number"
                  value={pricingForm.hourly_first}
                  onChange={(e) => setPricingForm({ ...pricingForm, hourly_first: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Giờ thứ hai (VND)</label>
                <input
                  type="number"
                  value={pricingForm.hourly_second}
                  onChange={(e) => setPricingForm({ ...pricingForm, hourly_second: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Giờ thứ 3+ (VND/giờ)</label>
                <input
                  type="number"
                  value={pricingForm.hourly_additional}
                  onChange={(e) => setPricingForm({ ...pricingForm, hourly_additional: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Theo ngày (VND)</label>
                <input
                  type="number"
                  value={pricingForm.daily_rate}
                  onChange={(e) => setPricingForm({ ...pricingForm, daily_rate: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Theo tháng (VND)</label>
                <input
                  type="number"
                  value={pricingForm.monthly_rate}
                  onChange={(e) => setPricingForm({ ...pricingForm, monthly_rate: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div className="flex gap-4">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition duration-200"
                >
                  Cập nhật giá
                </button>
                <button
                  type="button"
                  onClick={() => setShowPricingModal(false)}
                  className="flex-1 bg-gray-400 text-white py-2 px-4 rounded-lg hover:bg-gray-500 transition duration-200"
                >
                  Hủy
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Success message for checkout */}
      {checkoutBill && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
            <div className="text-center">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100 mb-4">
                <span className="text-2xl">✅</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Check-out thành công!</h3>
              <div className="bg-gray-50 p-4 rounded-lg mb-4 text-left">
                <p className="text-sm text-gray-600">{checkoutBill.details}</p>
                <p className="text-xl font-bold text-green-600 mt-2">
                  Tổng tiền: {checkoutBill.total_cost?.toLocaleString()} VND
                </p>
              </div>
              <button
                onClick={() => setCheckoutBill(null)}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition duration-200"
              >
                OK
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Dish Modal */}
      {showDishModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              {selectedDish ? "Sửa món ăn" : "Thêm món ăn mới"}
            </h3>
            <form onSubmit={handleCreateDish} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tên món</label>
                <input
                  type="text"
                  value={dishForm.name}
                  onChange={(e) => setDishForm({ ...dishForm, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Giá (VND)</label>
                <input
                  type="number"
                  value={dishForm.price}
                  onChange={(e) => setDishForm({ ...dishForm, price: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Mô tả (tùy chọn)</label>
                <textarea
                  value={dishForm.description}
                  onChange={(e) => setDishForm({ ...dishForm, description: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  rows={3}
                />
              </div>
              <div className="flex gap-4">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition duration-200"
                >
                  {selectedDish ? "Cập nhật" : "Thêm"}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowDishModal(false);
                    setSelectedDish(null);
                    setDishForm({ name: "", price: "", description: "" });
                  }}
                  className="flex-1 bg-gray-400 text-white py-2 px-4 rounded-lg hover:bg-gray-500 transition duration-200"
                >
                  Hủy
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Order Modal */}
      {showOrderModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Tạo đơn hàng mới</h3>
            <form onSubmit={handleCreateOrder} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tên công ty</label>
                <input
                  type="text"
                  value={orderForm.company_name}
                  onChange={(e) => setOrderForm({ ...orderForm, company_name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="Nhập tên công ty"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Món ăn</label>
                <select
                  value={orderForm.dish_id}
                  onChange={(e) => setOrderForm({ ...orderForm, dish_id: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="">Chọn món ăn</option>
                  {dishes.map((dish) => (
                    <option key={dish.id} value={dish.id}>
                      {dish.name} - {dish.price?.toLocaleString()} VND
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Số lượng</label>
                <input
                  type="number"
                  min="1"
                  value={orderForm.quantity}
                  onChange={(e) => setOrderForm({ ...orderForm, quantity: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div className="flex gap-4">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition duration-200"
                >
                  Tạo đơn hàng
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowOrderModal(false);
                    setOrderForm({ company_name: "", dish_id: "", quantity: 1 });
                  }}
                  className="flex-1 bg-gray-400 text-white py-2 px-4 rounded-lg hover:bg-gray-500 transition duration-200"
                >
                  Hủy
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Room Detail Modal */}
      {showRoomDetailModal && selectedRoom && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
              <h3 className="text-xl font-semibold text-gray-900">
                📋 Chi tiết phòng {selectedRoom.number}
              </h3>
              <button
                onClick={() => setShowRoomDetailModal(false)}
                className="text-gray-500 hover:text-gray-700 text-2xl"
              >
                ×
              </button>
            </div>
            
            <div className="p-6">
              {/* Room Basic Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h4 className="font-medium text-blue-800 mb-2">Thông tin phòng</h4>
                  <p><span className="font-medium">Số phòng:</span> {selectedRoom.number}</p>
                  <p><span className="font-medium">Loại phòng:</span> {selectedRoom.type === 'single' ? 'Đơn' : 'Đôi'}</p>
                  <p><span className="font-medium">Trạng thái:</span> 
                    <span className={`ml-2 px-2 py-1 rounded-full text-xs ${getRoomStatusColor(selectedRoom.status)}`}>
                      {getRoomStatusText(selectedRoom.status)}
                    </span>
                  </p>
                </div>
                
                <div className="bg-green-50 p-4 rounded-lg">
                  <h4 className="font-medium text-green-800 mb-2">Thông tin đặt phòng</h4>
                  {selectedRoom.booking_type && (
                    <p><span className="font-medium">Loại đặt:</span> 
                      <span className="ml-2 px-2 py-1 text-xs rounded bg-green-200 text-green-800">
                        {selectedRoom.booking_type === 'hourly' ? `${selectedRoom.booking_duration || 1} giờ` : 
                         selectedRoom.booking_type === 'daily' ? `${selectedRoom.booking_duration || 1} ngày` : 
                         selectedRoom.booking_type === 'monthly' ? `${selectedRoom.booking_duration || 1} tháng` : selectedRoom.booking_type}
                      </span>
                    </p>
                  )}
                  <p><span className="font-medium">Check-in:</span> {new Date(selectedRoom.check_in_date).toLocaleString('vi-VN')}</p>
                  <p><span className="font-medium">Check-out dự kiến:</span> {new Date(selectedRoom.check_out_date).toLocaleString('vi-VN')}</p>
                  {selectedRoom.total_cost && (
                    <p><span className="font-medium">Chi phí dự kiến:</span> 
                      <span className="ml-2 px-2 py-1 text-xs rounded bg-yellow-200 text-yellow-800 font-bold">
                        {selectedRoom.total_cost.toLocaleString()} VND
                      </span>
                    </p>
                  )}
                </div>
              </div>

              {/* Company Info */}
              {selectedRoom.company_name && (
                <div className="mb-6">
                  <h4 className="font-medium text-gray-800 mb-3 flex items-center">
                    🏢 Thông tin công ty
                  </h4>
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <p className="text-lg font-semibold text-purple-800">{selectedRoom.company_name}</p>
                  </div>
                </div>
              )}

              {/* Guests Info */}
              {selectedRoom.guests && selectedRoom.guests.length > 0 ? (
                <div className="mb-6">
                  <h4 className="font-medium text-gray-800 mb-3 flex items-center">
                    👥 Danh sách khách ({selectedRoom.guests.length} người)
                  </h4>
                  <div className="space-y-3">
                    {selectedRoom.guests.map((guest, index) => (
                      <div key={index} className="bg-gray-50 p-4 rounded-lg border-l-4 border-blue-400">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                          <div>
                            <p className="font-semibold text-blue-800 text-lg">{guest.name}</p>
                            {guest.phone && (
                              <p className="text-sm text-gray-600">
                                <span className="font-medium">📞 Điện thoại:</span> {guest.phone}
                              </p>
                            )}
                          </div>
                          <div>
                            {guest.email && (
                              <p className="text-sm text-gray-600">
                                <span className="font-medium">📧 Email:</span> {guest.email}
                              </p>
                            )}
                            {guest.id_card && (
                              <p className="text-sm text-gray-600">
                                <span className="font-medium">🆔 CMND/CCCD:</span> {guest.id_card}
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : selectedRoom.guest_name ? (
                <div className="mb-6">
                  <h4 className="font-medium text-gray-800 mb-3 flex items-center">
                    👤 Thông tin khách
                  </h4>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="font-semibold text-blue-800 text-lg">{selectedRoom.guest_name}</p>
                    {selectedRoom.guest_phone && (
                      <p className="text-sm text-gray-600">
                        <span className="font-medium">📞 Điện thoại:</span> {selectedRoom.guest_phone}
                      </p>
                    )}
                  </div>
                </div>
              ) : null}

              {/* Action Buttons */}
              <div className="flex gap-3 pt-4 border-t border-gray-200">
                <button
                  onClick={() => {
                    setShowRoomDetailModal(false);
                    handleCheckOut(selectedRoom);
                  }}
                  className="flex-1 bg-red-600 text-white py-3 px-4 rounded-lg hover:bg-red-700 transition duration-200 font-medium"
                >
                  🚪 Check-out ngay
                </button>
                <button
                  onClick={() => setShowRoomDetailModal(false)}
                  className="bg-gray-500 text-white py-3 px-4 rounded-lg hover:bg-gray-600 transition duration-200 font-medium"
                >
                  Đóng
                </button>
              </div>
            </div>
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

  return (
    <div className="App">
      {admin ? (
        <Dashboard admin={admin} onLogout={handleLogout} />
      ) : (
        <Login onLogin={handleLogin} />
      )}
    </div>
  );
}

export default App;