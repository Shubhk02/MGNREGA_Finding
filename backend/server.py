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
from states_data import get_all_states, get_districts_for_state, INDIAN_STATES

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection (robust env handling)
# Support common var names and provide a clear error if missing
mongo_url = (
    os.environ.get('MONGO_URL')
    or os.environ.get('MONGODB_URI')
    or os.environ.get('MONGO_URI')
)
if not mongo_url:
    raise RuntimeError(
        "Missing MongoDB connection string. Set MONGO_URL (or MONGODB_URI/MONGO_URI) in your environment."
    )

db_name = os.environ.get('DB_NAME', 'mgnrega')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# Redis connection
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
redis_client = None

# data.gov.in configuration
DATA_GOV_API_KEY = os.environ.get('DATA_GOV_API_KEY', '579b464db66ec23bdd000001c5f7ea9da0054f1442874f7b61f02d14')
DATA_GOV_RESOURCE_ID = os.environ.get('DATA_GOV_RESOURCE_ID', 'ee03643a-ee4c-48c2-ac30-9f2ff26ab722')
USE_DATA_GOV = os.environ.get('USE_DATA_GOV', '0').strip() in {'1', 'true', 'yes', 'on'}

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
    """Fetch performance data from data.gov.in API if enabled; else return mock.

    This implementation makes a best-effort query against the provided resource.
    It attempts to map common field names; if data is unavailable or parsing fails,
    it falls back to mock data to keep the app responsive.
    """
    if not USE_DATA_GOV:
        return generate_mock_performance_data(district_code, month, year)

    base_url = f"https://api.data.gov.in/resource/{DATA_GOV_RESOURCE_ID}"
    params = {
        'api-key': DATA_GOV_API_KEY,
        'format': 'json',
        'limit': '1',
        # Best-effort filters; dataset schemas vary. Adjust as needed.
        'filters[district_code]': district_code,
        'filters[month]': str(month),
        'filters[year]': str(year),
    }

    def pick_num(rec: Dict[str, Any], keys: list[str], default: float = 0) -> float:
        for k in keys:
            if k in rec and rec[k] not in (None, ""):
                try:
                    return float(rec[k])
                except Exception:
                    pass
        return float(default)

    try:
        async with httpx.AsyncClient(timeout=8.0) as client_http:
            resp = await client_http.get(base_url, params=params)
            resp.raise_for_status()
            payload = resp.json()
            records = payload.get('records') or payload.get('data') or []
            if not records:
                return generate_mock_performance_data(district_code, month, year)
            rec = records[0]

            # Map likely fields to our schema; fallback to zeros when missing
            return {
                'district_code': district_code,
                'month': month,
                'year': year,
                'total_workers': int(pick_num(rec, ['total_workers', 'workers_total', 'tot_workers', 'households_worked'] , 0)),
                'work_completed': int(pick_num(rec, ['work_completed', 'works_completed', 'completed_works'], 0)),
                'work_ongoing': int(pick_num(rec, ['work_ongoing', 'works_ongoing', 'ongoing_works'], 0)),
                'average_wage': round(pick_num(rec, ['average_wage', 'avg_wage', 'wage_avg'], 0.0), 2),
                'budget_allocated': round(pick_num(rec, ['budget_allocated', 'funds_allocated', 'allocated_funds'], 0.0), 2),
                'budget_spent': round(pick_num(rec, ['budget_spent', 'expenditure', 'funds_spent'], 0.0), 2),
                'person_days_generated': int(pick_num(rec, ['person_days_generated', 'persondays', 'person_days', 'person_days_total'], 0)),
            }
    except Exception as e:
        logging.warning(f"data.gov.in fetch failed, falling back to mock: {e}")
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
    """Get all districts for a state (deduped by district_code)."""
    try:
        cache_key = f"districts:{state_code}"
        cached_data = await cache_get(cache_key)
        
        if cached_data:
            return DistrictResponse(success=True, data=cached_data)
        
        # Fetch and deduplicate in Python by normalized district_code
        districts_raw = await db.districts.find(
            {"state_code": state_code},
            {"_id": 0}
        ).sort("district_name", 1).to_list(1000)

        def _normalize(d: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            code = str(d.get("district_code", "")).strip().upper()
            if not code:
                return None
            d["district_code"] = code
            # Also trim names if present
            if d.get("district_name"):
                d["district_name"] = str(d["district_name"]).strip()
            if d.get("district_name_hi"):
                d["district_name_hi"] = str(d["district_name_hi"]).strip()
            return d

        dedup: Dict[str, Dict[str, Any]] = {}
        for d in districts_raw:
            nd = _normalize(d)
            if not nd:
                continue
            code = nd["district_code"]
            if code not in dedup:
                dedup[code] = nd
        districts = list(dedup.values())

        if not districts:
            # As a fallback, load from data file without writing to DB
            data_file = ROOT_DIR / 'data' / 'up_districts.json'
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    file_items = json.load(f)
                tmp: Dict[str, Dict[str, Any]] = {}
                for d in file_items:
                    code = str(d.get("district_code", "")).strip().upper()
                    if not code:
                        continue
                    if code not in tmp:
                        tmp[code] = {
                            "id": str(uuid.uuid4()),
                            "district_code": code,
                            "district_name": (d.get("district_name") or "").strip(),
                            "district_name_hi": (d.get("district_name_hi") or d.get("district_name") or "").strip(),
                            "state_code": state_code,
                            "state_name": "Uttar Pradesh" if state_code == "UP" else "",
                            "state_name_hi": "उत्तर प्रदेश" if state_code == "UP" else "",
                        }
                districts = list(tmp.values())
            except Exception as _:
                districts = []
        
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
    """Seed UP districts from data file; upsert missing entries so we reach full coverage."""
    data_file = ROOT_DIR / 'data' / 'up_districts.json'
    up_districts: List[Dict[str, Any]] = []
    try:
        if data_file.exists():
            import json as _json
            with open(data_file, 'r', encoding='utf-8') as f:
                up_districts = _json.load(f)
        else:
            logging.warning(f"District data file not found: {data_file}. Seeding minimal defaults.")
            up_districts = []
    except Exception as e:
        logging.warning(f"Failed to load districts file: {e}. Using minimal list.")
        up_districts = []

    # Decorate and upsert
    results: List[Dict[str, Any]] = []
    for d in up_districts:
        # Normalize and sanitize values
        raw_code = d.get("district_code", "")
        norm_code = str(raw_code).strip().upper()
        name_en = (d.get("district_name") or "").strip()
        name_hi = (d.get("district_name_hi") or name_en).strip()

        if not norm_code:
            continue  # skip invalid entries

        doc = {
            "id": str(uuid.uuid4()),
            "district_code": norm_code,
            "district_name": name_en,
            "district_name_hi": name_hi,
            "state_code": "UP",
            "state_name": "Uttar Pradesh",
            "state_name_hi": "उत्तर प्रदेश",
        }
        # Upsert by district_code; then update key fields to normalized values
        try:
            await db.districts.update_one(
                {"district_code": doc["district_code"]},
                {"$setOnInsert": doc},
                upsert=True
            )
            await db.districts.update_one(
                {"district_code": doc["district_code"]},
                {"$set": {
                    "district_name": doc["district_name"],
                    "district_name_hi": doc["district_name_hi"],
                    "state_code": doc["state_code"],
                    "state_name": doc["state_name"],
                    "state_name_hi": doc["state_name_hi"]
                }},
                upsert=False
            )
            results.append(doc)
        except Exception as e:
            logging.warning(f"Upsert failed for {doc['district_code']}: {e}")

    # If DB ended up empty (e.g., file missing), ensure at least what's in states_data
    if not results:
        from states_data import STATE_DISTRICTS
        for d in STATE_DISTRICTS.get('UP', []):
            raw_code = d.get("district_code", "")
            norm_code = str(raw_code).strip().upper()
            name_en = (d.get("district_name") or "").strip()
            name_hi = (d.get("district_name_hi") or name_en).strip()

            if not norm_code:
                continue

            doc = {
                "id": str(uuid.uuid4()),
                "district_code": norm_code,
                "district_name": name_en,
                "district_name_hi": name_hi,
                "state_code": "UP",
                "state_name": "Uttar Pradesh",
                "state_name_hi": "उत्तर प्रदेश",
            }
            await db.districts.update_one(
                {"district_code": doc["district_code"]},
                {"$setOnInsert": doc},
                upsert=True
            )
            await db.districts.update_one(
                {"district_code": doc["district_code"]},
                {"$set": {
                    "district_name": doc["district_name"],
                    "district_name_hi": doc["district_name_hi"],
                    "state_code": doc["state_code"],
                    "state_name": doc["state_name"],
                    "state_name_hi": doc["state_name_hi"]
                }},
                upsert=False
            )
            results.append(doc)

    return results

# Configure CORS origins robustly (strip quotes and whitespace)
raw_origins = os.environ.get('CORS_ORIGINS', '*')
if raw_origins == '*':
    allow_origins = ['*']
else:
    allow_origins = [o.strip().strip('"').strip("'") for o in raw_origins.split(',') if o.strip()]

# Log resolved origins
logging.getLogger(__name__).info(f"Configured CORS origins: {allow_origins}")

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=allow_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(api_router)

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