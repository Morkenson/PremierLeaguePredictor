from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import uvicorn
import os
from dotenv import load_dotenv

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.match_predictor_simple import MatchPredictor
from services.data_service import DataService
from services.prediction_service import PredictionService

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
allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
if frontend_url:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
data_service = DataService()
prediction_service = PredictionService()

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

@app.on_event("startup")
async def startup_event():
    """Initialize the prediction model on startup"""
    try:
        await prediction_service.initialize_model()
        print("SUCCESS: Prediction model initialized successfully")
    except Exception as e:
        print(f"ERROR: Error initializing model: {e}")

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
        fixtures = await data_service.get_upcoming_fixtures()
        return fixtures
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        table = await data_service.get_league_table(season)
        return table
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
