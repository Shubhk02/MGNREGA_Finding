from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import httpx
import redis.asyncio as redis
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Redis connection
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
redis_client = None

# data.gov.in API key
DATA_GOV_API_KEY = os.environ.get('DATA_GOV_API_KEY', '579b464db66ec23bdd000001c5f7ea9da0054f1442874f7b61f02d14')

# Create the main app
app = FastAPI(title="MGNREGA Dashboard API")
api_router = APIRouter(prefix="/api")

# Models
class District(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    district_code: str
    district_name: str
    district_name_hi: str
    state_code: str = "UP"
    state_name: str = "Uttar Pradesh"
    state_name_hi: str = "उत्तर प्रदेश"
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class PerformanceData(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    district_code: str
    month: int
    year: int
    total_workers: int = 0
    work_completed: int = 0
    work_ongoing: int = 0
    average_wage: float = 0.0
    budget_allocated: float = 0.0
    budget_spent: float = 0.0
    person_days_generated: int = 0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DistrictResponse(BaseModel):
    success: bool
    data: List[District]

class PerformanceResponse(BaseModel):
    success: bool
    data: Optional[PerformanceData] = None

class HistoricalResponse(BaseModel):
    success: bool
    data: List[PerformanceData]

class ComparisonResponse(BaseModel):
    success: bool
    data: Dict[str, Any]

# Helper Functions
async def get_redis():
    global redis_client
    if redis_client is None:
        try:
            redis_client = await redis.from_url(redis_url, decode_responses=True)
        except Exception as e:
            logging.warning(f"Redis connection failed: {e}. Continuing without cache.")
    return redis_client

async def cache_get(key: str) -> Optional[Any]:
    try:
        r = await get_redis()
        if r:
            value = await r.get(key)
            return json.loads(value) if value else None
    except Exception as e:
        logging.error(f"Cache get error: {e}")
    return None

async def cache_set(key: str, value: Any, ttl: int = 3600):
    try:
        r = await get_redis()
        if r:
            await r.setex(key, ttl, json.dumps(value, default=str))
    except Exception as e:
        logging.error(f"Cache set error: {e}")

async def fetch_from_data_gov(district_code: str, month: int, year: int) -> Dict[str, Any]:
    """Fetch performance data from data.gov.in API"""
    # For MVP, using mock data as the actual data.gov.in MGNREGA API endpoint structure may vary
    # In production, replace with actual data.gov.in MGNREGA API endpoint once confirmed
    return generate_mock_performance_data(district_code, month, year)

def generate_mock_performance_data(district_code: str, month: int, year: int) -> Dict[str, Any]:
    """Generate realistic mock data for demonstration"""
    import random
    base_seed = hash(f"{district_code}{month}{year}")
    random.seed(base_seed)
    
    return {
        "district_code": district_code,
        "month": month,
        "year": year,
        "total_workers": random.randint(5000, 50000),
        "work_completed": random.randint(50, 200),
        "work_ongoing": random.randint(10, 100),
        "average_wage": round(random.uniform(180.0, 250.0), 2),
        "budget_allocated": round(random.uniform(10000000, 50000000), 2),
        "budget_spent": round(random.uniform(5000000, 45000000), 2),
        "person_days_generated": random.randint(100000, 500000)
    }

# API Routes
@api_router.get("/")
async def root():
    return {"message": "MGNREGA Dashboard API", "version": "1.0"}

@api_router.get("/districts", response_model=DistrictResponse)
async def get_districts(state_code: str = Query("UP")):
    """Get all districts for a state"""
    try:
        cache_key = f"districts:{state_code}"
        cached_data = await cache_get(cache_key)
        
        if cached_data:
            return DistrictResponse(success=True, data=cached_data)
        
        districts = await db.districts.find(
            {"state_code": state_code},
            {"_id": 0}
        ).sort("district_name", 1).to_list(100)
        
        if not districts:
            # If no districts in DB, return a default list
            districts = await seed_default_districts(state_code)
        
        await cache_set(cache_key, districts, 86400)  # Cache for 24 hours
        return DistrictResponse(success=True, data=districts)
    except Exception as e:
        logging.error(f"Error fetching districts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/district/{district_code}/current", response_model=PerformanceResponse)
async def get_current_performance(district_code: str):
    """Get current month's performance for a district"""
    try:
        now = datetime.now(timezone.utc)
        cache_key = f"performance:{district_code}:{now.month}:{now.year}"
        
        cached_data = await cache_get(cache_key)
        if cached_data:
            return PerformanceResponse(success=True, data=cached_data)
        
        # Check if data exists in DB
        perf_data = await db.performance_data.find_one(
            {
                "district_code": district_code,
                "month": now.month,
                "year": now.year
            },
            {"_id": 0}
        )
        
        if not perf_data:
            # Fetch from API or generate mock data
            api_data = await fetch_from_data_gov(district_code, now.month, now.year)
            perf_data = PerformanceData(**api_data).model_dump()
            
            # Store in DB
            await db.performance_data.insert_one(perf_data)
        
        await cache_set(cache_key, perf_data, 3600)  # Cache for 1 hour
        return PerformanceResponse(success=True, data=perf_data)
    except Exception as e:
        logging.error(f"Error fetching current performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/district/{district_code}/history", response_model=HistoricalResponse)
async def get_historical_performance(district_code: str, months: int = Query(6, ge=1, le=24)):
    """Get historical performance data for a district"""
    try:
        cache_key = f"history:{district_code}:{months}"
        cached_data = await cache_get(cache_key)
        
        if cached_data:
            return HistoricalResponse(success=True, data=cached_data)
        
        # Generate date range
        now = datetime.now(timezone.utc)
        historical_data = []
        
        for i in range(months):
            date = now - timedelta(days=30 * i)
            month, year = date.month, date.year
            
            # Check DB first
            perf_data = await db.performance_data.find_one(
                {"district_code": district_code, "month": month, "year": year},
                {"_id": 0}
            )
            
            if not perf_data:
                # Generate or fetch data
                api_data = await fetch_from_data_gov(district_code, month, year)
                perf_data = PerformanceData(**api_data).model_dump()
                await db.performance_data.insert_one(perf_data)
            
            historical_data.append(perf_data)
        
        historical_data.reverse()  # Oldest first
        await cache_set(cache_key, historical_data, 7200)  # Cache for 2 hours
        return HistoricalResponse(success=True, data=historical_data)
    except Exception as e:
        logging.error(f"Error fetching historical data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/district/{district_code}/compare", response_model=ComparisonResponse)
async def compare_performance(district_code: str):
    """Compare current month with previous month"""
    try:
        now = datetime.now(timezone.utc)
        prev_month = now - timedelta(days=30)
        
        # Get current month data
        current = await db.performance_data.find_one(
            {"district_code": district_code, "month": now.month, "year": now.year},
            {"_id": 0}
        )
        
        if not current:
            api_data = await fetch_from_data_gov(district_code, now.month, now.year)
            current = PerformanceData(**api_data).model_dump()
            await db.performance_data.insert_one(current)
        
        # Get previous month data
        previous = await db.performance_data.find_one(
            {"district_code": district_code, "month": prev_month.month, "year": prev_month.year},
            {"_id": 0}
        )
        
        if not previous:
            api_data = await fetch_from_data_gov(district_code, prev_month.month, prev_month.year)
            previous = PerformanceData(**api_data).model_dump()
            await db.performance_data.insert_one(previous)
        
        # Calculate comparisons
        comparison = {
            "current": current,
            "previous": previous,
            "changes": {
                "total_workers": ((current["total_workers"] - previous["total_workers"]) / previous["total_workers"] * 100) if previous["total_workers"] > 0 else 0,
                "work_completed": ((current["work_completed"] - previous["work_completed"]) / previous["work_completed"] * 100) if previous["work_completed"] > 0 else 0,
                "budget_spent": ((current["budget_spent"] - previous["budget_spent"]) / previous["budget_spent"] * 100) if previous["budget_spent"] > 0 else 0,
                "person_days_generated": ((current["person_days_generated"] - previous["person_days_generated"]) / previous["person_days_generated"] * 100) if previous["person_days_generated"] > 0 else 0
            }
        }
        
        return ComparisonResponse(success=True, data=comparison)
    except Exception as e:
        logging.error(f"Error comparing performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def seed_default_districts(state_code: str = "UP") -> List[Dict[str, Any]]:
    """Seed default UP districts if not present"""
    up_districts = [
        {"district_code": "UP01", "district_name": "Agra", "district_name_hi": "आगरा", "latitude": 27.1767, "longitude": 78.0081},
        {"district_code": "UP02", "district_name": "Aligarh", "district_name_hi": "अलीगढ़", "latitude": 27.8974, "longitude": 78.0880},
        {"district_code": "UP03", "district_name": "Allahabad", "district_name_hi": "इलाहाबाद", "latitude": 25.4358, "longitude": 81.8463},
        {"district_code": "UP04", "district_name": "Ambedkar Nagar", "district_name_hi": "अंबेडकर नगर", "latitude": 26.4050, "longitude": 82.6986},
        {"district_code": "UP05", "district_name": "Amethi", "district_name_hi": "अमेठी", "latitude": 26.1544, "longitude": 81.8084},
        {"district_code": "UP06", "district_name": "Amroha", "district_name_hi": "अमरोहा", "latitude": 28.9031, "longitude": 78.4675},
        {"district_code": "UP07", "district_name": "Auraiya", "district_name_hi": "औरैया", "latitude": 26.4667, "longitude": 79.5167},
        {"district_code": "UP08", "district_name": "Azamgarh", "district_name_hi": "आजमगढ़", "latitude": 26.0686, "longitude": 83.1840},
        {"district_code": "UP09", "district_name": "Baghpat", "district_name_hi": "बागपत", "latitude": 28.9472, "longitude": 77.2195},
        {"district_code": "UP10", "district_name": "Bahraich", "district_name_hi": "बहराइच", "latitude": 27.5742, "longitude": 81.5947},
        {"district_code": "UP11", "district_name": "Ballia", "district_name_hi": "बलिया", "latitude": 25.7648, "longitude": 84.1496},
        {"district_code": "UP12", "district_name": "Balrampur", "district_name_hi": "बलरामपुर", "latitude": 27.4308, "longitude": 82.1807},
        {"district_code": "UP13", "district_name": "Banda", "district_name_hi": "बांदा", "latitude": 25.4762, "longitude": 80.3361},
        {"district_code": "UP14", "district_name": "Barabanki", "district_name_hi": "बाराबंकी", "latitude": 26.9245, "longitude": 81.1840},
        {"district_code": "UP15", "district_name": "Bareilly", "district_name_hi": "बरेली", "latitude": 28.3670, "longitude": 79.4304},
        {"district_code": "UP16", "district_name": "Basti", "district_name_hi": "बस्ती", "latitude": 26.7850, "longitude": 82.7392},
        {"district_code": "UP17", "district_name": "Bijnor", "district_name_hi": "बिजनौर", "latitude": 29.3731, "longitude": 78.1331},
        {"district_code": "UP18", "district_name": "Budaun", "district_name_hi": "बदायूं", "latitude": 28.0330, "longitude": 79.1333},
        {"district_code": "UP19", "district_name": "Bulandshahr", "district_name_hi": "बुलंदशहर", "latitude": 28.4067, "longitude": 77.8498},
        {"district_code": "UP20", "district_name": "Chandauli", "district_name_hi": "चंदौली", "latitude": 25.2667, "longitude": 83.2667},
        {"district_code": "UP21", "district_name": "Chitrakoot", "district_name_hi": "चित्रकूट", "latitude": 25.2000, "longitude": 80.9000},
        {"district_code": "UP22", "district_name": "Deoria", "district_name_hi": "देवरिया", "latitude": 26.5024, "longitude": 83.7791},
        {"district_code": "UP23", "district_name": "Etah", "district_name_hi": "एटा", "latitude": 27.5639, "longitude": 78.6628},
        {"district_code": "UP24", "district_name": "Etawah", "district_name_hi": "इटावा", "latitude": 26.7855, "longitude": 79.0215},
        {"district_code": "UP25", "district_name": "Faizabad", "district_name_hi": "फैजाबाद", "latitude": 26.7750, "longitude": 82.1496},
        {"district_code": "UP26", "district_name": "Farrukhabad", "district_name_hi": "फर्रुखाबाद", "latitude": 27.3882, "longitude": 79.5804},
        {"district_code": "UP27", "district_name": "Fatehpur", "district_name_hi": "फतेहपुर", "latitude": 25.9308, "longitude": 80.8122},
        {"district_code": "UP28", "district_name": "Firozabad", "district_name_hi": "फिरोजाबाद", "latitude": 27.1484, "longitude": 78.3957},
        {"district_code": "UP29", "district_name": "Gautam Buddha Nagar", "district_name_hi": "गौतम बुद्ध नगर", "latitude": 28.3587, "longitude": 77.5186},
        {"district_code": "UP30", "district_name": "Ghaziabad", "district_name_hi": "गाजियाबाद", "latitude": 28.6692, "longitude": 77.4538},
        {"district_code": "UP31", "district_name": "Ghazipur", "district_name_hi": "गाजीपुर", "latitude": 25.5881, "longitude": 83.5778},
        {"district_code": "UP32", "district_name": "Gonda", "district_name_hi": "गोंडा", "latitude": 27.1333, "longitude": 81.9667},
        {"district_code": "UP33", "district_name": "Gorakhpur", "district_name_hi": "गोरखपुर", "latitude": 26.7606, "longitude": 83.3732},
        {"district_code": "UP34", "district_name": "Hamirpur", "district_name_hi": "हमीरपुर", "latitude": 25.9565, "longitude": 80.1482},
        {"district_code": "UP35", "district_name": "Hapur", "district_name_hi": "हापुड़", "latitude": 28.7293, "longitude": 77.7758},
        {"district_code": "UP36", "district_name": "Hardoi", "district_name_hi": "हरदोई", "latitude": 27.3965, "longitude": 80.1251},
        {"district_code": "UP37", "district_name": "Hathras", "district_name_hi": "हाथरस", "latitude": 27.5952, "longitude": 78.0499},
        {"district_code": "UP38", "district_name": "Jalaun", "district_name_hi": "जालौन", "latitude": 26.1447, "longitude": 79.3376},
        {"district_code": "UP39", "district_name": "Jaunpur", "district_name_hi": "जौनपुर", "latitude": 25.7462, "longitude": 82.6841},
        {"district_code": "UP40", "district_name": "Jhansi", "district_name_hi": "झांसी", "latitude": 25.4486, "longitude": 78.5696},
        {"district_code": "UP41", "district_name": "Kannauj", "district_name_hi": "कन्नौज", "latitude": 27.0514, "longitude": 79.9142},
        {"district_code": "UP42", "district_name": "Kanpur Dehat", "district_name_hi": "कानपुर देहात", "latitude": 26.4675, "longitude": 79.8655},
        {"district_code": "UP43", "district_name": "Kanpur Nagar", "district_name_hi": "कानपुर नगर", "latitude": 26.4499, "longitude": 80.3319},
        {"district_code": "UP44", "district_name": "Kasganj", "district_name_hi": "कासगंज", "latitude": 27.8088, "longitude": 78.6443},
        {"district_code": "UP45", "district_name": "Kaushambi", "district_name_hi": "कौशाम्बी", "latitude": 25.5316, "longitude": 81.3784},
        {"district_code": "UP46", "district_name": "Kushinagar", "district_name_hi": "कुशीनगर", "latitude": 26.7420, "longitude": 83.8891},
        {"district_code": "UP47", "district_name": "Lakhimpur Kheri", "district_name_hi": "लखीमपुर खीरी", "latitude": 27.9474, "longitude": 80.7780},
        {"district_code": "UP48", "district_name": "Lalitpur", "district_name_hi": "ललितपुर", "latitude": 24.6880, "longitude": 78.4122},
        {"district_code": "UP49", "district_name": "Lucknow", "district_name_hi": "लखनऊ", "latitude": 26.8467, "longitude": 80.9462},
        {"district_code": "UP50", "district_name": "Maharajganj", "district_name_hi": "महाराजगंज", "latitude": 27.1441, "longitude": 83.5599}
    ]
    
    # Add more fields
    for district in up_districts:
        district.update({
            "id": str(uuid.uuid4()),
            "state_code": "UP",
            "state_name": "Uttar Pradesh",
            "state_name_hi": "उत्तर प्रदेश"
        })
    
    # Insert into DB
    try:
        await db.districts.insert_many(up_districts)
    except Exception as e:
        logging.warning(f"Error seeding districts: {e}")
    
    return up_districts

# Include router
app.include_router(api_router)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting MGNREGA Dashboard API")
    await get_redis()

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    if redis_client:
        await redis_client.close()