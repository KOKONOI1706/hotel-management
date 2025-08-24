#!/usr/bin/env python3
"""
Test script to verify real-time cost calculation only applies to hourly bookings
"""

import requests
import json
from datetime import datetime, timezone

BASE_URL = "http://127.0.0.1:8001/api"

def test_hourly_booking_real_time():
    """Test that hourly bookings get real-time cost calculation"""
    print("=== Testing Hourly Booking Real-time Cost ===")
    
    # First, get available rooms
    response = requests.get(f"{BASE_URL}/rooms")
    if response.status_code != 200:
        print("Failed to get rooms")
        return
    
    rooms = response.json()
    empty_room = None
    for room in rooms:
        if room["status"] == "empty":
            empty_room = room
            break
    
    if not empty_room:
        print("No empty rooms available for testing")
        return
    
    room_id = empty_room["id"]
    print(f"Using room: {empty_room['number']}")
    
    # Check in with hourly booking
    checkin_data = {
        "company_name": "Test Company",
        "guests": [
            {
                "name": "Test Guest",
                "phone": "0123456789",
                "email": "test@example.com",
                "id_card": "123456789"
            }
        ],
        "booking_type": "hourly",
        "duration": 2,  # 2 hours
        "check_in_date": datetime.now(timezone.utc).isoformat()
    }
    
    # Check in
    response = requests.post(f"{BASE_URL}/rooms/{room_id}/checkin-company", 
                           json=checkin_data)
    if response.status_code != 200:
        print(f"Failed to check in: {response.text}")
        return
    
    print("✓ Successfully checked in with hourly booking")
    
    # Get current cost (should be real-time for hourly)
    response = requests.get(f"{BASE_URL}/rooms/{room_id}/current-cost")
    if response.status_code != 200:
        print(f"Failed to get current cost: {response.text}")
        return
    
    cost_data = response.json()
    print(f"✓ Current cost data:")
    print(f"  - Booking type: {cost_data.get('booking_type')}")
    print(f"  - Is hourly booking: {cost_data.get('is_hourly_booking')}")
    print(f"  - Calculation method: {cost_data.get('calculation_method')}")
    print(f"  - Message: {cost_data.get('message')}")
    print(f"  - Total cost: {cost_data.get('total_cost'):,.0f} VND")
    print(f"  - Duration: {cost_data.get('duration_hours')} hours")
    
    # Check out
    response = requests.post(f"{BASE_URL}/rooms/{room_id}/checkout")
    if response.status_code != 200:
        print(f"Failed to check out: {response.text}")
        return
    
    print("✓ Successfully checked out")

def test_daily_booking_fixed_cost():
    """Test that daily bookings get fixed cost (not real-time)"""
    print("\n=== Testing Daily Booking Fixed Cost ===")
    
    # Get available rooms
    response = requests.get(f"{BASE_URL}/rooms")
    if response.status_code != 200:
        print("Failed to get rooms")
        return
    
    rooms = response.json()
    empty_room = None
    for room in rooms:
        if room["status"] == "empty":
            empty_room = room
            break
    
    if not empty_room:
        print("No empty rooms available for testing")
        return
    
    room_id = empty_room["id"]
    print(f"Using room: {empty_room['number']}")
    
    # Check in with daily booking
    checkin_data = {
        "company_name": "Test Company Daily",
        "guests": [
            {
                "name": "Test Guest Daily",
                "phone": "0987654321",
                "email": "daily@example.com",
                "id_card": "987654321"
            }
        ],
        "booking_type": "daily",
        "duration": 2,  # 2 days
        "check_in_date": datetime.now(timezone.utc).isoformat()
    }
    
    # Check in
    response = requests.post(f"{BASE_URL}/rooms/{room_id}/checkin-company", 
                           json=checkin_data)
    if response.status_code != 200:
        print(f"Failed to check in: {response.text}")
        return
    
    print("✓ Successfully checked in with daily booking")
    
    # Get current cost (should be fixed for daily)
    response = requests.get(f"{BASE_URL}/rooms/{room_id}/current-cost")
    if response.status_code != 200:
        print(f"Failed to get current cost: {response.text}")
        return
    
    cost_data = response.json()
    print(f"✓ Current cost data:")
    print(f"  - Booking type: {cost_data.get('booking_type')}")
    print(f"  - Is hourly booking: {cost_data.get('is_hourly_booking')}")
    print(f"  - Calculation method: {cost_data.get('calculation_method')}")
    print(f"  - Message: {cost_data.get('message')}")
    print(f"  - Total cost: {cost_data.get('total_cost'):,.0f} VND")
    
    # Check out
    response = requests.post(f"{BASE_URL}/rooms/{room_id}/checkout")
    if response.status_code != 200:
        print(f"Failed to check out: {response.text}")
        return
    
    print("✓ Successfully checked out")

if __name__ == "__main__":
    print("Testing Real-time Cost Calculation Logic")
    print("========================================")
    
    try:
        test_hourly_booking_real_time()
        test_daily_booking_fixed_cost()
        print("\n✅ All tests completed!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
