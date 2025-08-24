import json
import os
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
import tempfile
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uuid

# Initialize FastAPI app
app = FastAPI(title="Hotel Management API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data storage in temporary files (for Vercel)
DATA_DIR = "/tmp"
ROOMS_FILE = os.path.join(DATA_DIR, "rooms.json")
GUESTS_FILE = os.path.join(DATA_DIR, "guests.json")
ORDERS_FILE = os.path.join(DATA_DIR, "orders.json")
BILLS_FILE = os.path.join(DATA_DIR, "bills.json")
DISHES_FILE = os.path.join(DATA_DIR, "dishes.json")

# Models
class RoomGuest(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    id_card: Optional[str] = None

class Room(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    number: str
    type: str  # "single" or "double"
    status: str = "empty"  # "empty" or "occupied"
    pricing: Dict[str, float] = Field(default_factory=lambda: {
        "hourly_first": 80000,
        "hourly_second": 40000,
        "hourly_additional": 20000,
        "daily_rate": 500000,
        "monthly_rate": 12000000
    })
    guest_name: Optional[str] = None
    company_name: Optional[str] = None
    guests: List[RoomGuest] = Field(default_factory=list)
    check_in_date: Optional[str] = None
    check_out_date: Optional[str] = None
    booking_type: Optional[str] = None
    booking_duration: Optional[int] = None
    total_cost: Optional[float] = None

class CheckInRequest(BaseModel):
    guest_name: str
    guest_phone: Optional[str] = None
    guest_id: Optional[str] = None
    booking_type: str = "hourly"
    duration: int = 1

class CompanyCheckInRequest(BaseModel):
    company_name: str
    guests: List[RoomGuest]
    booking_type: str = "hourly"
    duration: int = 1

class Dish(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    price: float
    description: Optional[str] = None
    status: str = "available"

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_name: str
    dish_id: str
    dish_name: str
    quantity: int
    unit_price: float
    total_price: float
    order_date: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "pending"

class OrderCreate(BaseModel):
    company_name: str
    dish_id: str
    quantity: int

# Utility functions
def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def load_json_file(file_path: str, default_data: Any = None):
    ensure_data_dir()
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    return default_data or []

def save_json_file(file_path: str, data: Any):
    ensure_data_dir()
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

def get_default_rooms():
    return [
        {
            "id": str(i),
            "number": str(200 + i),
            "type": "single" if i <= 10 else "double",
            "status": "empty",
            "pricing": {
                "hourly_first": 80000,
                "hourly_second": 40000,
                "hourly_additional": 20000,
                "daily_rate": 500000,
                "monthly_rate": 12000000
            }
        }
        for i in range(1, 21)
    ]

def get_default_dishes():
    return [
        {"id": "1", "name": "Phở bò", "price": 50000, "description": "Phở bò truyền thống", "status": "available"},
        {"id": "2", "name": "Cơm tấm", "price": 45000, "description": "Cơm tấm sườn nướng", "status": "available"},
        {"id": "3", "name": "Bánh mì", "price": 25000, "description": "Bánh mì thịt nguội", "status": "available"},
        {"id": "4", "name": "Bún chả", "price": 55000, "description": "Bún chả Hà Nội", "status": "available"},
        {"id": "5", "name": "Gỏi cuốn", "price": 35000, "description": "Gỏi cuốn tôm thịt", "status": "available"}
    ]

def calculate_cost(pricing: Dict[str, float], booking_type: str, duration: int):
    if booking_type == "hourly":
        if duration <= 1:
            return pricing.get("hourly_first", 80000)
        elif duration <= 2:
            return pricing.get("hourly_first", 80000) + pricing.get("hourly_second", 40000)
        else:
            return (pricing.get("hourly_first", 80000) + 
                   pricing.get("hourly_second", 40000) + 
                   (duration - 2) * pricing.get("hourly_additional", 20000))
    elif booking_type == "daily":
        return duration * pricing.get("daily_rate", 500000)
    else:  # monthly
        return duration * pricing.get("monthly_rate", 12000000)

# API Routes
@app.get("/")
def read_root():
    return {"message": "Hotel Management API", "status": "running"}

@app.get("/api/dashboard/stats")
def get_dashboard_stats():
    rooms = load_json_file(ROOMS_FILE, get_default_rooms())
    orders = load_json_file(ORDERS_FILE, [])
    bills = load_json_file(BILLS_FILE, [])
    
    occupied_rooms = len([r for r in rooms if r.get("status") == "occupied"])
    empty_rooms = len([r for r in rooms if r.get("status") == "empty"])
    total_revenue = sum(bill.get("cost_calculation", {}).get("total_cost", 0) for bill in bills)
    total_orders = len(orders)
    
    return {
        "total_rooms": len(rooms),
        "occupied_rooms": occupied_rooms,
        "empty_rooms": empty_rooms,
        "total_revenue": total_revenue,
        "total_orders": total_orders
    }

@app.get("/api/rooms")
def get_rooms():
    rooms = load_json_file(ROOMS_FILE, get_default_rooms())
    return rooms

@app.post("/api/rooms/{room_id}/checkin")
def checkin_room(room_id: str, request: CheckInRequest):
    rooms = load_json_file(ROOMS_FILE, get_default_rooms())
    
    # Find room
    room = None
    room_index = None
    for i, r in enumerate(rooms):
        if r["id"] == room_id:
            room = r
            room_index = i
            break
    
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if room["status"] != "empty":
        raise HTTPException(status_code=400, detail="Room is not available")
    
    # Calculate cost
    total_cost = calculate_cost(room["pricing"], request.booking_type, request.duration)
    
    # Update room
    now = datetime.now(timezone.utc)
    rooms[room_index].update({
        "status": "occupied",
        "guest_name": request.guest_name,
        "company_name": "Cá nhân",
        "guests": [{"name": request.guest_name, "phone": request.guest_phone, "email": "", "id_card": request.guest_id}],
        "booking_type": request.booking_type,
        "booking_duration": request.duration,
        "total_cost": total_cost,
        "check_in_date": now.isoformat(),
        "check_out_date": now.isoformat()
    })
    
    save_json_file(ROOMS_FILE, rooms)
    
    return {
        "message": "Check-in successful",
        "room_id": room_id,
        "total_cost": total_cost,
        "booking_type": request.booking_type,
        "duration": request.duration
    }

@app.post("/api/rooms/{room_id}/checkin-company")
def checkin_company(room_id: str, request: CompanyCheckInRequest):
    rooms = load_json_file(ROOMS_FILE, get_default_rooms())
    
    # Find room
    room = None
    room_index = None
    for i, r in enumerate(rooms):
        if r["id"] == room_id:
            room = r
            room_index = i
            break
    
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if room["status"] != "empty":
        raise HTTPException(status_code=400, detail="Room is not available")
    
    # Calculate cost
    total_cost = calculate_cost(room["pricing"], request.booking_type, request.duration)
    
    # Update room
    now = datetime.now(timezone.utc)
    rooms[room_index].update({
        "status": "occupied",
        "company_name": request.company_name,
        "guests": [guest.dict() for guest in request.guests],
        "booking_type": request.booking_type,
        "booking_duration": request.duration,
        "total_cost": total_cost,
        "check_in_date": now.isoformat(),
        "check_out_date": now.isoformat()
    })
    
    save_json_file(ROOMS_FILE, rooms)
    
    return {
        "message": "Check-in successful",
        "room_id": room_id,
        "total_cost": total_cost,
        "booking_type": request.booking_type,
        "duration": request.duration
    }

@app.post("/api/rooms/{room_id}/checkout")
def checkout_room(room_id: str):
    rooms = load_json_file(ROOMS_FILE, get_default_rooms())
    bills = load_json_file(BILLS_FILE, [])
    
    # Find room
    room = None
    room_index = None
    for i, r in enumerate(rooms):
        if r["id"] == room_id:
            room = r
            room_index = i
            break
    
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if room["status"] != "occupied":
        raise HTTPException(status_code=400, detail="Room is not occupied")
    
    # Calculate final cost
    booking_type = room.get("booking_type", "hourly")
    
    if booking_type in ["daily", "monthly"]:
        final_cost = room.get("total_cost", 0)
        details = f"Booking {booking_type}: {room.get('booking_duration', 1)} {booking_type}"
    else:
        # For hourly, calculate based on actual time if available
        final_cost = room.get("total_cost", 0)
        details = f"Hourly rate: {room.get('booking_duration', 1)} hours"
    
    # Create bill
    bill = {
        "id": str(len(bills) + 1),
        "room_number": room["number"],
        "guest_name": room.get("company_name") or room.get("guest_name", "Unknown"),
        "check_in_time": room.get("check_in_date"),
        "check_out_time": datetime.now(timezone.utc).isoformat(),
        "cost_calculation": {
            "total_cost": final_cost,
            "details": details,
            "calculation_type": booking_type
        }
    }
    
    bills.append(bill)
    save_json_file(BILLS_FILE, bills)
    
    # Reset room
    rooms[room_index].update({
        "status": "empty",
        "company_name": None,
        "guests": [],
        "guest_name": None,
        "booking_type": None,
        "booking_duration": None,
        "total_cost": None,
        "check_in_date": None,
        "check_out_date": None
    })
    
    save_json_file(ROOMS_FILE, rooms)
    
    return {
        "message": "Checkout successful",
        "bill": bill
    }

@app.get("/api/dishes")
def get_dishes():
    dishes = load_json_file(DISHES_FILE, get_default_dishes())
    return dishes

@app.post("/api/dishes")
def create_dish(dish: Dict[str, Any]):
    dishes = load_json_file(DISHES_FILE, get_default_dishes())
    
    new_dish = {
        "id": str(uuid.uuid4()),
        "name": dish["name"],
        "price": float(dish["price"]),
        "description": dish.get("description", ""),
        "status": "available"
    }
    
    dishes.append(new_dish)
    save_json_file(DISHES_FILE, dishes)
    
    return new_dish

@app.get("/api/orders")
def get_orders(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    company_name: Optional[str] = None,
    dish_name: Optional[str] = None,
    limit: int = 100
):
    orders = load_json_file(ORDERS_FILE, [])
    
    # Apply filters
    filtered_orders = orders
    
    if company_name:
        filtered_orders = [o for o in filtered_orders if company_name.lower() in o.get("company_name", "").lower()]
    
    if dish_name:
        filtered_orders = [o for o in filtered_orders if dish_name.lower() in o.get("dish_name", "").lower()]
    
    if start_date:
        filtered_orders = [o for o in filtered_orders if o.get("order_date", "") >= start_date]
    
    if end_date:
        filtered_orders = [o for o in filtered_orders if o.get("order_date", "") <= end_date]
    
    return filtered_orders[:limit]

@app.post("/api/orders")
def create_order(order: OrderCreate):
    orders = load_json_file(ORDERS_FILE, [])
    dishes = load_json_file(DISHES_FILE, get_default_dishes())
    
    # Find dish
    dish = next((d for d in dishes if d["id"] == order.dish_id), None)
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    
    new_order = {
        "id": str(uuid.uuid4()),
        "company_name": order.company_name,
        "dish_id": order.dish_id,
        "dish_name": dish["name"],
        "quantity": order.quantity,
        "unit_price": dish["price"],
        "total_price": dish["price"] * order.quantity,
        "order_date": datetime.now(timezone.utc).isoformat(),
        "status": "pending"
    }
    
    orders.append(new_order)
    save_json_file(ORDERS_FILE, orders)
    
    return new_order

@app.get("/api/orders/companies")
def get_companies():
    orders = load_json_file(ORDERS_FILE, [])
    companies = list(set(order.get("company_name", "") for order in orders if order.get("company_name")))
    return {"companies": sorted(companies)}

@app.get("/api/orders/dishes")
def get_order_dishes():
    orders = load_json_file(ORDERS_FILE, [])
    dishes = list(set(order.get("dish_name", "") for order in orders if order.get("dish_name")))
    return {"dishes": sorted(dishes)}

@app.get("/api/orders/company-summary")
def get_company_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    orders = load_json_file(ORDERS_FILE, [])
    
    # Apply date filters
    filtered_orders = orders
    if start_date:
        filtered_orders = [o for o in filtered_orders if o.get("order_date", "") >= start_date]
    if end_date:
        filtered_orders = [o for o in filtered_orders if o.get("order_date", "") <= end_date]
    
    # Group by company
    company_stats = {}
    for order in filtered_orders:
        company = order.get("company_name", "")
        if company not in company_stats:
            company_stats[company] = {
                "company_name": company,
                "total_orders": 0,
                "total_amount": 0,
                "unique_dishes": set()
            }
        
        company_stats[company]["total_orders"] += 1
        company_stats[company]["total_amount"] += order.get("total_price", 0)
        company_stats[company]["unique_dishes"].add(order.get("dish_name", ""))
    
    # Convert to list and add calculated fields
    companies = []
    for stats in company_stats.values():
        companies.append({
            "company_name": stats["company_name"],
            "total_orders": stats["total_orders"],
            "total_amount": stats["total_amount"],
            "average_order_value": stats["total_amount"] / stats["total_orders"] if stats["total_orders"] > 0 else 0,
            "unique_dishes_count": len(stats["unique_dishes"])
        })
    
    # Sort by total amount
    companies.sort(key=lambda x: x["total_amount"], reverse=True)
    
    return {
        "companies": companies,
        "total_companies": len(companies),
        "grand_total": sum(c["total_amount"] for c in companies)
    }

@app.get("/api/bills")
def get_bills():
    bills = load_json_file(BILLS_FILE, [])
    return bills

# Main handler for Vercel
def handler(request):
    return app(request)

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
