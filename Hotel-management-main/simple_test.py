#!/usr/bin/env python3
"""
Simple test to verify the real-time cost calculation feature
"""

import requests
import json
from datetime import datetime, timezone
import time

BASE_URL = "http://127.0.0.1:8001/api"

def simple_test():
    """Simple test of the API"""
    print("=== Simple API Test ===")
    
    # Test API is working
    try:
        response = requests.get(f"{BASE_URL}/rooms", timeout=5)
        if response.status_code != 200:
            print(f"❌ API not working: {response.status_code}")
            return False
            
        rooms = response.json()
        print(f"✓ API working, found {len(rooms)} rooms")
        
        # Find empty room
        empty_room = None
        for room in rooms:
            if room["status"] == "empty":
                empty_room = room
                break
        
        if not empty_room:
            print("❌ No empty rooms")
            return False
            
        room_id = empty_room["id"]
        print(f"✓ Using room {empty_room['number']} (ID: {room_id})")
        
        # Test hourly checkin
        checkin_data = {
            "company_name": "Test Hourly",
            "guests": [{"name": "Test Guest", "phone": "123456789"}],
            "booking_type": "hourly",
            "duration": 2,
            "check_in_date": datetime.now(timezone.utc).isoformat()
        }
        
        response = requests.post(f"{BASE_URL}/rooms/{room_id}/checkin-company", 
                               json=checkin_data, timeout=5)
        if response.status_code != 200:
            print(f"❌ Check-in failed: {response.status_code} - {response.text}")
            return False
            
        print("✓ Hourly check-in successful")
        
        # Wait a moment to see time difference
        time.sleep(2)
        
        # Test current cost
        response = requests.get(f"{BASE_URL}/rooms/{room_id}/current-cost", timeout=5)
        if response.status_code != 200:
            print(f"❌ Current cost failed: {response.status_code} - {response.text}")
            return False
            
        cost_data = response.json()
        print("✓ Current cost data retrieved:")
        print(f"  - Booking type: {cost_data.get('booking_type', 'N/A')}")
        print(f"  - Is hourly: {cost_data.get('is_hourly_booking', 'N/A')}")
        print(f"  - Method: {cost_data.get('calculation_method', 'N/A')}")
        print(f"  - Message: {cost_data.get('message', 'N/A')}")
        print(f"  - Cost: {cost_data.get('total_cost', 0):,.0f} VND")
        
        # Check out
        response = requests.post(f"{BASE_URL}/rooms/{room_id}/checkout", timeout=5)
        if response.status_code != 200:
            print(f"❌ Check-out failed: {response.status_code}")
            return False
            
        print("✓ Check-out successful")
        
        # Test daily booking
        print("\n--- Testing Daily Booking ---")
        
        checkin_data["booking_type"] = "daily"
        checkin_data["company_name"] = "Test Daily"
        
        response = requests.post(f"{BASE_URL}/rooms/{room_id}/checkin-company", 
                               json=checkin_data, timeout=5)
        if response.status_code != 200:
            print(f"❌ Daily check-in failed: {response.status_code}")
            return False
            
        print("✓ Daily check-in successful")
        
        # Test current cost for daily
        response = requests.get(f"{BASE_URL}/rooms/{room_id}/current-cost", timeout=5)
        if response.status_code != 200:
            print(f"❌ Daily current cost failed: {response.status_code}")
            return False
            
        cost_data = response.json()
        print("✓ Daily cost data retrieved:")
        print(f"  - Booking type: {cost_data.get('booking_type', 'N/A')}")
        print(f"  - Is hourly: {cost_data.get('is_hourly_booking', 'N/A')}")
        print(f"  - Method: {cost_data.get('calculation_method', 'N/A')}")
        print(f"  - Message: {cost_data.get('message', 'N/A')}")
        print(f"  - Cost: {cost_data.get('total_cost', 0):,.0f} VND")
        
        # Check out
        response = requests.post(f"{BASE_URL}/rooms/{room_id}/checkout", timeout=5)
        if response.status_code != 200:
            print(f"❌ Daily check-out failed: {response.status_code}")
            return False
            
        print("✓ Daily check-out successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Real-time Cost Calculation")
    print("==================================")
    
    if simple_test():
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed!")
