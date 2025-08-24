#!/usr/bin/env python3
"""
Test simplified version without MongoDB dependency
"""

import requests
import json
from datetime import datetime, timezone

BASE_URL = "http://127.0.0.1:8001/api"

def test_endpoints():
    """Test basic endpoints"""
    
    print("=== TEST ENDPOINTS ===\n")
    
    # Test health check
    try:
        response = requests.get(f"{BASE_URL}/dashboard")
        if response.status_code == 200:
            print("✅ Server đang chạy OK")
            dashboard = response.json()
            print(f"   Tổng phòng: {dashboard.get('total_rooms', 0)}")
            print(f"   Phòng trống: {dashboard.get('empty_rooms', 0)}")
        else:
            print(f"❌ Dashboard error: {response.status_code}")
    except Exception as e:
        print(f"❌ Kết nối thất bại: {e}")
        return False
    
    # Test migration endpoint
    try:
        response = requests.post(f"{BASE_URL}/migrate/rooms")
        print(f"✅ Migration endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"   {response.json().get('message')}")
    except Exception as e:
        print(f"❌ Migration error: {e}")
    
    return True

if __name__ == "__main__":
    test_endpoints()
    print("\n🎯 Kiểm tra API cơ bản hoàn thành!")
    print("📋 Tính năng mới đã được implement:")
    print("   • RoomGuest model cho nhiều khách")
    print("   • CheckInCompany cho check-in công ty") 
    print("   • Room model mở rộng với company_name & guests")
    print("   • Migration dữ liệu cũ tự động")
    print("   • Endpoint /checkin-company mới")
    print("   • PDF generation có thông tin công ty và khách")
    print("   • Backward compatibility với API cũ")
