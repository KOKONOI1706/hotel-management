from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
from enum import Enum
from functools import wraps

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class RoomType(str, Enum):
    SINGLE = "single"
    DOUBLE = "double"

class RoomStatus(str, Enum):
    EMPTY = "empty"
    OCCUPIED = "occupied" 
    BOOKED = "booked"
    MAINTENANCE = "maintenance"

class MealStatus(str, Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"

# Models
class RoomGuest(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    id_card: Optional[str] = None

class PricingStructure(BaseModel):
    hourly_first: float = 80000  # First hour
    hourly_second: float = 40000  # Second hour  
    hourly_additional: float = 20000  # Third hour onwards
    daily_rate: float = 500000  # Daily rate (24 hours)
    monthly_rate: float = 12000000  # Monthly rate (30 days)

class Room(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    number: str
    type: RoomType
    status: RoomStatus = RoomStatus.EMPTY
    pricing: PricingStructure = Field(default_factory=PricingStructure)
    # Legacy field for backward compatibility
    guest_name: Optional[str] = None
    # New fields for company and multiple guests
    company_name: Optional[str] = None
    guests: List[RoomGuest] = Field(default_factory=list)
    check_in_date: Optional[datetime] = None
    check_out_date: Optional[datetime] = None
    total_cost: Optional[float] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RoomCreate(BaseModel):
    number: str
    type: RoomType
    pricing: Optional[PricingStructure] = Field(default_factory=PricingStructure)

class RoomUpdate(BaseModel):
    status: Optional[RoomStatus] = None
    pricing: Optional[PricingStructure] = None
    guest_name: Optional[str] = None
    company_name: Optional[str] = None
    guests: Optional[List[RoomGuest]] = None
    check_in_date: Optional[datetime] = None
    check_out_date: Optional[datetime] = None

class BookingType(str, Enum):
    HOURLY = "hourly"
    DAILY = "daily"
    MONTHLY = "monthly"

class CheckInCompany(BaseModel):
    company_name: str
    guests: List[RoomGuest]
    booking_type: BookingType = BookingType.HOURLY
    duration: int = 1  # số giờ/ngày/tháng
    check_in_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    check_out_date: Optional[datetime] = None

# Keep legacy CheckIn for backward compatibility
class CheckIn(BaseModel):
    guest_name: str  # Tên khách hàng
    guest_phone: Optional[str] = None
    guest_id: Optional[str] = None  # ID/CMND khách hàng
    booking_type: BookingType = BookingType.HOURLY
    duration: int = 1  # số giờ/ngày/tháng
    check_in_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    check_out_date: Optional[datetime] = None

class Dish(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    price: float
    status: MealStatus = MealStatus.AVAILABLE
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DishCreate(BaseModel):
    name: str
    price: float
    description: Optional[str] = None

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_name: str
    dish_id: str
    dish_name: str
    quantity: int
    unit_price: float
    total_price: float
    order_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "pending"  # pending, confirmed, delivered

class OrderCreate(BaseModel):
    company_name: str
    dish_id: str
    quantity: int

# Enhanced Admin with roles
class AdminRole(str, Enum):
    ADMIN = "admin"
    RECEPTIONIST = "receptionist"
    MANAGER = "manager"

# Permission decorator  
def require_permission(required_role: AdminRole):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # In real app, you would get current user from JWT token
            # For demo, we'll skip authentication check
            # current_admin = get_current_admin_from_token()
            # if current_admin.role != required_role and current_admin.role != AdminRole.ADMIN:
            #     raise HTTPException(status_code=403, detail="Insufficient permissions")
            return await func(*args, **kwargs)
        return wrapper
    return decorator

class Admin(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    password: str
    role: AdminRole = AdminRole.RECEPTIONIST
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AdminLogin(BaseModel):
    username: str
    password: str

class AdminResponse(BaseModel):
    id: str
    username: str
    role: AdminRole
class Guest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    id_card: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GuestCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    id_card: Optional[str] = None

class GuestUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    id_card: Optional[str] = None

# Reservation models
class ReservationStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    CHECKED_IN = "checked_in"

class Reservation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    room_id: str
    guest_id: str
    start_date: datetime
    end_date: datetime
    status: ReservationStatus = ReservationStatus.PENDING
    total_cost: Optional[float] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ReservationCreate(BaseModel):
    room_id: str
    guest_id: str
    start_date: datetime
    end_date: datetime

class ReservationUpdate(BaseModel):
    status: Optional[ReservationStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

# Enhanced Bill models
class BillStatus(str, Enum):
    UNPAID = "unpaid"
    PAID = "paid"
    REFUNDED = "refunded"

class BillItem(BaseModel):
    type: str  # "room", "service", "food"
    description: str
    quantity: int = 1
    unit_price: float
    total_price: float

class EnhancedBill(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    guest_id: str
    room_id: Optional[str] = None
    reservation_id: Optional[str] = None
    items: List[BillItem] = []
    subtotal: float = 0.0
    tax: float = 0.0
    total: float = 0.0
    status: BillStatus = BillStatus.UNPAID
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    paid_at: Optional[datetime] = None

# Helper functions
def calculate_room_cost(check_in_time: datetime, check_out_time: datetime, pricing: PricingStructure) -> dict:
    """Calculate total cost based on duration and pricing structure"""
    
    # Calculate duration
    duration = check_out_time - check_in_time
    total_hours = duration.total_seconds() / 3600
    total_days = duration.days
    
    # If stay is 30+ days, use monthly rate
    if total_days >= 30:
        months = total_days / 30
        total_cost = months * pricing.monthly_rate
        calculation_type = "monthly"
        details = f"{months:.1f} tháng x {pricing.monthly_rate:,.0f} VND"
    
    # If stay is 1+ full day, use daily rate  
    elif total_days >= 1:
        # Calculate full days + remaining hours
        remaining_hours = total_hours - (total_days * 24)
        
        daily_cost = total_days * pricing.daily_rate
        hourly_cost = 0
        
        # Calculate hourly cost for remaining hours
        if remaining_hours > 0:
            if remaining_hours <= 1:
                hourly_cost = pricing.hourly_first
            elif remaining_hours <= 2:
                hourly_cost = pricing.hourly_first + pricing.hourly_second
            else:
                hourly_cost = pricing.hourly_first + pricing.hourly_second + ((remaining_hours - 2) * pricing.hourly_additional)
        
        total_cost = daily_cost + hourly_cost
        calculation_type = "daily_hourly"
        details = f"{total_days} ngày x {pricing.daily_rate:,.0f} + {remaining_hours:.1f}h"
    
    # Use hourly rate
    else:
        if total_hours <= 1:
            total_cost = pricing.hourly_first
            details = f"1 giờ đầu: {pricing.hourly_first:,.0f} VND"
        elif total_hours <= 2:
            total_cost = pricing.hourly_first + pricing.hourly_second
            details = f"2 giờ: {pricing.hourly_first:,.0f} + {pricing.hourly_second:,.0f} VND"
        else:
            additional_hours = total_hours - 2
            additional_cost = additional_hours * pricing.hourly_additional
            total_cost = pricing.hourly_first + pricing.hourly_second + additional_cost
            details = f"2 giờ đầu + {additional_hours:.1f}h x {pricing.hourly_additional:,.0f} VND"
        
        calculation_type = "hourly"
    
    return {
        "total_cost": round(total_cost, 0),
        "duration_hours": round(total_hours, 2),
        "duration_days": total_days,
        "calculation_type": calculation_type,
        "details": details
    }
def prepare_for_mongo(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
    return data

def parse_from_mongo(item):
    if isinstance(item, dict):
        for key, value in item.items():
            if isinstance(value, str) and 'T' in value:  # ISO datetime string
                try:
                    item[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError:
                    pass
    return item

# Initialize default rooms and admin
@app.on_event("startup")
async def startup_event():
    # Create default admin if not exists
    admin_exists = await db.admins.find_one({"username": "admin"})
    if not admin_exists:
        admin = Admin(username="admin", password="admin123", role=AdminRole.ADMIN)
        admin_dict = prepare_for_mongo(admin.dict())
        await db.admins.insert_one(admin_dict)
        print("Default admin created: username=admin, password=admin123, role=admin")
    
    # Create default rooms if not exist
    room_count = await db.rooms.count_documents({})
    if room_count == 0:
        default_rooms = [
            # Single rooms
            {"number": "201", "type": "single"},
            {"number": "206", "type": "single"},
            {"number": "207", "type": "single"},
            # Double rooms  
            {"number": "101", "type": "double"},
            {"number": "102", "type": "double"},
            {"number": "103", "type": "double"},
            {"number": "202", "type": "double"},
            {"number": "203", "type": "double"},
            {"number": "204", "type": "double"},
            {"number": "205", "type": "double"},
        ]
        
        for room_data in default_rooms:
            room = Room(**room_data)
            room_dict = prepare_for_mongo(room.dict())
            await db.rooms.insert_one(room_dict)
        print("Default rooms created")
    
    # Auto-migrate old room data
    await migrate_old_room_data()

# Migration function
async def migrate_old_room_data():
    """Migrate old room data with guest_name to new structure with company_name and guests"""
    print("Starting room data migration...")
    
    # Find rooms with guest_name but no company_name (old structure)
    old_rooms = await db.rooms.find({
        "guest_name": {"$exists": True, "$ne": None},
        "company_name": {"$exists": False}
    }).to_list(length=None)
    
    migrated_count = 0
    for room in old_rooms:
        guest_name = room.get("guest_name")
        if guest_name:
            # Create guest from old guest_name
            guest = RoomGuest(
                name=guest_name,
                phone=None,
                email=None,
                id_card=None
            )
            
            # Update room with new structure
            update_data = {
                "company_name": "Cá nhân",
                "guests": [guest.dict()]
            }
            
            await db.rooms.update_one(
                {"id": room["id"]}, 
                {"$set": update_data}
            )
            migrated_count += 1
    
    if migrated_count > 0:
        print(f"Migrated {migrated_count} rooms from old structure to new structure")
    else:
        print("No rooms needed migration")

# Migration endpoint (manual trigger)
@api_router.post("/migrate/rooms")
async def manual_migrate_rooms():
    """Manually trigger room data migration"""
    await migrate_old_room_data()
    return {"message": "Room migration completed successfully"}

# Auth routes
@api_router.post("/admin/login", response_model=AdminResponse)
async def admin_login(login_data: AdminLogin):
    admin = await db.admins.find_one({"username": login_data.username, "password": login_data.password})
    if not admin:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return AdminResponse(id=admin["id"], username=admin["username"], role=admin.get("role", "receptionist"))

# Room routes
@api_router.get("/rooms", response_model=List[Room])
async def get_rooms():
    rooms = await db.rooms.find().to_list(length=None)
    return [Room(**parse_from_mongo(room)) for room in rooms]

@api_router.post("/rooms", response_model=Room)
async def create_room(room_data: RoomCreate):
    # Check if room number already exists
    existing = await db.rooms.find_one({"number": room_data.number})
    if existing:
        raise HTTPException(status_code=400, detail="Room number already exists")
    
    room = Room(**room_data.dict())
    room_dict = prepare_for_mongo(room.dict())
    await db.rooms.insert_one(room_dict)
    return room

@api_router.put("/rooms/{room_id}", response_model=Room)
async def update_room(room_id: str, room_data: RoomUpdate):
    existing = await db.rooms.find_one({"id": room_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Room not found")
    
    update_data = {k: v for k, v in room_data.dict().items() if v is not None}
    update_data = prepare_for_mongo(update_data)
    
    await db.rooms.update_one({"id": room_id}, {"$set": update_data})
    updated_room = await db.rooms.find_one({"id": room_id})
    return Room(**parse_from_mongo(updated_room))

@api_router.post("/rooms/{room_id}/checkin", response_model=Room)
async def check_in_room(room_id: str, checkin_data: CheckIn):
    """Legacy check-in endpoint for backward compatibility"""
    try:
        existing = await db.rooms.find_one({"id": room_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Room not found")
        
        if existing["status"] != "empty":
            raise HTTPException(status_code=400, detail="Room is not available")
        
        # Convert legacy CheckIn to new structure
        guest = RoomGuest(
            name=checkin_data.guest_name,
            phone=checkin_data.guest_phone,
            email=None,
            id_card=checkin_data.guest_id
        )
        
        company_checkin = CheckInCompany(
            company_name="Cá nhân",
            guests=[guest],
            booking_type=checkin_data.booking_type,
            duration=checkin_data.duration,
            check_in_date=checkin_data.check_in_date
        )
        
        return await process_company_checkin(room_id, company_checkin)
    
    except Exception as e:
        print(f"Error in check_in_room: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@api_router.post("/rooms/{room_id}/checkin-company", response_model=Room)
async def check_in_room_company(room_id: str, checkin_data: CheckInCompany):
    """New check-in endpoint for companies with multiple guests"""
    try:
        return await process_company_checkin(room_id, checkin_data)
    except Exception as e:
        print(f"Error in check_in_room_company: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

async def process_company_checkin(room_id: str, checkin_data: CheckInCompany):
    """Process check-in for company with multiple guests"""
    existing = await db.rooms.find_one({"id": room_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if existing["status"] != "empty":
        raise HTTPException(status_code=400, detail="Room is not available")
    
    # Validate at least one guest
    if not checkin_data.guests or len(checkin_data.guests) == 0:
        raise HTTPException(status_code=400, detail="At least one guest is required")
    
    # Calculate check-out time based on booking type and duration
    check_in_time = checkin_data.check_in_date
    
    if checkin_data.booking_type == BookingType.HOURLY:
        check_out_time = check_in_time + timedelta(hours=checkin_data.duration)
    elif checkin_data.booking_type == BookingType.DAILY:
        check_out_time = check_in_time + timedelta(days=checkin_data.duration)
    elif checkin_data.booking_type == BookingType.MONTHLY:
        check_out_time = check_in_time + timedelta(days=checkin_data.duration * 30)
    else:
        raise HTTPException(status_code=400, detail="Invalid booking type")
    
    # Calculate total cost based on booking type
    room_pricing = PricingStructure(**existing.get("pricing", {}))
    
    if checkin_data.booking_type == BookingType.HOURLY:
        if checkin_data.duration <= 1:
            total_cost = room_pricing.hourly_first
        elif checkin_data.duration <= 2:
            total_cost = room_pricing.hourly_first + room_pricing.hourly_second
        else:
            total_cost = room_pricing.hourly_first + room_pricing.hourly_second + ((checkin_data.duration - 2) * room_pricing.hourly_additional)
    elif checkin_data.booking_type == BookingType.DAILY:
        total_cost = room_pricing.daily_rate * checkin_data.duration
    elif checkin_data.booking_type == BookingType.MONTHLY:
        total_cost = room_pricing.monthly_rate * checkin_data.duration
    
    # Convert guests to dict for MongoDB
    guests_dict = [guest.dict() for guest in checkin_data.guests]
    
    update_data = {
        "status": "occupied",
        "company_name": checkin_data.company_name,
        "guests": guests_dict,
        # Keep guest_name for backward compatibility (use first guest's name)
        "guest_name": checkin_data.guests[0].name,
        "check_in_date": check_in_time.isoformat(),
        "check_out_date": check_out_time.isoformat(),
        "total_cost": total_cost,
        "booking_type": checkin_data.booking_type.value,  # Store booking type for later reference
        "booking_duration": checkin_data.duration
    }
    
    await db.rooms.update_one({"id": room_id}, {"$set": update_data})
    updated_room = await db.rooms.find_one({"id": room_id})
    return Room(**parse_from_mongo(updated_room))

@api_router.post("/rooms/{room_id}/checkout")
async def check_out_room(room_id: str):
    existing = await db.rooms.find_one({"id": room_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if existing["status"] != "occupied":
        raise HTTPException(status_code=400, detail="Room is not occupied")
    
    # Get booking type to determine how to calculate cost
    booking_type = existing.get("booking_type", "hourly")  # Default to hourly for older records
    original_total_cost = existing.get("total_cost")  # Pre-calculated cost from check-in
    
    # Calculate total cost
    check_in_date_str = existing["check_in_date"]
    if isinstance(check_in_date_str, str):
        # Handle both timezone-aware and naive datetime strings
        if check_in_date_str.endswith('Z'):
            check_in_time = datetime.fromisoformat(check_in_date_str.replace('Z', '+00:00'))
        elif '+' in check_in_date_str or check_in_date_str.endswith('+00:00'):
            check_in_time = datetime.fromisoformat(check_in_date_str)
        else:
            # Assume UTC if no timezone info
            check_in_time = datetime.fromisoformat(check_in_date_str).replace(tzinfo=timezone.utc)
    else:
        check_in_time = check_in_date_str
        if check_in_time.tzinfo is None:
            check_in_time = check_in_time.replace(tzinfo=timezone.utc)
    
    check_out_time = datetime.now(timezone.utc)
    
    # Get pricing from room or use default
    pricing_data = existing.get("pricing", {})
    pricing = PricingStructure(**pricing_data) if pricing_data else PricingStructure()
    
    # Determine final cost based on booking type
    if booking_type == "hourly":
        # For hourly bookings, calculate based on actual time spent
        cost_calculation = calculate_room_cost(check_in_time, check_out_time, pricing)
        calculation_method = "actual_time_hourly"
    elif booking_type in ["daily", "monthly"]:
        # For daily/monthly bookings, use the pre-calculated cost regardless of early checkout
        if original_total_cost is not None:
            # Use the original cost that was calculated during check-in
            duration = check_out_time - check_in_time
            actual_hours = duration.total_seconds() / 3600
            actual_days = duration.days
            
            cost_calculation = {
                "total_cost": original_total_cost,
                "duration_hours": round(actual_hours, 2),
                "duration_days": actual_days,
                "calculation_type": f"fixed_{booking_type}",
                "details": f"Chi phí cố định ({booking_type}) - Đã thanh toán trước: {original_total_cost:,.0f} VND"
            }
            calculation_method = f"pre_paid_{booking_type}"
        else:
            # Fallback: calculate based on actual time if no original cost found
            cost_calculation = calculate_room_cost(check_in_time, check_out_time, pricing)
            calculation_method = "fallback_calculation"
    else:
        # Unknown booking type, default to time-based calculation
        cost_calculation = calculate_room_cost(check_in_time, check_out_time, pricing)
        calculation_method = "default_calculation"
    
    # Get company and guest info
    company_name = existing.get("company_name", "Cá nhân")
    guests = existing.get("guests", [])
    
    # Fallback to legacy guest_name if no guests
    if not guests and existing.get("guest_name"):
        guests = [{"name": existing["guest_name"], "phone": None, "email": None, "id_card": None}]
    
    update_data = {
        "status": "empty",
        "company_name": None,
        "guests": [],
        "guest_name": None,
        "check_in_date": None,
        "check_out_date": None,
        "total_cost": None,
        "booking_type": None,  # Clear booking type
        "booking_duration": None  # Clear booking duration
    }
    
    await db.rooms.update_one({"id": room_id}, {"$set": update_data})
    
    # Save billing record with company and guests info
    bill_record = {
        "id": str(uuid.uuid4()),
        "room_number": existing["number"],
        "company_name": company_name,
        "guests": guests,
        "guest_name": existing.get("guest_name"),  # Keep for backward compatibility
        "booking_type": booking_type,  # Save original booking type
        "original_total_cost": original_total_cost,  # Save original cost
        "calculation_method": calculation_method,  # How the final cost was calculated
        "check_in_time": check_in_time.isoformat(),
        "check_out_time": check_out_time.isoformat(),
        "cost_calculation": cost_calculation,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.bills.insert_one(bill_record)
    
    # Also save to enhanced_bills
    enhanced_bill = EnhancedBill(
        guest_id=guests[0]["name"] if guests else "Unknown",
        room_id=room_id,
        items=[BillItem(
            type="room",
            description=f"Phòng {existing['number']} - {cost_calculation['details']} (Booking: {booking_type})",
            quantity=1,
            unit_price=cost_calculation["total_cost"],
            total_price=cost_calculation["total_cost"]
        )],
        subtotal=cost_calculation["total_cost"],
        total=cost_calculation["total_cost"],
        status=BillStatus.UNPAID
    )
    
    enhanced_bill_dict = prepare_for_mongo(enhanced_bill.dict())
    await db.enhanced_bills.insert_one(enhanced_bill_dict)
    
    updated_room = await db.rooms.find_one({"id": room_id})
    
    return {
        "room": Room(**parse_from_mongo(updated_room)),
        "bill": cost_calculation,
        "booking_type": booking_type,
        "original_total_cost": original_total_cost,
        "calculation_method": calculation_method,
        "company_name": company_name,
        "guests": guests,
        "guest_name": existing.get("guest_name"),  # Legacy field
        "check_in_time": check_in_time.isoformat(),
        "check_out_time": check_out_time.isoformat()
    }

@api_router.delete("/rooms/{room_id}")
async def delete_room(room_id: str):
    result = await db.rooms.delete_one({"id": room_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Room not found")
    return {"message": "Room deleted successfully"}

# Guest routes
@api_router.get("/guests", response_model=List[Guest])
async def get_guests():
    guests = await db.guests.find().sort("created_at", -1).to_list(length=None)
    return [Guest(**parse_from_mongo(guest)) for guest in guests]

@api_router.post("/guests", response_model=Guest)
async def create_guest(guest_data: GuestCreate):
    guest = Guest(**guest_data.dict())
    guest_dict = prepare_for_mongo(guest.dict())
    await db.guests.insert_one(guest_dict)
    return guest

@api_router.get("/guests/{guest_id}", response_model=Guest)
async def get_guest(guest_id: str):
    guest = await db.guests.find_one({"id": guest_id})
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    return Guest(**parse_from_mongo(guest))

@api_router.put("/guests/{guest_id}", response_model=Guest)
async def update_guest(guest_id: str, guest_data: GuestUpdate):
    existing = await db.guests.find_one({"id": guest_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Guest not found")
    
    update_data = {k: v for k, v in guest_data.dict().items() if v is not None}
    update_data = prepare_for_mongo(update_data)
    
    await db.guests.update_one({"id": guest_id}, {"$set": update_data})
    updated_guest = await db.guests.find_one({"id": guest_id})
    return Guest(**parse_from_mongo(updated_guest))

@api_router.delete("/guests/{guest_id}")
async def delete_guest(guest_id: str):
    result = await db.guests.delete_one({"id": guest_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Guest not found")
    return {"message": "Guest deleted successfully"}

# Reservation routes
@api_router.get("/reservations", response_model=List[Reservation])
async def get_reservations():
    reservations = await db.reservations.find().sort("created_at", -1).to_list(length=None)
    return [Reservation(**parse_from_mongo(reservation)) for reservation in reservations]

@api_router.post("/reservations", response_model=Reservation)
async def create_reservation(reservation_data: ReservationCreate):
    # Check if room exists
    room = await db.rooms.find_one({"id": reservation_data.room_id})
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Check if guest exists
    guest = await db.guests.find_one({"id": reservation_data.guest_id})
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    
    # Check room availability for the date range
    existing_reservations = await db.reservations.find({
        "room_id": reservation_data.room_id,
        "status": {"$in": ["confirmed", "checked_in"]},
        "$or": [
            {"start_date": {"$lte": reservation_data.end_date.isoformat()}, 
             "end_date": {"$gte": reservation_data.start_date.isoformat()}}
        ]
    }).to_list(length=None)
    
    if existing_reservations:
        raise HTTPException(status_code=400, detail="Room is not available for the selected dates")
    
    # Calculate total cost
    duration = reservation_data.end_date - reservation_data.start_date
    days = duration.days
    room_pricing = PricingStructure(**room.get("pricing", {}))
    total_cost = room_pricing.daily_rate * days
    
    reservation = Reservation(**reservation_data.dict(), total_cost=total_cost)
    reservation_dict = prepare_for_mongo(reservation.dict())
    await db.reservations.insert_one(reservation_dict)
    return reservation

@api_router.put("/reservations/{reservation_id}", response_model=Reservation)
async def update_reservation(reservation_id: str, reservation_data: ReservationUpdate):
    existing = await db.reservations.find_one({"id": reservation_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    update_data = {k: v for k, v in reservation_data.dict().items() if v is not None}
    update_data = prepare_for_mongo(update_data)
    
    await db.reservations.update_one({"id": reservation_id}, {"$set": update_data})
    updated_reservation = await db.reservations.find_one({"id": reservation_id})
    return Reservation(**parse_from_mongo(updated_reservation))

@api_router.post("/reservations/{reservation_id}/checkin")
async def checkin_from_reservation(reservation_id: str):
    reservation = await db.reservations.find_one({"id": reservation_id})
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    if reservation["status"] != "confirmed":
        raise HTTPException(status_code=400, detail="Reservation is not confirmed")
    
    # Check if current date is within reservation period
    current_date = datetime.now(timezone.utc)
    start_date = datetime.fromisoformat(reservation["start_date"].replace('Z', '+00:00'))
    
    if current_date < start_date:
        raise HTTPException(status_code=400, detail="Cannot check-in before reservation start date")
    
    # Update room status
    await db.rooms.update_one(
        {"id": reservation["room_id"]}, 
        {"$set": {"status": "occupied", "guest_name": reservation["guest_id"]}}
    )
    
    # Update reservation status
    await db.reservations.update_one(
        {"id": reservation_id}, 
        {"$set": {"status": "checked_in"}}
    )
    
    return {"message": "Checked in successfully"}

# Dish routes
@api_router.get("/dishes", response_model=List[Dish])
async def get_dishes():
    dishes = await db.dishes.find().to_list(length=None)
    return [Dish(**parse_from_mongo(dish)) for dish in dishes]

@api_router.post("/dishes", response_model=Dish)
async def create_dish(dish_data: DishCreate):
    dish = Dish(**dish_data.dict())
    dish_dict = prepare_for_mongo(dish.dict())
    await db.dishes.insert_one(dish_dict)
    return dish

@api_router.put("/dishes/{dish_id}", response_model=Dish)
async def update_dish(dish_id: str, dish_data: DishCreate):
    existing = await db.dishes.find_one({"id": dish_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Dish not found")
    
    update_data = prepare_for_mongo(dish_data.dict())
    await db.dishes.update_one({"id": dish_id}, {"$set": update_data})
    updated_dish = await db.dishes.find_one({"id": dish_id})
    return Dish(**parse_from_mongo(updated_dish))

@api_router.delete("/dishes/{dish_id}")
async def delete_dish(dish_id: str):
    result = await db.dishes.delete_one({"id": dish_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Dish not found")
    return {"message": "Dish deleted successfully"}

# Order routes
@api_router.get("/orders", response_model=List[Order])
async def get_orders(
    start_date: str = None,
    end_date: str = None,
    company_name: str = None,
    dish_name: str = None,
    limit: int = 100
):
    """Get orders with optional filters"""
    # Build filter query
    filter_query = {}
    
    # Date filter
    if start_date or end_date:
        date_filter = {}
        if start_date:
            date_filter["$gte"] = start_date
        if end_date:
            date_filter["$lte"] = end_date
        filter_query["order_date"] = date_filter
    
    # Company name filter (case-insensitive partial match)
    if company_name:
        filter_query["company_name"] = {"$regex": company_name, "$options": "i"}
    
    # Dish name filter (case-insensitive partial match)
    if dish_name:
        filter_query["dish_name"] = {"$regex": dish_name, "$options": "i"}
    
    orders = await db.orders.find(filter_query).sort("order_date", -1).limit(limit).to_list(length=None)
    return [Order(**parse_from_mongo(order)) for order in orders]

@api_router.get("/orders/company-report")
async def get_company_order_report(
    company_name: str,
    start_date: str = None,
    end_date: str = None,
    group_by: str = "daily"  # daily, monthly
):
    """Get order report for a specific company with daily/monthly totals"""
    
    # Build date filter
    date_filter = {}
    if start_date:
        date_filter["$gte"] = start_date
    if end_date:
        date_filter["$lte"] = end_date
    
    # Base match stage
    match_stage = {
        "company_name": {"$regex": company_name, "$options": "i"}
    }
    if date_filter:
        match_stage["order_date"] = date_filter
    
    # Group by date format
    if group_by == "monthly":
        date_format = "%Y-%m"
        group_label = "month"
    else:  # daily
        date_format = "%Y-%m-%d"
        group_label = "day"
    
    # Aggregation pipeline
    pipeline = [
        {"$match": match_stage},
        {
            "$group": {
                "_id": {
                    "date": {"$dateToString": {"format": date_format, "date": {"$dateFromString": {"dateString": "$order_date"}}}},
                    "company": "$company_name"
                },
                "total_orders": {"$sum": 1},
                "total_amount": {"$sum": "$total_price"},
                "orders": {
                    "$push": {
                        "dish_name": "$dish_name",
                        "quantity": "$quantity",
                        "unit_price": "$unit_price",
                        "total_price": "$total_price",
                        "order_date": "$order_date"
                    }
                }
            }
        },
        {"$sort": {"_id.date": -1}}
    ]
    
    results = await db.orders.aggregate(pipeline).to_list(length=None)
    
    # Calculate overall totals
    total_orders = sum(result["total_orders"] for result in results)
    total_amount = sum(result["total_amount"] for result in results)
    
    # Format results
    formatted_results = []
    for result in results:
        formatted_results.append({
            "date": result["_id"]["date"],
            "company_name": result["_id"]["company"],
            "total_orders": result["total_orders"],
            "total_amount": result["total_amount"],
            "orders": result["orders"]
        })
    
    return {
        "company_name": company_name,
        "period": group_by,
        "date_range": {
            "start_date": start_date,
            "end_date": end_date
        },
        "summary": {
            "total_orders": total_orders,
            "total_amount": total_amount,
            "average_order_value": round(total_amount / total_orders, 2) if total_orders > 0 else 0
        },
        "details": formatted_results
    }

@api_router.get("/orders/company-summary")
async def get_companies_order_summary(
    start_date: str = None,
    end_date: str = None
):
    """Get order summary for all companies"""
    
    # Build date filter
    date_filter = {}
    if start_date:
        date_filter["$gte"] = start_date
    if end_date:
        date_filter["$lte"] = end_date
    
    match_stage = {}
    if date_filter:
        match_stage["order_date"] = date_filter
    
    # Aggregation pipeline
    pipeline = [
        {"$match": match_stage} if match_stage else {"$match": {}},
        {
            "$group": {
                "_id": "$company_name",
                "total_orders": {"$sum": 1},
                "total_amount": {"$sum": "$total_price"},
                "unique_dishes": {"$addToSet": "$dish_name"},
                "last_order_date": {"$max": "$order_date"}
            }
        },
        {"$sort": {"total_amount": -1}}
    ]
    
    results = await db.orders.aggregate(pipeline).to_list(length=None)
    
    # Format results
    formatted_results = []
    for result in results:
        formatted_results.append({
            "company_name": result["_id"],
            "total_orders": result["total_orders"],
            "total_amount": result["total_amount"],
            "unique_dishes_count": len(result["unique_dishes"]),
            "unique_dishes": result["unique_dishes"],
            "last_order_date": result["last_order_date"],
            "average_order_value": round(result["total_amount"] / result["total_orders"], 2) if result["total_orders"] > 0 else 0
        })
    
    return {
        "date_range": {
            "start_date": start_date,
            "end_date": end_date
        },
        "companies": formatted_results,
        "total_companies": len(formatted_results),
        "grand_total": sum(company["total_amount"] for company in formatted_results)
    }

@api_router.post("/orders", response_model=Order)
async def create_order(order_data: OrderCreate):
    # Get dish info
    dish = await db.dishes.find_one({"id": order_data.dish_id})
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    
    total_price = dish["price"] * order_data.quantity
    
    order = Order(
        company_name=order_data.company_name,
        dish_id=order_data.dish_id,
        dish_name=dish["name"],
        quantity=order_data.quantity,
        unit_price=dish["price"],
        total_price=total_price
    )
    
    order_dict = prepare_for_mongo(order.dict())
    await db.orders.insert_one(order_dict)
    return order
async def create_order(order_data: OrderCreate):
    # Get dish info
    dish = await db.dishes.find_one({"id": order_data.dish_id})
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    
    total_price = dish["price"] * order_data.quantity
    
    order = Order(
        company_name=order_data.company_name,
        dish_id=order_data.dish_id,
        dish_name=dish["name"],
        quantity=order_data.quantity,
        unit_price=dish["price"],
        total_price=total_price
    )
    
    order_dict = prepare_for_mongo(order.dict())
    await db.orders.insert_one(order_dict)
    return order

@api_router.get("/orders/companies")
async def get_order_companies():
    """Get list of all companies that have placed orders"""
    pipeline = [
        {"$group": {"_id": "$company_name"}},
        {"$sort": {"_id": 1}}
    ]
    
    results = await db.orders.aggregate(pipeline).to_list(length=None)
    companies = [result["_id"] for result in results if result["_id"]]
    
    return {"companies": companies}

@api_router.get("/orders/dishes")
async def get_order_dishes():
    """Get list of all dishes that have been ordered"""
    pipeline = [
        {"$group": {"_id": "$dish_name"}},
        {"$sort": {"_id": 1}}
    ]
    
    results = await db.orders.aggregate(pipeline).to_list(length=None)
    dishes = [result["_id"] for result in results if result["_id"]]
    
    return {"dishes": dishes}

# Billing routes
@api_router.get("/bills")
async def get_bills():
    bills = await db.bills.find().sort("created_at", -1).to_list(length=50)
    # Remove MongoDB _id field to avoid serialization issues
    for bill in bills:
        if "_id" in bill:
            del bill["_id"]
    return bills

# Enhanced Billing routes
@api_router.get("/enhanced-bills", response_model=List[EnhancedBill])
async def get_enhanced_bills():
    bills = await db.enhanced_bills.find().sort("created_at", -1).to_list(length=50)
    return [EnhancedBill(**parse_from_mongo(bill)) for bill in bills]

@api_router.post("/enhanced-bills", response_model=EnhancedBill)
async def create_enhanced_bill(bill_data: dict):
    # Create a new enhanced bill
    bill = EnhancedBill(**bill_data)
    bill_dict = prepare_for_mongo(bill.dict())
    await db.enhanced_bills.insert_one(bill_dict)
    return bill

@api_router.put("/enhanced-bills/{bill_id}/payment")
async def update_bill_payment_status(bill_id: str, status: BillStatus):
    existing = await db.enhanced_bills.find_one({"id": bill_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Bill not found")
    
    update_data = {"status": status}
    if status == BillStatus.PAID:
        update_data["paid_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.enhanced_bills.update_one({"id": bill_id}, {"$set": update_data})
    updated_bill = await db.enhanced_bills.find_one({"id": bill_id})
    return EnhancedBill(**parse_from_mongo(updated_bill))

# PDF Generation route (temporarily disabled due to reportlab dependency)
@api_router.get("/bills/{bill_id}/pdf")
async def generate_bill_pdf(bill_id: str):
    # TODO: Install reportlab package for PDF generation
    raise HTTPException(status_code=501, detail="PDF generation temporarily disabled")

# Reports routes
@api_router.get("/reports/revenue")
async def get_revenue_report(period: str = "daily", start_date: str = None, end_date: str = None):
    """
    Get revenue report by period (daily, weekly, monthly)
    """
    if not start_date:
        start_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        start_date = datetime.fromisoformat(start_date)
    
    if not end_date:
        end_date = datetime.now(timezone.utc)
    else:
        end_date = datetime.fromisoformat(end_date)
    
    # Get bills in date range
    bills = await db.bills.find({
        "created_at": {
            "$gte": start_date.isoformat(),
            "$lte": end_date.isoformat()
        }
    }).to_list(length=None)
    
    total_revenue = sum([bill.get("cost_calculation", {}).get("total_cost", 0) for bill in bills])
    
    # Group by period
    revenue_by_period = {}
    for bill in bills:
        bill_date = datetime.fromisoformat(bill["created_at"])
        
        if period == "daily":
            key = bill_date.strftime("%Y-%m-%d")
        elif period == "weekly":
            key = f"{bill_date.year}-W{bill_date.isocalendar()[1]}"
        elif period == "monthly":
            key = bill_date.strftime("%Y-%m")
        else:
            key = bill_date.strftime("%Y-%m-%d")
        
        if key not in revenue_by_period:
            revenue_by_period[key] = 0
        revenue_by_period[key] += bill.get("cost_calculation", {}).get("total_cost", 0)
    
    return {
        "period": period,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "total_revenue": total_revenue,
        "revenue_by_period": revenue_by_period
    }

@api_router.get("/reports/popular-dishes")
async def get_popular_dishes_report(limit: int = 10):
    """
    Get most popular dishes by order quantity
    """
    pipeline = [
        {
            "$group": {
                "_id": "$dish_id",
                "dish_name": {"$first": "$dish_name"},
                "total_quantity": {"$sum": "$quantity"},
                "total_revenue": {"$sum": "$total_price"},
                "order_count": {"$sum": 1}
            }
        },
        {"$sort": {"total_quantity": -1}},
        {"$limit": limit}
    ]
    
    popular_dishes = await db.orders.aggregate(pipeline).to_list(length=limit)
    
    return {
        "popular_dishes": popular_dishes
    }

@api_router.get("/reports/room-occupancy")
async def get_room_occupancy_report():
    """
    Get room occupancy rate by room type
    """
    # Get all rooms grouped by type
    pipeline = [
        {
            "$group": {
                "_id": "$type",
                "total_rooms": {"$sum": 1},
                "occupied_rooms": {
                    "$sum": {
                        "$cond": [{"$eq": ["$status", "occupied"]}, 1, 0]
                    }
                },
                "empty_rooms": {
                    "$sum": {
                        "$cond": [{"$eq": ["$status", "empty"]}, 1, 0]
                    }
                }
            }
        }
    ]
    
    occupancy_data = await db.rooms.aggregate(pipeline).to_list(length=None)
    
    # Calculate occupancy rates
    for item in occupancy_data:
        item["occupancy_rate"] = round((item["occupied_rooms"] / item["total_rooms"]) * 100, 1)
    
    return {
        "room_occupancy": occupancy_data
    }

# Admin management routes (with permission examples)
@api_router.post("/admins", response_model=AdminResponse)
@require_permission(AdminRole.ADMIN)
async def create_admin(admin_data: dict):
    """Only ADMIN can create new admins"""
    admin = Admin(**admin_data)
    admin_dict = prepare_for_mongo(admin.dict())
    await db.admins.insert_one(admin_dict)
    return AdminResponse(**admin.dict())

@api_router.get("/admins", response_model=List[AdminResponse])
@require_permission(AdminRole.ADMIN)
async def get_all_admins():
    """Only ADMIN can view all admins"""
    admins = await db.admins.find().to_list(length=None)
    return [AdminResponse(**parse_from_mongo(admin)) for admin in admins]

@api_router.delete("/rooms/{room_id}")
@require_permission(AdminRole.MANAGER)
async def delete_room(room_id: str):
    """Only MANAGER or ADMIN can delete rooms"""
    existing = await db.rooms.find_one({"id": room_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Room not found")
    
    await db.rooms.delete_one({"id": room_id})
    return {"message": "Room deleted successfully"}

# Dashboard summary (any authenticated user)
@api_router.get("/dashboard")
async def get_dashboard_summary():
    total_rooms = await db.rooms.count_documents({})
    occupied_rooms = await db.rooms.count_documents({"status": "occupied"})
    empty_rooms = await db.rooms.count_documents({"status": "empty"})
    
    # Get today's orders count and revenue
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_orders = await db.orders.count_documents({"created_at": {"$gte": today.isoformat()}})
    
    # Calculate today's revenue from bills
    today_bills = await db.bills.find({
        "created_at": {"$gte": today.isoformat()}
    }).to_list(length=None)
    
    today_revenue = sum([bill.get("cost_calculation", {}).get("total_cost", 0) for bill in today_bills])
    
    return {
        "total_rooms": total_rooms,
        "occupied_rooms": occupied_rooms,
        "empty_rooms": empty_rooms,
        "occupancy_rate": round((occupied_rooms / total_rooms) * 100, 1) if total_rooms > 0 else 0,
        "today_orders": today_orders,
        "today_revenue": today_revenue
    }

@api_router.get("/rooms/{room_id}/current-cost")
async def get_current_cost(room_id: str):
    """Get current cost calculation for occupied room - only applies to hourly bookings"""
    existing = await db.rooms.find_one({"id": room_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if existing["status"] != "occupied":
        raise HTTPException(status_code=400, detail="Room is not occupied")
    
    # Check if this is an hourly booking by looking at stored booking_type
    booking_type = existing.get("booking_type", "hourly")  # Default to hourly for older records
    is_hourly_booking = booking_type == "hourly"
    
    check_in_date_str = existing["check_in_date"]
    check_out_date_str = existing.get("check_out_date")
    
    if isinstance(check_in_date_str, str):
        # Handle both timezone-aware and naive datetime strings
        if check_in_date_str.endswith('Z'):
            check_in_time = datetime.fromisoformat(check_in_date_str.replace('Z', '+00:00'))
        elif '+' in check_in_date_str or check_in_date_str.endswith('+00:00'):
            check_in_time = datetime.fromisoformat(check_in_date_str)
        else:
            # Assume UTC if no timezone info
            check_in_time = datetime.fromisoformat(check_in_date_str).replace(tzinfo=timezone.utc)
    else:
        check_in_time = check_in_date_str
        if check_in_time.tzinfo is None:
            check_in_time = check_in_time.replace(tzinfo=timezone.utc)
    
    # Parse check_out_date if exists
    planned_check_out_time = None
    if check_out_date_str:
        if isinstance(check_out_date_str, str):
            if check_out_date_str.endswith('Z'):
                planned_check_out_time = datetime.fromisoformat(check_out_date_str.replace('Z', '+00:00'))
            elif '+' in check_out_date_str or check_out_date_str.endswith('+00:00'):
                planned_check_out_time = datetime.fromisoformat(check_out_date_str)
            else:
                planned_check_out_time = datetime.fromisoformat(check_out_date_str).replace(tzinfo=timezone.utc)
        else:
            planned_check_out_time = check_out_date_str
            if planned_check_out_time.tzinfo is None:
                planned_check_out_time = planned_check_out_time.replace(tzinfo=timezone.utc)
    
    current_time = datetime.now(timezone.utc)
    
    # Get pricing from room or use default
    pricing_data = existing.get("pricing", {})
    pricing = PricingStructure(**pricing_data) if pricing_data else PricingStructure()
    
    if is_hourly_booking:
        # Real-time calculation for hourly bookings only
        cost_calculation = calculate_room_cost(check_in_time, current_time, pricing)
        calculation_method = "real_time_hourly"
        message = "Chi phí được tính theo thời gian thực (đặt theo giờ)"
    else:
        # For daily/monthly bookings, use the pre-calculated cost
        if planned_check_out_time:
            cost_calculation = calculate_room_cost(check_in_time, planned_check_out_time, pricing)
            calculation_method = "fixed_duration"
            message = f"Chi phí cố định theo kế hoạch (đặt theo {booking_type})"
        else:
            # Fallback - this shouldn't happen for daily/monthly bookings
            cost_calculation = {
                "total_cost": existing.get("total_cost", 0),
                "duration_hours": 0,
                "duration_days": 0,
                "calculation_type": booking_type,
                "details": f"Chi phí đã tính trước ({booking_type})"
            }
            calculation_method = "pre_calculated"
            message = f"Chi phí đã được tính trước (đặt theo {booking_type})"
    
    return {
        "room_number": existing["number"],
        "company_name": existing.get("company_name", "Cá nhân"),
        "guests": existing.get("guests", []),
        "guest_name": existing.get("guest_name"),  # Legacy field
        "check_in_time": check_in_time.isoformat(),
        "current_time": current_time.isoformat(),
        "planned_check_out_time": planned_check_out_time.isoformat() if planned_check_out_time else None,
        "booking_type": booking_type,
        "is_hourly_booking": is_hourly_booking,
        "calculation_method": calculation_method,
        "message": message,
        **cost_calculation
    }
@api_router.get("/rooms/{room_id}/guests")
async def get_room_guests(room_id: str):
    """Get guests information for a specific room"""
    room = await db.rooms.find_one({"id": room_id})
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    guests = room.get("guests", [])
    company_name = room.get("company_name")
    
    # Fallback to legacy guest_name
    if not guests and room.get("guest_name"):
        guests = [{
            "name": room["guest_name"],
            "phone": None,
            "email": None,
            "id_card": None
        }]
    
    return {
        "room_id": room_id,
        "room_number": room["number"],
        "company_name": company_name,
        "guests": guests,
        "status": room["status"]
    }

# Dashboard stats
@api_router.get("/dashboard/stats")
async def get_dashboard_stats():
    # Room stats
    total_rooms = await db.rooms.count_documents({})
    occupied_rooms = await db.rooms.count_documents({"status": "occupied"})
    empty_rooms = await db.rooms.count_documents({"status": "empty"})
    
    # Order stats for today
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_orders = await db.orders.count_documents({"order_date": {"$gte": today.isoformat()}})
    
    # Revenue stats for today
    today_bills = await db.bills.find({"created_at": {"$gte": today.isoformat()}}).to_list(length=None)
    today_revenue = sum([bill.get("cost_calculation", {}).get("total_cost", 0) for bill in today_bills])
    
    return {
        "total_rooms": total_rooms,
        "occupied_rooms": occupied_rooms,
        "empty_rooms": empty_rooms,
        "occupancy_rate": round((occupied_rooms / total_rooms) * 100, 1) if total_rooms > 0 else 0,
        "today_orders": today_orders,
        "today_revenue": today_revenue
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)

