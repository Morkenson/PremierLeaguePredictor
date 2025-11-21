from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import uvicorn
import os
import asyncio
import time
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.match_predictor_simple import MatchPredictor
from services.data_service import DataService
from services.prediction_service import PredictionService
from services.scheduler_service import SchedulerService

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Premier League Match Predictor",
    description="AI-powered Premier League match prediction system",
    version="1.0.0"
)

# CORS middleware for React frontend
# Get allowed origins from environment variable or use defaults
frontend_url = os.getenv("FRONTEND_URL", "")
allowed_origins = [
    "http://localhost:3000", 
    "http://127.0.0.1:3000",
    "https://premier-league-predictor-zach.vercel.app",  # Remove trailing slash
]

if frontend_url:
    allowed_origins.append(frontend_url)
    # Also add without protocol variations
    if frontend_url.startswith("https://"):
        allowed_origins.append(frontend_url.replace("https://", "http://"))

# For production, be more permissive with Vercel domains
if os.getenv("ENVIRONMENT") == "production" or not os.getenv("ENVIRONMENT"):
    # Allow common Vercel patterns
    allowed_origins.extend([
        "https://*.vercel.app",
        "http://*.vercel.app",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily allow all for debugging - can restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # Expose all headers
)

# Initialize services
data_service = DataService()
prediction_service = PredictionService()
scheduler_service = SchedulerService(data_service, prediction_service)

# Pydantic models for API
class TeamInfo(BaseModel):
    name: str
    id: int

class MatchPredictionRequest(BaseModel):
    home_team: str
    away_team: str
    season: Optional[str] = "2023-24"

class MatchPredictionResponse(BaseModel):
    home_team: str
    away_team: str
    home_win_probability: float
    draw_probability: float
    away_win_probability: float
    predicted_score: Dict[str, int]
    confidence: float
    key_factors: List[str]

class TeamStats(BaseModel):
    team_name: str
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    points: int
    form: List[str]  # Last 5 results
    home_record: Dict[str, int]
    away_record: Dict[str, int]

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and responses"""
    start_time = time.time()
    logger.info(f"Request: {request.method} {request.url}")
    logger.info(f"Origin: {request.headers.get('origin', 'No origin')}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"Response: {response.status_code} - {process_time:.2f}s")
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Error processing request after {process_time:.2f}s: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            }
        )

@app.on_event("startup")
async def startup_event():
    """Initialize the prediction model and scheduler on startup"""
    try:
        # Initialize data and model
        await prediction_service.initialize_model()
        print("SUCCESS: Prediction model initialized successfully")
        
        # Start daily update scheduler
        scheduler_service.start_scheduler()
        print("SUCCESS: Daily update scheduler started")
        
    except Exception as e:
        print(f"ERROR: Error during startup: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    scheduler_service.stop_scheduler()
    print("Scheduler stopped")

@app.get("/")
async def root():
    return {"message": "Premier League Match Predictor API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/teams", response_model=List[TeamInfo])
async def get_teams():
    """Get list of all Premier League teams"""
    try:
        teams = await data_service.get_teams()
        return teams
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/teams/{team_name}/stats", response_model=TeamStats)
async def get_team_stats(team_name: str, season: str = "2023-24"):
    """Get detailed statistics for a specific team"""
    try:
        stats = await data_service.get_team_stats(team_name, season)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict", response_model=MatchPredictionResponse)
async def predict_match(request: MatchPredictionRequest):
    """Predict the outcome of a Premier League match"""
    try:
        prediction = await prediction_service.predict_match(
            request.home_team,
            request.away_team,
            request.season
        )
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/fixtures")
async def get_upcoming_fixtures():
    """Get upcoming Premier League fixtures"""
    try:
        logger.info("Fetching fixtures...")
        # Add timeout protection
        fixtures = await asyncio.wait_for(
            data_service.get_upcoming_fixtures(),
            timeout=8.0  # 8 second timeout
        )
        logger.info(f"Returning {len(fixtures)} fixtures")
        return JSONResponse(
            content=fixtures,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            }
        )
    except asyncio.TimeoutError:
        logger.error("Timeout getting fixtures")
        return JSONResponse(
            status_code=504,
            content={"detail": "Request timeout - server is processing data"},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            }
        )
    except Exception as e:
        logger.error(f"Error getting fixtures: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            }
        )

@app.get("/predictions/batch")
async def get_batch_predictions():
    """Get predictions for all upcoming fixtures"""
    try:
        predictions = await prediction_service.get_batch_predictions()
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/league-table")
async def get_league_table(season: str = "2023-24"):
    """Get current Premier League table"""
    try:
        logger.info(f"Fetching league table for season {season}...")
        # Add timeout protection
        table = await asyncio.wait_for(
            data_service.get_league_table(season),
            timeout=8.0  # 8 second timeout
        )
        logger.info(f"Returning league table with {len(table)} teams")
        return JSONResponse(
            content=table,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            }
        )
    except asyncio.TimeoutError:
        logger.error("Timeout getting league table")
        return JSONResponse(
            status_code=504,
            content={"detail": "Request timeout - server is processing data"},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            }
        )
    except Exception as e:
        logger.error(f"Error getting league table: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            }
        )

@app.get("/league-standings")
async def get_league_standings(season: str = "2023-24"):
    """Get league standings directly from API"""
    try:
        standings = await data_service.get_league_standings_from_api(season)
        return standings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/teams/{team_id}/matches")
async def get_team_matches(team_id: int, limit: int = 10):
    """Get all matches for a specific team"""
    try:
        matches = await data_service.get_team_matches(team_id, limit)
        return matches
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/matches/{match_id}")
async def get_match_details(match_id: int):
    """Get detailed information about a specific match"""
    try:
        match = await data_service.get_match_details(match_id)
        return match
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/competition")
async def get_competition_info():
    """Get Premier League competition information"""
    try:
        info = await data_service.get_competition_info()
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/head-to-head/{team1_id}/{team2_id}")
async def get_head_to_head(team1_id: int, team2_id: int):
    """Get head-to-head record between two teams"""
    try:
        h2h = await data_service.get_head_to_head(team1_id, team2_id)
        return h2h
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/refresh-data")
async def manual_refresh_data():
    """Manually trigger data refresh and model retraining"""
    try:
        success = await scheduler_service.trigger_manual_update()
        
        if success:
            return {
                "status": "success",
                "message": "Data refreshed and model retrained successfully",
                "timestamp": datetime.now().isoformat(),
                "last_update": data_service.last_update.isoformat() if data_service.last_update else None
            }
        else:
            return {
                "status": "error",
                "message": "Data refresh failed, using existing data",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin/scheduler-status")
async def get_scheduler_status():
    """Get scheduler status and next run time"""
    try:
        logger.info("Fetching scheduler status...")
        next_run = scheduler_service.get_next_run_time()
        status = {
            "scheduler_running": scheduler_service.is_running,
            "next_update": next_run.isoformat() if next_run else None,
            "last_update": data_service.last_update.isoformat() if data_service.last_update else None,
            "timestamp": datetime.now().isoformat()
        }
        logger.info(f"Returning scheduler status: {status}")
        return JSONResponse(
            content=status,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            }
        )
    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            }
        )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
