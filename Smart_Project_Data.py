import time
import random
from datetime import datetime, timedelta
from faker import Faker
from pymongo import MongoClient
from bson import ObjectId

# === MongoDB Setup ===
client = MongoClient("mongodb://localhost:27017/")
db = client.smart_transport
vehicles_col = db.vehicles
trips_col = db.trips

# === Constants ===
fake = Faker()
VEHICLE_TYPES = ["Bus", "Taxi", "Truck", "Van"]
PROVINCES = [
    "Gauteng", "Western Cape", "KwaZulu-Natal", "Eastern Cape",
    "Free State", "Limpopo", "Mpumalanga", "North West", "Northern Cape"
]
BASE_LAT = -25.7479
BASE_LNG = 28.2293

# === Create Fleet of Vehicles ===
def create_fleet(n=5):
    fleet = []
    for _ in range(n):
        vehicle = {
            "plateNumber": fake.bothify('??###').upper(),
            "type": random.choice(VEHICLE_TYPES),
            "status": "Active",
            "province": random.choice(PROVINCES),
            "currentLocation": {
                "lat": round(BASE_LAT + random.uniform(-0.01, 0.01), 6),
                "lng": round(BASE_LNG + random.uniform(-0.01, 0.01), 6),
                "timestamp": datetime.utcnow()
            }
        }
        vehicle_id = vehicles_col.insert_one(vehicle).inserted_id
        fleet.append(vehicle_id)
        print(f"✅ Created Vehicle {vehicle['plateNumber']} in {vehicle['province']}")
    return fleet

# === Update Vehicle Location (simulate movement) ===
def update_vehicle_location(vehicle_id):
    move_lat = round(random.uniform(-0.001, 0.001), 6)
    move_lng = round(random.uniform(-0.001, 0.001), 6)
    vehicle = vehicles_col.find_one({"_id": vehicle_id})
    if not vehicle:
        return
    new_lat = round(vehicle['currentLocation']['lat'] + move_lat, 6)
    new_lng = round(vehicle['currentLocation']['lng'] + move_lng, 6)
    vehicles_col.update_one(
        {"_id": vehicle_id},
        {"$set": {
            "currentLocation.lat": new_lat,
            "currentLocation.lng": new_lng,
            "currentLocation.timestamp": datetime.utcnow()
        }}
    )
    print(f"📍 Vehicle {vehicle['plateNumber']} moved to ({new_lat}, {new_lng})")

# === Create Trip with Fare Breakdown ===
def generate_trip(vehicle_id):
    driver_id = ObjectId()
    route_id = ObjectId()
    distance_km = round(random.uniform(5.0, 25.0), 1)
    base_fare = 10.00
    rate_per_km = 2.50
    surcharge = random.choice([0, 5, 10])
    distance_rate = round(rate_per_km * distance_km, 2)
    subtotal = base_fare + distance_rate + surcharge
    vat = round(subtotal * 0.15, 2)
    total = round(subtotal + vat, 2)

    start_time = datetime.utcnow() - timedelta(minutes=random.randint(10, 30))
    end_time = start_time + timedelta(minutes=random.randint(10, 30))

    trip = {
        "vehicleId": vehicle_id,
        "driverId": driver_id,
        "routeId": route_id,
        "startTime": start_time,
        "endTime": end_time,
        "distanceKm": distance_km,
        "fare": {
            "baseFare": base_fare,
            "distanceRate": distance_rate,
            "surcharge": surcharge,
            "vat": vat,
            "total": total
        }
    }

    trip_id = trips_col.insert_one(trip).inserted_id
    print(f"🧾 Trip for vehicle ID {vehicle_id} - Distance: {distance_km}km, Fare: R{total}")

# === Main Simulation Loop ===
def run_simulation():
    fleet = create_fleet(5)
    print("\n🚦 Starting real-time simulation every 30 seconds...\n")
    while True:
        for vehicle_id in fleet:
            update_vehicle_location(vehicle_id)
            generate_trip(vehicle_id)
        print("⏳ Waiting 30 seconds...\n")
        time.sleep(30)

# === Start Simulation ===
if __name__ == "__main__":
    run_simulation()

