#!/usr/bin/env python3
"""
Simplified version using in-memory storage for testing
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
import json

app = FastAPI(title="Hotel Management - Company Check-in")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
rooms_db = {}
bills_db = []

# Enums
class RoomType(str, Enum):
    SINGLE = "single"
    DOUBLE = "double"

class RoomStatus(str, Enum):
    EMPTY = "empty"
    OCCUPIED = "occupied"

class BookingType(str, Enum):
    HOURLY = "hourly"
    DAILY = "daily"
    MONTHLY = "monthly"

# Models
class RoomGuest(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    id_card: Optional[str] = None

class PricingStructure(BaseModel):
    hourly_first: float = 80000
    hourly_second: float = 40000
    hourly_additional: float = 20000
    daily_rate: float = 500000
    monthly_rate: float = 12000000

class Room(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    number: str
    type: RoomType
    status: RoomStatus = RoomStatus.EMPTY
    pricing: PricingStructure = Field(default_factory=PricingStructure)
    # Legacy field
    guest_name: Optional[str] = None
    # New fields
    company_name: Optional[str] = None
    guests: List[RoomGuest] = Field(default_factory=list)
    check_in_date: Optional[datetime] = None
    check_out_date: Optional[datetime] = None
    total_cost: Optional[float] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CheckInCompany(BaseModel):
    company_name: str
    guests: List[RoomGuest]
    booking_type: BookingType = BookingType.HOURLY
    duration: int = 1
    check_in_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Initialize sample data
def init_data():
    sample_rooms = [
        {"number": "101", "type": "double"},
        {"number": "102", "type": "double"},
        {"number": "201", "type": "single"},
        {"number": "202", "type": "single"},
    ]
    
    for room_data in sample_rooms:
        room = Room(**room_data)
        rooms_db[room.id] = room

init_data()

# Routes
@app.get("/api/rooms")
async def get_rooms():
    return list(rooms_db.values())

@app.get("/api/dashboard")
async def get_dashboard():
    total_rooms = len(rooms_db)
    occupied_rooms = sum(1 for room in rooms_db.values() if room.status == RoomStatus.OCCUPIED)
    empty_rooms = total_rooms - occupied_rooms
    
    return {
        "total_rooms": total_rooms,
        "occupied_rooms": occupied_rooms,
        "empty_rooms": empty_rooms,
        "occupancy_rate": round((occupied_rooms / total_rooms) * 100, 1) if total_rooms > 0 else 0
    }

@app.post("/api/rooms/{room_id}/checkin-company")
async def check_in_room_company(room_id: str, checkin_data: CheckInCompany):
    if room_id not in rooms_db:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room = rooms_db[room_id]
    if room.status != RoomStatus.EMPTY:
        raise HTTPException(status_code=400, detail="Room is not available")
    
    if not checkin_data.guests:
        raise HTTPException(status_code=400, detail="At least one guest is required")
    
    # Calculate check-out time
    check_in_time = checkin_data.check_in_date
    
    if checkin_data.booking_type == BookingType.HOURLY:
        check_out_time = check_in_time + timedelta(hours=checkin_data.duration)
    elif checkin_data.booking_type == BookingType.DAILY:
        check_out_time = check_in_time + timedelta(days=checkin_data.duration)
    elif checkin_data.booking_type == BookingType.MONTHLY:
        check_out_time = check_in_time + timedelta(days=checkin_data.duration * 30)
    
    # Calculate cost
    if checkin_data.booking_type == BookingType.HOURLY:
        if checkin_data.duration <= 1:
            total_cost = room.pricing.hourly_first
        elif checkin_data.duration <= 2:
            total_cost = room.pricing.hourly_first + room.pricing.hourly_second
        else:
            total_cost = room.pricing.hourly_first + room.pricing.hourly_second + ((checkin_data.duration - 2) * room.pricing.hourly_additional)
    elif checkin_data.booking_type == BookingType.DAILY:
        total_cost = room.pricing.daily_rate * checkin_data.duration
    elif checkin_data.booking_type == BookingType.MONTHLY:
        total_cost = room.pricing.monthly_rate * checkin_data.duration
    
    # Update room
    room.status = RoomStatus.OCCUPIED
    room.company_name = checkin_data.company_name
    room.guests = checkin_data.guests
    room.guest_name = checkin_data.guests[0].name  # Backward compatibility
    room.check_in_date = check_in_time
    room.check_out_date = check_out_time
    room.total_cost = total_cost
    
    return room

@app.get("/api/rooms/{room_id}/guests")
async def get_room_guests(room_id: str):
    if room_id not in rooms_db:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room = rooms_db[room_id]
    return {
        "room_id": room_id,
        "room_number": room.number,
        "company_name": room.company_name,
        "guests": room.guests,
        "status": room.status
    }

@app.post("/api/rooms/{room_id}/checkout")
async def check_out_room(room_id: str):
    if room_id not in rooms_db:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room = rooms_db[room_id]
    if room.status != RoomStatus.OCCUPIED:
        raise HTTPException(status_code=400, detail="Room is not occupied")
    
    # Calculate final cost
    check_out_time = datetime.now(timezone.utc)
    
    # Create bill
    bill = {
        "id": str(uuid.uuid4()),
        "room_number": room.number,
        "company_name": room.company_name,
        "guests": [guest.dict() for guest in room.guests],
        "check_in_time": room.check_in_date.isoformat(),
        "check_out_time": check_out_time.isoformat(),
        "total_cost": room.total_cost,
        "created_at": check_out_time.isoformat()
    }
    
    bills_db.append(bill)
    
    # Reset room
    company_name = room.company_name
    guests = room.guests
    total_cost = room.total_cost
    
    room.status = RoomStatus.EMPTY
    room.company_name = None
    room.guests = []
    room.guest_name = None
    room.check_in_date = None
    room.check_out_date = None
    room.total_cost = None
    
    return {
        "room": room,
        "company_name": company_name,
        "guests": [guest.dict() for guest in guests],
        "total_cost": total_cost,
        "bill_id": bill["id"]
    }

@app.post("/api/migrate/rooms")
async def migrate_rooms():
    """Migration endpoint for compatibility"""
    migrated_count = 0
    
    for room in rooms_db.values():
        if room.guest_name and not room.company_name:
            # Migrate old data
            room.company_name = "Cá nhân"
            room.guests = [RoomGuest(name=room.guest_name)]
            migrated_count += 1
    
    return {"message": f"Migrated {migrated_count} rooms successfully"}

@app.get("/api/bills")
async def get_bills():
    return bills_db[-10:]  # Return last 10 bills

if __name__ == "__main__":
    import uvicorn
    print("🚀 Khởi động Hotel Management Server với tính năng Company Check-in")
    print("📋 Tính năng mới:")
    print("   • RoomGuest model cho nhiều khách")
    print("   • CheckInCompany cho check-in công ty")
    print("   • Room model mở rộng với company_name & guests")
    print("   • Migration dữ liệu cũ")
    print("   • Backward compatibility")
    print("🌐 Server: http://127.0.0.1:8002")
    print("📚 API Docs: http://127.0.0.1:8002/docs")
    uvicorn.run(app, host="127.0.0.1", port=8002)
