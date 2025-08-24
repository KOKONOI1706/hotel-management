#!/usr/bin/env python3
"""
Test script cho tính năng check-in công ty với nhiều khách
"""

import requests
import json
from datetime import datetime, timezone

BASE_URL = "http://127.0.0.1:8001/api"

def test_company_checkin():
    """Test check-in với công ty và nhiều khách"""
    
    print("=== TEST CHECK-IN CÔNG TY VỚI NHIỀU KHÁCH ===\n")
    
    # 1. Lấy danh sách phòng trống
    print("1. Lấy danh sách phòng...")
    response = requests.get(f"{BASE_URL}/rooms")
    rooms = response.json()
    
    empty_rooms = [room for room in rooms if room['status'] == 'empty']
    if not empty_rooms:
        print("❌ Không có phòng trống để test!")
        return
    
    room = empty_rooms[0]
    print(f"✅ Tìm thấy phòng trống: {room['number']} (ID: {room['id']})")
    
    # 2. Test check-in công ty với nhiều khách
    print("\n2. Test check-in công ty với nhiều khách...")
    
    checkin_data = {
        "company_name": "Công ty TNHH ABC",
        "guests": [
            {
                "name": "Nguyễn Văn A",
                "phone": "0123456789",
                "email": "a@abc.com",
                "id_card": "123456789"
            },
            {
                "name": "Trần Thị B", 
                "phone": "0987654321",
                "email": "b@abc.com",
                "id_card": "987654321"
            },
            {
                "name": "Lê Văn C",
                "phone": "0111222333",
                "email": "c@abc.com", 
                "id_card": "111222333"
            }
        ],
        "booking_type": "daily",
        "duration": 2,
        "check_in_date": datetime.now(timezone.utc).isoformat()
    }
    
    response = requests.post(
        f"{BASE_URL}/rooms/{room['id']}/checkin-company",
        json=checkin_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Check-in thành công!")
        print(f"   Công ty: {result['company_name']}")
        print(f"   Số khách: {len(result['guests'])}")
        print(f"   Tên khách: {[guest['name'] for guest in result['guests']]}")
        print(f"   Tổng chi phí: {result['total_cost']:,.0f} VND")
        room_id = result['id']
    else:
        print(f"❌ Check-in thất bại: {response.text}")
        return
    
    # 3. Test lấy thông tin khách trong phòng
    print("\n3. Test lấy thông tin khách trong phòng...")
    response = requests.get(f"{BASE_URL}/rooms/{room_id}/guests")
    
    if response.status_code == 200:
        guests_info = response.json()
        print(f"✅ Lấy thông tin thành công:")
        print(f"   Phòng: {guests_info['room_number']}")
        print(f"   Công ty: {guests_info['company_name']}")
        print(f"   Danh sách khách:")
        for i, guest in enumerate(guests_info['guests'], 1):
            print(f"     {i}. {guest['name']} - SĐT: {guest['phone']} - Email: {guest['email']}")
    else:
        print(f"❌ Lỗi lấy thông tin: {response.text}")
    
    # 4. Test tính toán chi phí hiện tại
    print("\n4. Test tính toán chi phí hiện tại...")
    response = requests.get(f"{BASE_URL}/rooms/{room_id}/current-cost")
    
    if response.status_code == 200:
        cost_info = response.json()
        print(f"✅ Tính toán thành công:")
        print(f"   Công ty: {cost_info['company_name']}")
        print(f"   Chi phí hiện tại: {cost_info['total_cost']:,.0f} VND")
        print(f"   Chi tiết: {cost_info['details']}")
    else:
        print(f"❌ Lỗi tính toán: {response.text}")
    
    # 5. Test check-out
    print("\n5. Test check-out...")
    response = requests.post(f"{BASE_URL}/rooms/{room_id}/checkout")
    
    if response.status_code == 200:
        checkout_result = response.json()
        print(f"✅ Check-out thành công!")
        print(f"   Công ty: {checkout_result['company_name']}")
        print(f"   Số khách: {len(checkout_result['guests'])}")
        print(f"   Tổng chi phí: {checkout_result['bill']['total_cost']:,.0f} VND")
        print(f"   Chi tiết: {checkout_result['bill']['details']}")
    else:
        print(f"❌ Check-out thất bại: {response.text}")

def test_legacy_checkin():
    """Test check-in cũ vẫn hoạt động"""
    
    print("\n=== TEST CHECK-IN CŨ (BACKWARD COMPATIBILITY) ===\n")
    
    # Lấy phòng trống
    response = requests.get(f"{BASE_URL}/rooms")
    rooms = response.json()
    
    empty_rooms = [room for room in rooms if room['status'] == 'empty']
    if not empty_rooms:
        print("❌ Không có phòng trống để test!")
        return
    
    room = empty_rooms[0]
    print(f"✅ Tìm thấy phòng trống: {room['number']} (ID: {room['id']})")
    
    # Test check-in cũ
    legacy_checkin = {
        "guest_name": "Nguyễn Văn Cũ",
        "guest_phone": "0999888777",
        "guest_id": "111111111",
        "booking_type": "hourly",
        "duration": 3,
        "check_in_date": datetime.now(timezone.utc).isoformat()
    }
    
    response = requests.post(
        f"{BASE_URL}/rooms/{room['id']}/checkin",
        json=legacy_checkin
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Check-in cũ thành công!")
        print(f"   Tên khách (legacy): {result.get('guest_name')}")
        print(f"   Công ty (auto): {result.get('company_name')}")
        print(f"   Số khách: {len(result.get('guests', []))}")
        print(f"   Chi phí: {result['total_cost']:,.0f} VND")
        
        # Check-out luôn
        requests.post(f"{BASE_URL}/rooms/{result['id']}/checkout")
        print("✅ Check-out hoàn tất")
    else:
        print(f"❌ Check-in cũ thất bại: {response.text}")

def test_migration():
    """Test migration endpoint"""
    
    print("\n=== TEST MIGRATION DỮ LIỆU CŨ ===\n")
    
    response = requests.post(f"{BASE_URL}/migrate/rooms")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Migration thành công: {result['message']}")
    else:
        print(f"❌ Migration thất bại: {response.text}")

if __name__ == "__main__":
    try:
        test_company_checkin()
        test_legacy_checkin()
        test_migration()
        print("\n🎉 TẤT CẢ TEST HOÀN THÀNH!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Không thể kết nối đến server. Hãy đảm bảo server đang chạy trên port 8001!")
    except Exception as e:
        print(f"❌ Lỗi không xác định: {e}")
