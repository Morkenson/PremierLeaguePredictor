from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uvicorn
import os
import sys
import asyncio
import time
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    logger.info("Starting application initialization...")
    try:
        # Initialize data and model
        logger.info("Initializing prediction model...")
        await prediction_service.initialize_model()
        
        if prediction_service.is_initialized:
            logger.info("SUCCESS: Prediction model initialized successfully")
            print("SUCCESS: Prediction model initialized successfully")
        else:
            logger.warning("WARNING: Prediction model initialization completed but model is not ready")
            print("WARNING: Prediction model initialization completed but model is not ready")
        
        # Start daily update scheduler
        scheduler_service.start_scheduler()
        logger.info("SUCCESS: Daily update scheduler started")
        print("SUCCESS: Daily update scheduler started")
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"ERROR: Error during startup: {e}")
        logger.error(f"Traceback: {error_trace}")
        print(f"ERROR: Error during startup: {e}")
        print(f"Traceback: {error_trace}")

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

@app.get("/model-status")
async def get_model_status():
    """Get the status of the prediction model"""
    try:
        status = {
            "is_initialized": prediction_service.is_initialized,
            "is_trained": prediction_service.predictor.is_trained if prediction_service.predictor else False,
            "has_models": len(prediction_service.predictor.models) > 0 if prediction_service.predictor else False,
            "has_training_data": False,
            "timestamp": datetime.now().isoformat()
        }
        
        # Check if training data exists
        try:
            training_data = prediction_service.data_service.get_training_data()
            status["has_training_data"] = len(training_data) > 0
            status["training_data_count"] = len(training_data)
        except:
            pass
        
        return JSONResponse(
            content=status,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            }
        )
    except Exception as e:
        logger.error(f"Error getting model status: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            }
        )

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
        logger.info(f"Prediction request: {request.home_team} vs {request.away_team}")
        
        # Check if model is initialized, if not try to initialize
        if not prediction_service.is_initialized:
            logger.warning("Model not initialized, attempting to initialize now...")
            try:
                await prediction_service.initialize_model()
                if not prediction_service.is_initialized:
                    logger.error("Failed to initialize model after retry")
                    # Get more details about why it failed
                    try:
                        training_data = prediction_service.data_service.get_training_data()
                        training_count = len(training_data) if training_data is not None else 0
                        detail_msg = f"Prediction model is not ready. Training data: {training_count} records. Please check /model-status endpoint or server logs."
                    except:
                        detail_msg = "Prediction model is not ready. Please check /model-status endpoint or server logs."
                    
                    raise HTTPException(
                        status_code=503,
                        detail=detail_msg
                    )
                logger.info("Model initialized successfully on demand")
            except HTTPException:
                # Re-raise HTTP exceptions
                raise
            except RuntimeError as init_error:
                # RuntimeError from initialize_model contains detailed error info
                logger.error(f"Error initializing model on demand: {init_error}", exc_info=True)
                raise HTTPException(
                    status_code=503,
                    detail=f"Prediction model initialization failed: {str(init_error)}. Please check server logs for details."
                )
            except Exception as init_error:
                logger.error(f"Unexpected error initializing model on demand: {init_error}", exc_info=True)
                raise HTTPException(
                    status_code=503,
                    detail=f"Prediction model initialization failed: {str(init_error)}. Please check server logs."
                )
        
        prediction = await prediction_service.predict_match(
            request.home_team,
            request.away_team,
            request.season
        )
        
        logger.info(f"Prediction successful: {prediction.get('home_win_probability', 0):.2f}% home win")
        return prediction
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        logger.error(f"ValueError in prediction: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error making prediction: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate prediction: {str(e)}"
        )

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

@app.post("/admin/initialize-model")
async def manual_initialize_model():
    """Manually trigger model initialization"""
    try:
        logger.info("Manual model initialization requested...")
        await prediction_service.initialize_model()
        
        if prediction_service.is_initialized:
            return {
                "status": "success",
                "message": "Model initialized successfully",
                "is_initialized": True,
                "is_trained": prediction_service.predictor.is_trained,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "error",
                "message": "Model initialization completed but model is not ready",
                "is_initialized": False,
                "is_trained": prediction_service.predictor.is_trained if prediction_service.predictor else False,
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Error initializing model: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Error initializing model: {str(e)}",
                "detail": error_trace,
                "timestamp": datetime.now().isoformat()
            },
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
