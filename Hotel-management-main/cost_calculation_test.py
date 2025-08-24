#!/usr/bin/env python3
"""
Direct Cost Calculation Test
Tests the calculate_room_cost function directly with specific durations
"""

import requests
import json
from datetime import datetime, timedelta, timezone
import sys

BACKEND_URL = "https://hotelmanager-1.preview.emergentagent.com/api"

class CostCalculationTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        
    def log(self, message):
        print(f"[COST TEST] {message}")
        
    def test_cost_calculation_via_api(self):
        """Test cost calculation by checking in with past times"""
        self.log("Testing Cost Calculation via API with Past Times...")
        
        try:
            # Get an empty room
            response = self.session.get(f"{self.base_url}/rooms")
            rooms = response.json()
            test_room = None
            for room in rooms:
                if room["status"] == "empty":
                    test_room = room
                    break
                    
            if not test_room:
                self.log("❌ No empty rooms available")
                return False
                
            room_id = test_room["id"]
            
            # Reset to default pricing
            default_pricing = {
                "hourly_first": 80000,
                "hourly_second": 40000, 
                "hourly_additional": 20000,
                "daily_rate": 500000,
                "monthly_rate": 12000000
            }
            
            self.session.put(f"{self.base_url}/rooms/{room_id}", json={"pricing": default_pricing})
            
            # Test Scenario 1: Check in 2 hours ago, checkout now (2 hour duration)
            self.log("Scenario 1: 2 hour duration (check-in 2 hours ago)")
            now = datetime.now(timezone.utc)
            two_hours_ago = now - timedelta(hours=2)
            
            checkin_data = {
                "guest_name": "Test Guest 2H Past",
                "check_in_date": two_hours_ago.isoformat(),
                "check_out_date": now.isoformat()  # This is ignored by checkout endpoint
            }
            
            # Manually update the room with past check-in time
            update_data = {
                "status": "occupied",
                "guest_name": "Test Guest 2H Past",
                "check_in_date": two_hours_ago.isoformat()
            }
            
            response = self.session.put(f"{self.base_url}/rooms/{room_id}", json=update_data)
            if response.status_code != 200:
                self.log(f"❌ Failed to update room: {response.status_code}")
                return False
                
            # Now checkout - this should calculate 2 hours duration
            response = self.session.post(f"{self.base_url}/rooms/{room_id}/checkout")
            if response.status_code != 200:
                self.log(f"❌ Checkout failed: {response.status_code}")
                return False
                
            result = response.json()
            expected_cost = 120000  # 80k + 40k for 2 hours
            actual_cost = result["bill"]["total_cost"]
            duration = result["bill"]["duration_hours"]
            
            self.log(f"2 hours: Duration={duration:.2f}h, Expected {expected_cost}, Got {actual_cost}")
            
            # Allow some tolerance for timing differences
            if abs(actual_cost - expected_cost) > 10000:
                self.log(f"❌ 2 hour scenario failed: Expected ~{expected_cost}, got {actual_cost}")
                return False
                
            # Test Scenario 2: Check in 4 hours ago, checkout now (4 hour duration)
            self.log("Scenario 2: 4 hour duration (check-in 4 hours ago)")
            four_hours_ago = now - timedelta(hours=4)
            
            update_data = {
                "status": "occupied",
                "guest_name": "Test Guest 4H Past",
                "check_in_date": four_hours_ago.isoformat()
            }
            
            response = self.session.put(f"{self.base_url}/rooms/{room_id}", json=update_data)
            if response.status_code != 200:
                self.log(f"❌ Failed to update room: {response.status_code}")
                return False
                
            response = self.session.post(f"{self.base_url}/rooms/{room_id}/checkout")
            if response.status_code != 200:
                self.log(f"❌ Checkout failed: {response.status_code}")
                return False
                
            result = response.json()
            expected_cost = 160000  # 80k + 40k + 2*20k for 4 hours
            actual_cost = result["bill"]["total_cost"]
            duration = result["bill"]["duration_hours"]
            
            self.log(f"4 hours: Duration={duration:.2f}h, Expected {expected_cost}, Got {actual_cost}")
            
            if abs(actual_cost - expected_cost) > 10000:
                self.log(f"❌ 4 hour scenario failed: Expected ~{expected_cost}, got {actual_cost}")
                return False
                
            # Test Scenario 3: Check in 1 day + 3 hours ago (daily + hourly)
            self.log("Scenario 3: 1 day + 3 hours duration")
            day_plus_3h_ago = now - timedelta(days=1, hours=3)
            
            update_data = {
                "status": "occupied",
                "guest_name": "Test Guest Daily",
                "check_in_date": day_plus_3h_ago.isoformat()
            }
            
            response = self.session.put(f"{self.base_url}/rooms/{room_id}", json=update_data)
            if response.status_code != 200:
                self.log(f"❌ Failed to update room: {response.status_code}")
                return False
                
            response = self.session.post(f"{self.base_url}/rooms/{room_id}/checkout")
            if response.status_code != 200:
                self.log(f"❌ Checkout failed: {response.status_code}")
                return False
                
            result = response.json()
            expected_cost = 500000 + 80000 + 40000 + 20000  # 1 day + 3 hours
            actual_cost = result["bill"]["total_cost"]
            duration = result["bill"]["duration_hours"]
            
            self.log(f"1 day + 3 hours: Duration={duration:.2f}h, Expected {expected_cost}, Got {actual_cost}")
            
            if abs(actual_cost - expected_cost) > 20000:  # Allow more tolerance for daily calculations
                self.log(f"❌ Daily scenario failed: Expected ~{expected_cost}, got {actual_cost}")
                return False
                
            self.log("✅ All cost calculation scenarios passed!")
            return True
            
        except Exception as e:
            self.log(f"❌ Exception in cost calculation: {str(e)}")
            return False
            
    def run_test(self):
        """Run cost calculation test"""
        self.log("=" * 60)
        self.log("STARTING COST CALCULATION TEST")
        self.log("=" * 60)
        
        if self.test_cost_calculation_via_api():
            self.log("🎉 COST CALCULATION TEST PASSED!")
            return True
        else:
            self.log("⚠️  COST CALCULATION TEST FAILED")
            return False

if __name__ == "__main__":
    tester = CostCalculationTest()
    success = tester.run_test()
    sys.exit(0 if success else 1)