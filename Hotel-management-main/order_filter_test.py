#!/usr/bin/env python3
"""
Test script for order filtering and company reporting features
"""

import requests
import json
from datetime import datetime, timezone, timedelta

BASE_URL = "http://127.0.0.1:8001/api"

def test_order_filters():
    """Test order filtering functionality"""
    print("=== Testing Order Filters ===")
    
    try:
        # Test basic orders endpoint
        response = requests.get(f"{BASE_URL}/orders", timeout=5)
        if response.status_code != 200:
            print(f"❌ Failed to get orders: {response.status_code}")
            return False
        
        orders = response.json()
        print(f"✓ Total orders: {len(orders)}")
        
        # Test filter by company name
        if orders:
            # Get first company name for testing
            test_company = orders[0]["company_name"]
            response = requests.get(f"{BASE_URL}/orders?company_name={test_company}", timeout=5)
            if response.status_code == 200:
                filtered_orders = response.json()
                print(f"✓ Orders for '{test_company}': {len(filtered_orders)}")
            else:
                print(f"❌ Failed to filter by company: {response.status_code}")
        
        # Test filter by dish name
        if orders:
            # Get first dish name for testing
            test_dish = orders[0]["dish_name"]
            response = requests.get(f"{BASE_URL}/orders?dish_name={test_dish}", timeout=5)
            if response.status_code == 200:
                filtered_orders = response.json()
                print(f"✓ Orders for dish '{test_dish}': {len(filtered_orders)}")
            else:
                print(f"❌ Failed to filter by dish: {response.status_code}")
        
        # Test date filter
        today = datetime.now().strftime("%Y-%m-%d")
        response = requests.get(f"{BASE_URL}/orders?start_date={today}", timeout=5)
        if response.status_code == 200:
            today_orders = response.json()
            print(f"✓ Orders from today: {len(today_orders)}")
        else:
            print(f"❌ Failed to filter by date: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing order filters: {e}")
        return False

def test_company_reports():
    """Test company reporting functionality"""
    print("\n=== Testing Company Reports ===")
    
    try:
        # Test companies list
        response = requests.get(f"{BASE_URL}/orders/companies", timeout=5)
        if response.status_code != 200:
            print(f"❌ Failed to get companies: {response.status_code}")
            return False
        
        companies_data = response.json()
        companies = companies_data.get("companies", [])
        print(f"✓ Found {len(companies)} companies with orders")
        
        if companies:
            # Test company summary
            response = requests.get(f"{BASE_URL}/orders/company-summary", timeout=5)
            if response.status_code == 200:
                summary = response.json()
                print(f"✓ Company summary - Total companies: {summary.get('total_companies', 0)}")
                print(f"  Grand total revenue: {summary.get('grand_total', 0):,.0f} VND")
            else:
                print(f"❌ Failed to get company summary: {response.status_code}")
            
            # Test specific company report (daily)
            test_company = companies[0]
            response = requests.get(f"{BASE_URL}/orders/company-report?company_name={test_company}&group_by=daily", timeout=5)
            if response.status_code == 200:
                report = response.json()
                print(f"✓ Daily report for '{test_company}':")
                print(f"  Total orders: {report.get('summary', {}).get('total_orders', 0)}")
                print(f"  Total amount: {report.get('summary', {}).get('total_amount', 0):,.0f} VND")
                print(f"  Daily details: {len(report.get('details', []))} days")
            else:
                print(f"❌ Failed to get company daily report: {response.status_code}")
            
            # Test specific company report (monthly)
            response = requests.get(f"{BASE_URL}/orders/company-report?company_name={test_company}&group_by=monthly", timeout=5)
            if response.status_code == 200:
                report = response.json()
                print(f"✓ Monthly report for '{test_company}':")
                print(f"  Monthly details: {len(report.get('details', []))} months")
            else:
                print(f"❌ Failed to get company monthly report: {response.status_code}")
        
        # Test dishes list
        response = requests.get(f"{BASE_URL}/orders/dishes", timeout=5)
        if response.status_code == 200:
            dishes_data = response.json()
            dishes = dishes_data.get("dishes", [])
            print(f"✓ Found {len(dishes)} different dishes ordered")
        else:
            print(f"❌ Failed to get dishes list: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing company reports: {e}")
        return False

def create_sample_orders():
    """Create some sample orders for testing"""
    print("\n=== Creating Sample Orders ===")
    
    try:
        # Get available dishes
        response = requests.get(f"{BASE_URL}/dishes", timeout=5)
        if response.status_code != 200:
            print(f"❌ Failed to get dishes: {response.status_code}")
            return False
        
        dishes = response.json()
        if not dishes:
            print("❌ No dishes available")
            return False
        
        # Create sample orders
        sample_orders = [
            {"company_name": "Công ty ABC", "dish_id": dishes[0]["id"], "quantity": 2},
            {"company_name": "Công ty XYZ", "dish_id": dishes[0]["id"], "quantity": 1},
            {"company_name": "Công ty ABC", "dish_id": dishes[1]["id"] if len(dishes) > 1 else dishes[0]["id"], "quantity": 3},
            {"company_name": "Doanh nghiệp 123", "dish_id": dishes[0]["id"], "quantity": 1},
        ]
        
        created_count = 0
        for order_data in sample_orders:
            response = requests.post(f"{BASE_URL}/orders", json=order_data, timeout=5)
            if response.status_code == 200:
                created_count += 1
            else:
                print(f"❌ Failed to create order: {response.status_code}")
        
        print(f"✓ Created {created_count} sample orders")
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample orders: {e}")
        return False

if __name__ == "__main__":
    print("Testing Order Filtering and Company Reporting")
    print("=" * 50)
    
    # First create some sample data
    create_sample_orders()
    
    # Test filtering
    success1 = test_order_filters()
    
    # Test reporting
    success2 = test_company_reports()
    
    if success1 and success2:
        print("\n✅ All tests completed successfully!")
    else:
        print("\n❌ Some tests failed!")
