from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from Vercel API!"}

@app.get("/api/test")
def test_endpoint():
    return {"status": "working", "data": "API is functional"}

@app.get("/api/rooms")
def get_rooms():
    return [
        {"id": "1", "number": "201", "type": "single", "status": "empty"},
        {"id": "2", "number": "202", "type": "single", "status": "empty"},
        {"id": "3", "number": "203", "type": "double", "status": "empty"}
    ]

@app.get("/api/dishes")
def get_dishes():
    return [
        {"id": "1", "name": "Phở bò", "price": 50000},
        {"id": "2", "name": "Cơm tấm", "price": 45000},
        {"id": "3", "name": "Bánh mì", "price": 25000}
    ]

@app.get("/api/dashboard/stats")
def get_stats():
    return {
        "total_rooms": 20,
        "empty_rooms": 18,
        "occupied_rooms": 2,
        "occupancy_rate": 10,
        "today_revenue": 500000
    }
