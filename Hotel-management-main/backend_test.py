    #!/usr/bin/env python3
"""
Backend API Testing for Hotel Management System
Tests all endpoints systematically according to test_result.md priorities
"""

import requests
import json
from datetime import datetime, timedelta
import sys
import os

# Get backend URL from frontend .env
BACKEND_URL = "https://hotelmanager-1.preview.emergentagent.com/api"

class HotelBackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = {
            "admin_auth": {"passed": False, "details": ""},
            "room_management": {"passed": False, "details": ""},
            "pricing_system": {"passed": False, "details": ""},
            "auto_cost_calculation": {"passed": False, "details": ""},
            "billing_system": {"passed": False, "details": ""},
            "enhanced_dashboard": {"passed": False, "details": ""},
            "dish_management": {"passed": False, "details": ""},
            "order_management": {"passed": False, "details": ""}
        }
        
    def log(self, message):
        print(f"[TEST] {message}")
        
    def test_admin_authentication(self):
        """Test admin login with default credentials"""
        self.log("Testing Admin Authentication...")
        
        try:
            # Test admin login
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            
            response = self.session.post(f"{self.base_url}/admin/login", json=login_data)
            self.log(f"Admin login response: {response.status_code}")
            
            if response.status_code == 200:
                admin_data = response.json()
                self.log(f"Admin login successful: {admin_data}")
                
                # Verify response structure
                if "id" in admin_data and "username" in admin_data:
                    if admin_data["username"] == "admin":
                        self.test_results["admin_auth"]["passed"] = True
                        self.test_results["admin_auth"]["details"] = "Admin authentication working correctly"
                        self.log("✅ Admin authentication test PASSED")
                        return True
                    else:
                        self.test_results["admin_auth"]["details"] = f"Wrong username returned: {admin_data['username']}"
                else:
                    self.test_results["admin_auth"]["details"] = "Invalid response structure"
            else:
                self.test_results["admin_auth"]["details"] = f"Login failed with status {response.status_code}: {response.text}"
                
        except Exception as e:
            self.test_results["admin_auth"]["details"] = f"Exception during admin auth test: {str(e)}"
            
        self.log("❌ Admin authentication test FAILED")
        return False
        
    def test_room_management(self):
        """Test room CRUD operations including check-in/check-out"""
        self.log("Testing Room Management...")
        
        try:
            # Test GET /api/rooms - should return default rooms
            response = self.session.get(f"{self.base_url}/rooms")
            self.log(f"Get rooms response: {response.status_code}")
            
            if response.status_code != 200:
                self.test_results["room_management"]["details"] = f"Failed to get rooms: {response.status_code} - {response.text}"
                self.log("❌ Room management test FAILED - Cannot get rooms")
                return False
                
            rooms = response.json()
            self.log(f"Found {len(rooms)} rooms")
            
            # Verify default rooms exist
            room_numbers = [room["number"] for room in rooms]
            expected_single = ["201", "206", "207"]
            expected_double = ["101", "102", "103", "202", "203", "204", "205"]
            
            missing_rooms = []
            for room_num in expected_single + expected_double:
                if room_num not in room_numbers:
                    missing_rooms.append(room_num)
                    
            if missing_rooms:
                self.test_results["room_management"]["details"] = f"Missing default rooms: {missing_rooms}"
                self.log("❌ Room management test FAILED - Missing default rooms")
                return False
                
            # Test room check-in
            test_room = None
            for room in rooms:
                if room["status"] == "empty":
                    test_room = room
                    break
                    
            if not test_room:
                self.test_results["room_management"]["details"] = "No empty rooms available for check-in test"
                self.log("❌ Room management test FAILED - No empty rooms")
                return False
                
            # Test check-in
            checkin_data = {
                "guest_name": "Nguyen Van A",
                "check_in_date": datetime.now().isoformat(),
                "check_out_date": (datetime.now() + timedelta(days=2)).isoformat()
            }
            
            response = self.session.post(f"{self.base_url}/rooms/{test_room['id']}/checkin", json=checkin_data)
            self.log(f"Check-in response: {response.status_code}")
            
            if response.status_code != 200:
                self.test_results["room_management"]["details"] = f"Check-in failed: {response.status_code} - {response.text}"
                self.log("❌ Room management test FAILED - Check-in failed")
                return False
                
            checked_in_room = response.json()
            if checked_in_room["status"] != "occupied" or checked_in_room["guest_name"] != "Nguyen Van A":
                self.test_results["room_management"]["details"] = "Check-in did not update room status correctly"
                self.log("❌ Room management test FAILED - Check-in status incorrect")
                return False
                
            # Test check-out
            response = self.session.post(f"{self.base_url}/rooms/{test_room['id']}/checkout")
            self.log(f"Check-out response: {response.status_code}")
            
            if response.status_code != 200:
                self.test_results["room_management"]["details"] = f"Check-out failed: {response.status_code} - {response.text}"
                self.log("❌ Room management test FAILED - Check-out failed")
                return False
                
            checked_out_result = response.json()
            # The checkout now returns a complex object with room, bill, etc.
            if "room" not in checked_out_result:
                self.test_results["room_management"]["details"] = "Checkout response missing room data"
                self.log("❌ Room management test FAILED - Checkout response structure incorrect")
                return False
                
            checked_out_room = checked_out_result["room"]
            if checked_out_room["status"] != "empty" or checked_out_room["guest_name"] is not None:
                self.test_results["room_management"]["details"] = "Check-out did not update room status correctly"
                self.log("❌ Room management test FAILED - Check-out status incorrect")
                return False
                
            # Test room update - update status to maintenance and back
            update_data = {"status": "maintenance"}
            response = self.session.put(f"{self.base_url}/rooms/{test_room['id']}", json=update_data)
            self.log(f"Room update response: {response.status_code}")
            
            if response.status_code != 200:
                self.test_results["room_management"]["details"] = f"Room update failed: {response.status_code} - {response.text}"
                self.log("❌ Room management test FAILED - Room update failed")
                return False
                
            updated_room = response.json()
            if updated_room["status"] != "maintenance":
                self.test_results["room_management"]["details"] = "Room update did not change status correctly"
                self.log("❌ Room management test FAILED - Room update incorrect")
                return False
                
            # Reset room status back to empty
            reset_data = {"status": "empty"}
            self.session.put(f"{self.base_url}/rooms/{test_room['id']}", json=reset_data)
                
            self.test_results["room_management"]["passed"] = True
            self.test_results["room_management"]["details"] = "All room operations working correctly - CRUD, check-in, check-out"
            self.log("✅ Room management test PASSED")
            return True
            
        except Exception as e:
            self.test_results["room_management"]["details"] = f"Exception during room management test: {str(e)}"
            self.log("❌ Room management test FAILED - Exception occurred")
            return False
            
    def test_pricing_system(self):
        """Test pricing system with hourly/daily/monthly rates"""
        self.log("Testing Pricing System...")
        
        try:
            # Get rooms to test pricing structure
            response = self.session.get(f"{self.base_url}/rooms")
            if response.status_code != 200:
                self.test_results["pricing_system"]["details"] = f"Failed to get rooms: {response.status_code}"
                self.log("❌ Pricing system test FAILED - Cannot get rooms")
                return False
                
            rooms = response.json()
            test_room = None
            for room in rooms:
                if room["status"] == "empty":
                    test_room = room
                    break
                    
            if not test_room:
                self.test_results["pricing_system"]["details"] = "No empty rooms available for pricing test"
                self.log("❌ Pricing system test FAILED - No empty rooms")
                return False
                
            # Reset room to default pricing first
            default_pricing = {
                "hourly_first": 80000,
                "hourly_second": 40000, 
                "hourly_additional": 20000,
                "daily_rate": 500000,
                "monthly_rate": 12000000
            }
            
            reset_data = {"pricing": default_pricing}
            room_id = test_room['id']  # Store the room ID
            response = self.session.put(f"{self.base_url}/rooms/{room_id}", json=reset_data)
            if response.status_code != 200:
                self.test_results["pricing_system"]["details"] = "Failed to reset room pricing"
                self.log("❌ Pricing system test FAILED - Cannot reset pricing")
                return False
                
            # Get the updated room to verify default pricing
            response = self.session.get(f"{self.base_url}/rooms")
            if response.status_code != 200:
                self.test_results["pricing_system"]["details"] = "Failed to get rooms after reset"
                self.log("❌ Pricing system test FAILED - Cannot get rooms after reset")
                return False
                
            rooms = response.json()
            test_room = None
            for room in rooms:
                if room["id"] == room_id:
                    test_room = room
                    break
                
            # Verify default pricing structure
            pricing = test_room.get("pricing", {})
            expected_pricing = {
                "hourly_first": 80000,
                "hourly_second": 40000, 
                "hourly_additional": 20000,
                "daily_rate": 500000,
                "monthly_rate": 12000000
            }
            
            for key, expected_value in expected_pricing.items():
                if pricing.get(key) != expected_value:
                    self.test_results["pricing_system"]["details"] = f"Pricing structure incorrect: {key} = {pricing.get(key)}, expected {expected_value}"
                    self.log("❌ Pricing system test FAILED - Incorrect pricing structure")
                    return False
                    
            # Test updating room pricing
            new_pricing = {
                "hourly_first": 90000,
                "hourly_second": 45000,
                "hourly_additional": 25000,
                "daily_rate": 600000,
                "monthly_rate": 15000000
            }
            
            update_data = {"pricing": new_pricing}
            response = self.session.put(f"{self.base_url}/rooms/{room_id}", json=update_data)
            
            if response.status_code != 200:
                self.test_results["pricing_system"]["details"] = f"Failed to update room pricing: {response.status_code} - {response.text}"
                self.log("❌ Pricing system test FAILED - Cannot update pricing")
                return False
                
            updated_room = response.json()
            updated_pricing = updated_room.get("pricing", {})
            
            for key, expected_value in new_pricing.items():
                if updated_pricing.get(key) != expected_value:
                    self.test_results["pricing_system"]["details"] = f"Updated pricing incorrect: {key} = {updated_pricing.get(key)}, expected {expected_value}"
                    self.log("❌ Pricing system test FAILED - Pricing update failed")
                    return False
                    
            self.test_results["pricing_system"]["passed"] = True
            self.test_results["pricing_system"]["details"] = "Pricing system working correctly with hourly (80k/40k/20k), daily (500k), monthly (12M) rates"
            self.log("✅ Pricing system test PASSED")
            return True
            
        except Exception as e:
            self.test_results["pricing_system"]["details"] = f"Exception during pricing system test: {str(e)}"
            self.log("❌ Pricing system test FAILED - Exception occurred")
            return False
            
    def test_auto_cost_calculation(self):
        """Test auto cost calculation on checkout with different duration scenarios"""
        self.log("Testing Auto Cost Calculation on Checkout...")
        
        try:
            # Get an empty room for testing
            response = self.session.get(f"{self.base_url}/rooms")
            if response.status_code != 200:
                self.test_results["auto_cost_calculation"]["details"] = "Failed to get rooms"
                self.log("❌ Auto cost calculation test FAILED - Cannot get rooms")
                return False
                
            rooms = response.json()
            test_room = None
            for room in rooms:
                if room["status"] == "empty":
                    test_room = room
                    break
                    
            if not test_room:
                self.test_results["auto_cost_calculation"]["details"] = "No empty rooms available"
                self.log("❌ Auto cost calculation test FAILED - No empty rooms")
                return False
                
            # Test 1: Hourly calculation (check-in and immediate checkout)
            checkin_data = {
                "guest_name": "Tran Thi B",
                "check_in_date": datetime.now().isoformat(),
                "check_out_date": (datetime.now() + timedelta(hours=3)).isoformat()
            }
            
            # Check-in
            response = self.session.post(f"{self.base_url}/rooms/{test_room['id']}/checkin", json=checkin_data)
            if response.status_code != 200:
                self.test_results["auto_cost_calculation"]["details"] = f"Check-in failed: {response.status_code}"
                self.log("❌ Auto cost calculation test FAILED - Check-in failed")
                return False
                
            # Test current cost preview
            response = self.session.get(f"{self.base_url}/rooms/{test_room['id']}/current-cost")
            if response.status_code != 200:
                self.test_results["auto_cost_calculation"]["details"] = f"Current cost preview failed: {response.status_code}"
                self.log("❌ Auto cost calculation test FAILED - Current cost preview failed")
                return False
                
            current_cost = response.json()
            self.log(f"Current cost preview: {current_cost}")
            
            # Verify current cost structure
            required_fields = ["room_number", "guest_name", "check_in_time", "current_time", "total_cost", "duration_hours", "calculation_type"]
            for field in required_fields:
                if field not in current_cost:
                    self.test_results["auto_cost_calculation"]["details"] = f"Missing field in current cost: {field}"
                    self.log("❌ Auto cost calculation test FAILED - Missing current cost field")
                    return False
                    
            # Test checkout with cost calculation
            response = self.session.post(f"{self.base_url}/rooms/{test_room['id']}/checkout")
            if response.status_code != 200:
                self.test_results["auto_cost_calculation"]["details"] = f"Checkout failed: {response.status_code} - {response.text}"
                self.log("❌ Auto cost calculation test FAILED - Checkout failed")
                return False
                
            checkout_result = response.json()
            self.log(f"Checkout result: {checkout_result}")
            
            # Verify checkout response structure
            required_checkout_fields = ["room", "bill", "guest_name", "check_in_time", "check_out_time"]
            for field in required_checkout_fields:
                if field not in checkout_result:
                    self.test_results["auto_cost_calculation"]["details"] = f"Missing field in checkout: {field}"
                    self.log("❌ Auto cost calculation test FAILED - Missing checkout field")
                    return False
                    
            # Verify bill calculation
            bill = checkout_result["bill"]
            required_bill_fields = ["total_cost", "duration_hours", "calculation_type", "details"]
            for field in required_bill_fields:
                if field not in bill:
                    self.test_results["auto_cost_calculation"]["details"] = f"Missing field in bill: {field}"
                    self.log("❌ Auto cost calculation test FAILED - Missing bill field")
                    return False
                    
            # Verify cost calculation logic for short duration (should be hourly)
            if bill["calculation_type"] != "hourly":
                self.test_results["auto_cost_calculation"]["details"] = f"Expected hourly calculation, got: {bill['calculation_type']}"
                self.log("❌ Auto cost calculation test FAILED - Wrong calculation type")
                return False
                
            # For very short duration, should be first hour rate
            # Note: The room might have custom pricing from previous tests, so we check the room's pricing
            room_pricing = checkout_result["room"].get("pricing", {})
            expected_first_hour = room_pricing.get("hourly_first", 80000)
            
            if bill["duration_hours"] <= 1 and bill["total_cost"] != expected_first_hour:
                self.test_results["auto_cost_calculation"]["details"] = f"Expected {expected_first_hour} for first hour, got: {bill['total_cost']}"
                self.log("❌ Auto cost calculation test FAILED - Wrong hourly cost")
                return False
                
            self.test_results["auto_cost_calculation"]["passed"] = True
            self.test_results["auto_cost_calculation"]["details"] = "Auto cost calculation working correctly with real-time preview and detailed checkout bill"
            self.log("✅ Auto cost calculation test PASSED")
            return True
            
        except Exception as e:
            self.test_results["auto_cost_calculation"]["details"] = f"Exception during auto cost calculation test: {str(e)}"
            self.log("❌ Auto cost calculation test FAILED - Exception occurred")
            return False
            
    def test_billing_system(self):
        """Test billing records and history"""
        self.log("Testing Billing System...")
        
        try:
            # Test GET /api/bills
            response = self.session.get(f"{self.base_url}/bills")
            if response.status_code != 200:
                self.test_results["billing_system"]["details"] = f"Failed to get bills: {response.status_code} - {response.text}"
                self.log("❌ Billing system test FAILED - Cannot get bills")
                return False
                
            initial_bills = response.json()
            initial_count = len(initial_bills)
            self.log(f"Found {initial_count} existing bills")
            
            # Create a billing record by doing a check-in/checkout cycle
            response = self.session.get(f"{self.base_url}/rooms")
            if response.status_code != 200:
                self.test_results["billing_system"]["details"] = "Failed to get rooms for billing test"
                self.log("❌ Billing system test FAILED - Cannot get rooms")
                return False
                
            rooms = response.json()
            test_room = None
            for room in rooms:
                if room["status"] == "empty":
                    test_room = room
                    break
                    
            if not test_room:
                self.test_results["billing_system"]["details"] = "No empty rooms available for billing test"
                self.log("❌ Billing system test FAILED - No empty rooms")
                return False
                
            # Check-in
            checkin_data = {
                "guest_name": "Le Van C",
                "check_in_date": datetime.now().isoformat(),
                "check_out_date": (datetime.now() + timedelta(hours=2)).isoformat()
            }
            
            response = self.session.post(f"{self.base_url}/rooms/{test_room['id']}/checkin", json=checkin_data)
            if response.status_code != 200:
                self.test_results["billing_system"]["details"] = "Check-in failed for billing test"
                self.log("❌ Billing system test FAILED - Check-in failed")
                return False
                
            # Checkout (this should create a billing record)
            response = self.session.post(f"{self.base_url}/rooms/{test_room['id']}/checkout")
            if response.status_code != 200:
                self.test_results["billing_system"]["details"] = "Checkout failed for billing test"
                self.log("❌ Billing system test FAILED - Checkout failed")
                return False
                
            checkout_result = response.json()
            
            # Verify billing record was created
            response = self.session.get(f"{self.base_url}/bills")
            if response.status_code != 200:
                self.test_results["billing_system"]["details"] = "Failed to get bills after checkout"
                self.log("❌ Billing system test FAILED - Cannot get bills after checkout")
                return False
                
            final_bills = response.json()
            final_count = len(final_bills)
            
            if final_count != initial_count + 1:
                self.test_results["billing_system"]["details"] = f"Bill count didn't increase. Expected {initial_count + 1}, got {final_count}"
                self.log("❌ Billing system test FAILED - Bill not created")
                return False
                
            # Verify the latest bill structure
            latest_bill = final_bills[0]  # Bills are sorted by created_at desc
            required_bill_fields = ["id", "room_number", "guest_name", "check_in_time", "check_out_time", "cost_calculation", "created_at"]
            
            for field in required_bill_fields:
                if field not in latest_bill:
                    self.test_results["billing_system"]["details"] = f"Missing field in bill record: {field}"
                    self.log("❌ Billing system test FAILED - Missing bill field")
                    return False
                    
            # Verify bill data matches checkout
            if (latest_bill["guest_name"] != "Le Van C" or
                latest_bill["room_number"] != test_room["number"]):
                self.test_results["billing_system"]["details"] = "Bill data doesn't match checkout data"
                self.log("❌ Billing system test FAILED - Bill data mismatch")
                return False
                
            # Verify cost calculation in bill
            cost_calc = latest_bill["cost_calculation"]
            required_cost_fields = ["total_cost", "duration_hours", "calculation_type", "details"]
            for field in required_cost_fields:
                if field not in cost_calc:
                    self.test_results["billing_system"]["details"] = f"Missing cost calculation field: {field}"
                    self.log("❌ Billing system test FAILED - Missing cost calculation field")
                    return False
                    
            self.test_results["billing_system"]["passed"] = True
            self.test_results["billing_system"]["details"] = "Billing system working correctly with proper record creation and cost calculations"
            self.log("✅ Billing system test PASSED")
            return True
            
        except Exception as e:
            self.test_results["billing_system"]["details"] = f"Exception during billing system test: {str(e)}"
            self.log("❌ Billing system test FAILED - Exception occurred")
            return False
            
    def test_enhanced_dashboard(self):
        """Test enhanced dashboard with revenue tracking"""
        self.log("Testing Enhanced Dashboard with Revenue...")
        
        try:
            response = self.session.get(f"{self.base_url}/dashboard/stats")
            if response.status_code != 200:
                self.test_results["enhanced_dashboard"]["details"] = f"Failed to get dashboard stats: {response.status_code} - {response.text}"
                self.log("❌ Enhanced dashboard test FAILED - Cannot get stats")
                return False
                
            stats = response.json()
            self.log(f"Enhanced dashboard stats: {stats}")
            
            # Verify required fields including new revenue field
            required_fields = ["total_rooms", "occupied_rooms", "empty_rooms", "occupancy_rate", "today_orders", "today_revenue"]
            missing_fields = []
            
            for field in required_fields:
                if field not in stats:
                    missing_fields.append(field)
                    
            if missing_fields:
                self.test_results["enhanced_dashboard"]["details"] = f"Missing required fields: {missing_fields}"
                self.log("❌ Enhanced dashboard test FAILED - Missing fields")
                return False
                
            # Verify today_revenue field
            if not isinstance(stats["today_revenue"], (int, float)) or stats["today_revenue"] < 0:
                self.test_results["enhanced_dashboard"]["details"] = "today_revenue should be a non-negative number"
                self.log("❌ Enhanced dashboard test FAILED - Invalid today_revenue")
                return False
                
            # Verify other existing fields still work
            if not isinstance(stats["total_rooms"], int) or stats["total_rooms"] < 0:
                self.test_results["enhanced_dashboard"]["details"] = "total_rooms should be a non-negative integer"
                self.log("❌ Enhanced dashboard test FAILED - Invalid total_rooms")
                return False
                
            if not isinstance(stats["occupied_rooms"], int) or stats["occupied_rooms"] < 0:
                self.test_results["enhanced_dashboard"]["details"] = "occupied_rooms should be a non-negative integer"
                self.log("❌ Enhanced dashboard test FAILED - Invalid occupied_rooms")
                return False
                
            # Verify occupancy rate calculation
            if stats["total_rooms"] > 0:
                expected_rate = round((stats["occupied_rooms"] / stats["total_rooms"]) * 100, 1)
                if abs(stats["occupancy_rate"] - expected_rate) > 0.1:
                    self.test_results["enhanced_dashboard"]["details"] = f"Occupancy rate calculation incorrect. Expected: {expected_rate}, Got: {stats['occupancy_rate']}"
                    self.log("❌ Enhanced dashboard test FAILED - Occupancy rate calculation wrong")
                    return False
                    
            self.test_results["enhanced_dashboard"]["passed"] = True
            self.test_results["enhanced_dashboard"]["details"] = "Enhanced dashboard working correctly with today_revenue field and all existing stats"
            self.log("✅ Enhanced dashboard test PASSED")
            return True
            
        except Exception as e:
            self.test_results["enhanced_dashboard"]["details"] = f"Exception during enhanced dashboard test: {str(e)}"
            self.log("❌ Enhanced dashboard test FAILED - Exception occurred")
            return False
            
    def test_dish_management(self):
        """Test dish CRUD operations"""
        self.log("Testing Dish Management...")
        
        try:
            # Test GET /api/dishes
            response = self.session.get(f"{self.base_url}/dishes")
            self.log(f"Get dishes response: {response.status_code}")
            
            if response.status_code != 200:
                self.test_results["dish_management"]["details"] = f"Failed to get dishes: {response.status_code} - {response.text}"
                self.log("❌ Dish management test FAILED - Cannot get dishes")
                return False
                
            initial_dishes = response.json()
            self.log(f"Found {len(initial_dishes)} existing dishes")
            
            # Test POST /api/dishes - Create new dish
            dish_data = {
                "name": "Phở Bò Đặc Biệt",
                "price": 85000,
                "description": "Phở bò truyền thống với thịt bò tái, chín, gầu"
            }
            
            response = self.session.post(f"{self.base_url}/dishes", json=dish_data)
            self.log(f"Create dish response: {response.status_code}")
            
            if response.status_code != 200:
                self.test_results["dish_management"]["details"] = f"Failed to create dish: {response.status_code} - {response.text}"
                self.log("❌ Dish management test FAILED - Cannot create dish")
                return False
                
            created_dish = response.json()
            dish_id = created_dish["id"]
            
            # Verify dish creation
            if (created_dish["name"] != dish_data["name"] or 
                created_dish["price"] != dish_data["price"] or
                created_dish["description"] != dish_data["description"]):
                self.test_results["dish_management"]["details"] = "Created dish data doesn't match input"
                self.log("❌ Dish management test FAILED - Created dish data incorrect")
                return False
                
            # Test PUT /api/dishes/{dish_id} - Update dish
            update_data = {
                "name": "Phở Bò Đặc Biệt (Cập nhật)",
                "price": 90000,
                "description": "Phở bò truyền thống với thịt bò tái, chín, gầu - phiên bản cải tiến"
            }
            
            response = self.session.put(f"{self.base_url}/dishes/{dish_id}", json=update_data)
            self.log(f"Update dish response: {response.status_code}")
            
            if response.status_code != 200:
                self.test_results["dish_management"]["details"] = f"Failed to update dish: {response.status_code} - {response.text}"
                self.log("❌ Dish management test FAILED - Cannot update dish")
                return False
                
            updated_dish = response.json()
            if (updated_dish["name"] != update_data["name"] or 
                updated_dish["price"] != update_data["price"]):
                self.test_results["dish_management"]["details"] = "Updated dish data doesn't match input"
                self.log("❌ Dish management test FAILED - Updated dish data incorrect")
                return False
                
            # Test DELETE /api/dishes/{dish_id}
            response = self.session.delete(f"{self.base_url}/dishes/{dish_id}")
            self.log(f"Delete dish response: {response.status_code}")
            
            if response.status_code != 200:
                self.test_results["dish_management"]["details"] = f"Failed to delete dish: {response.status_code} - {response.text}"
                self.log("❌ Dish management test FAILED - Cannot delete dish")
                return False
                
            # Verify dish is deleted
            response = self.session.get(f"{self.base_url}/dishes")
            final_dishes = response.json()
            
            if len(final_dishes) != len(initial_dishes):
                self.test_results["dish_management"]["details"] = "Dish count after deletion doesn't match initial count"
                self.log("❌ Dish management test FAILED - Dish not properly deleted")
                return False
                
            self.test_results["dish_management"]["passed"] = True
            self.test_results["dish_management"]["details"] = "All dish CRUD operations working correctly"
            self.log("✅ Dish management test PASSED")
            return True
            
        except Exception as e:
            self.test_results["dish_management"]["details"] = f"Exception during dish management test: {str(e)}"
            self.log("❌ Dish management test FAILED - Exception occurred")
            return False
            
    def test_order_management(self):
        """Test order operations"""
        self.log("Testing Order Management...")
        
        try:
            # First create a dish to order
            dish_data = {
                "name": "Cơm Tấm Sườn Nướng",
                "price": 65000,
                "description": "Cơm tấm với sườn nướng, chả trứng, bì"
            }
            
            response = self.session.post(f"{self.base_url}/dishes", json=dish_data)
            if response.status_code != 200:
                self.test_results["order_management"]["details"] = "Failed to create test dish for order"
                self.log("❌ Order management test FAILED - Cannot create test dish")
                return False
                
            test_dish = response.json()
            dish_id = test_dish["id"]
            
            # Test GET /api/orders
            response = self.session.get(f"{self.base_url}/orders")
            self.log(f"Get orders response: {response.status_code}")
            
            if response.status_code != 200:
                self.test_results["order_management"]["details"] = f"Failed to get orders: {response.status_code} - {response.text}"
                self.log("❌ Order management test FAILED - Cannot get orders")
                return False
                
            initial_orders = response.json()
            self.log(f"Found {len(initial_orders)} existing orders")
            
            # Test POST /api/orders - Create order
            order_data = {
                "company_name": "Công ty TNHH ABC",
                "dish_id": dish_id,
                "quantity": 5
            }
            
            response = self.session.post(f"{self.base_url}/orders", json=order_data)
            self.log(f"Create order response: {response.status_code}")
            
            if response.status_code != 200:
                self.test_results["order_management"]["details"] = f"Failed to create order: {response.status_code} - {response.text}"
                self.log("❌ Order management test FAILED - Cannot create order")
                return False
                
            created_order = response.json()
            
            # Verify order creation
            expected_total = test_dish["price"] * order_data["quantity"]
            if (created_order["company_name"] != order_data["company_name"] or
                created_order["dish_id"] != dish_id or
                created_order["quantity"] != order_data["quantity"] or
                created_order["total_price"] != expected_total or
                created_order["dish_name"] != test_dish["name"]):
                self.test_results["order_management"]["details"] = "Created order data doesn't match expected values"
                self.log("❌ Order management test FAILED - Order data incorrect")
                return False
                
            # Verify order appears in list
            response = self.session.get(f"{self.base_url}/orders")
            final_orders = response.json()
            
            if len(final_orders) != len(initial_orders) + 1:
                self.test_results["order_management"]["details"] = "Order count didn't increase after creation"
                self.log("❌ Order management test FAILED - Order not added to list")
                return False
                
            # Clean up - delete test dish
            self.session.delete(f"{self.base_url}/dishes/{dish_id}")
            
            self.test_results["order_management"]["passed"] = True
            self.test_results["order_management"]["details"] = "Order creation and listing working correctly"
            self.log("✅ Order management test PASSED")
            return True
            
        except Exception as e:
            self.test_results["order_management"]["details"] = f"Exception during order management test: {str(e)}"
            self.log("❌ Order management test FAILED - Exception occurred")
            return False
            
    def run_all_tests(self):
        """Run all backend tests in priority order"""
        self.log("=" * 60)
        self.log("STARTING HOTEL MANAGEMENT BACKEND TESTS")
        self.log("=" * 60)
        
        # Test in priority order based on test_result.md
        tests = [
            ("Admin Authentication", self.test_admin_authentication),
            ("Room Management", self.test_room_management),
            ("Pricing System", self.test_pricing_system),
            ("Auto Cost Calculation", self.test_auto_cost_calculation),
            ("Billing System", self.test_billing_system),
            ("Enhanced Dashboard", self.test_enhanced_dashboard),
            ("Dish Management", self.test_dish_management),
            ("Order Management", self.test_order_management)
        ]
        
        passed_count = 0
        total_count = len(tests)
        
        for test_name, test_func in tests:
            self.log(f"\n--- {test_name} ---")
            if test_func():
                passed_count += 1
                
        self.log("\n" + "=" * 60)
        self.log("TEST SUMMARY")
        self.log("=" * 60)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASSED" if result["passed"] else "❌ FAILED"
            self.log(f"{test_name.upper()}: {status}")
            self.log(f"  Details: {result['details']}")
            
        self.log(f"\nOVERALL: {passed_count}/{total_count} tests passed")
        
        if passed_count == total_count:
            self.log("🎉 ALL BACKEND TESTS PASSED!")
            return True
        else:
            self.log("⚠️  SOME BACKEND TESTS FAILED")
            return False

if __name__ == "__main__":
    tester = HotelBackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)