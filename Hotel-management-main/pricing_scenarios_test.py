#!/usr/bin/env python3
"""
Additional Pricing Scenarios Test
Tests specific duration scenarios for the pricing system
"""

import requests
import json
from datetime import datetime, timedelta, timezone
import sys

BACKEND_URL = "https://hotelmanager-1.preview.emergentagent.com/api"

class PricingScenariosTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        
    def log(self, message):
        print(f"[PRICING TEST] {message}")
        
    def test_hourly_scenarios(self):
        """Test different hourly duration scenarios"""
        self.log("Testing Hourly Pricing Scenarios...")
        
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
            
            # Test Scenario 1: 1 hour stay (should be 80k)
            self.log("Scenario 1: 1 hour stay")
            now = datetime.now(timezone.utc)
            checkin_data = {
                "guest_name": "Test Guest 1H",
                "check_in_date": now.isoformat(),
                "check_out_date": (now + timedelta(hours=1)).isoformat()
            }
            
            self.session.post(f"{self.base_url}/rooms/{room_id}/checkin", json=checkin_data)
            response = self.session.post(f"{self.base_url}/rooms/{room_id}/checkout")
            result = response.json()
            
            expected_cost = 80000
            actual_cost = result["bill"]["total_cost"]
            self.log(f"1 hour: Expected {expected_cost}, Got {actual_cost}")
            
            if actual_cost != expected_cost:
                self.log(f"❌ 1 hour scenario failed: Expected {expected_cost}, got {actual_cost}")
                return False
                
            # Test Scenario 2: 2 hour stay (should be 80k + 40k = 120k)
            self.log("Scenario 2: 2 hour stay")
            checkin_data = {
                "guest_name": "Test Guest 2H",
                "check_in_date": now.isoformat(),
                "check_out_date": (now + timedelta(hours=2)).isoformat()
            }
            
            self.session.post(f"{self.base_url}/rooms/{room_id}/checkin", json=checkin_data)
            response = self.session.post(f"{self.base_url}/rooms/{room_id}/checkout")
            result = response.json()
            
            expected_cost = 120000  # 80k + 40k
            actual_cost = result["bill"]["total_cost"]
            self.log(f"2 hours: Expected {expected_cost}, Got {actual_cost}")
            
            if actual_cost != expected_cost:
                self.log(f"❌ 2 hour scenario failed: Expected {expected_cost}, got {actual_cost}")
                return False
                
            # Test Scenario 3: 4 hour stay (should be 80k + 40k + 2*20k = 160k)
            self.log("Scenario 3: 4 hour stay")
            checkin_data = {
                "guest_name": "Test Guest 4H",
                "check_in_date": now.isoformat(),
                "check_out_date": (now + timedelta(hours=4)).isoformat()
            }
            
            self.session.post(f"{self.base_url}/rooms/{room_id}/checkin", json=checkin_data)
            response = self.session.post(f"{self.base_url}/rooms/{room_id}/checkout")
            result = response.json()
            
            expected_cost = 160000  # 80k + 40k + 2*20k
            actual_cost = result["bill"]["total_cost"]
            self.log(f"4 hours: Expected {expected_cost}, Got {actual_cost}")
            
            if actual_cost != expected_cost:
                self.log(f"❌ 4 hour scenario failed: Expected {expected_cost}, got {actual_cost}")
                return False
                
            self.log("✅ All hourly scenarios passed!")
            return True
            
        except Exception as e:
            self.log(f"❌ Exception in hourly scenarios: {str(e)}")
            return False
            
    def test_daily_scenario(self):
        """Test daily pricing scenario"""
        self.log("Testing Daily Pricing Scenario...")
        
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
            
            # Test Scenario: 1 day + 3 hours stay
            self.log("Scenario: 1 day + 3 hours stay")
            now = datetime.now(timezone.utc)
            checkin_data = {
                "guest_name": "Test Guest Daily",
                "check_in_date": now.isoformat(),
                "check_out_date": (now + timedelta(days=1, hours=3)).isoformat()
            }
            
            self.session.post(f"{self.base_url}/rooms/{room_id}/checkin", json=checkin_data)
            response = self.session.post(f"{self.base_url}/rooms/{room_id}/checkout")
            result = response.json()
            
            # Expected: 1 day (500k) + 3 hours (80k + 40k + 20k) = 640k
            expected_cost = 500000 + 80000 + 40000 + 20000  # 640k
            actual_cost = result["bill"]["total_cost"]
            self.log(f"1 day + 3 hours: Expected {expected_cost}, Got {actual_cost}")
            
            if abs(actual_cost - expected_cost) > 1000:  # Allow small rounding differences
                self.log(f"❌ Daily scenario failed: Expected ~{expected_cost}, got {actual_cost}")
                return False
                
            self.log("✅ Daily scenario passed!")
            return True
            
        except Exception as e:
            self.log(f"❌ Exception in daily scenario: {str(e)}")
            return False
            
    def run_all_scenarios(self):
        """Run all pricing scenario tests"""
        self.log("=" * 60)
        self.log("STARTING PRICING SCENARIOS TESTS")
        self.log("=" * 60)
        
        scenarios = [
            ("Hourly Scenarios", self.test_hourly_scenarios),
            ("Daily Scenario", self.test_daily_scenario)
        ]
        
        passed_count = 0
        total_count = len(scenarios)
        
        for scenario_name, scenario_func in scenarios:
            self.log(f"\n--- {scenario_name} ---")
            if scenario_func():
                passed_count += 1
                
        self.log(f"\nPRICING SCENARIOS: {passed_count}/{total_count} passed")
        
        if passed_count == total_count:
            self.log("🎉 ALL PRICING SCENARIOS PASSED!")
            return True
        else:
            self.log("⚠️  SOME PRICING SCENARIOS FAILED")
            return False

if __name__ == "__main__":
    tester = PricingScenariosTest()
    success = tester.run_all_scenarios()
    sys.exit(0 if success else 1)