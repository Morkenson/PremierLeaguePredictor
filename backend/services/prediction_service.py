from typing import Dict, List, Any
import asyncio

from models.match_predictor_simple import MatchPredictor
from services.data_service import DataService

class PredictionService:
    def __init__(self):
        self.predictor = MatchPredictor()
        self.data_service = DataService()
        self.is_initialized = False
    
    async def initialize_model(self):
        """Initialize the prediction model"""
        error_messages = []
        
        try:
            # Initialize data service
            print("Step 1: Initializing data service...")
            await self.data_service.initialize_data()
            print("Step 1: Data service initialized")
            
            # Get training data
            print("Step 2: Getting training data...")
            training_data = self.data_service.get_training_data()
            print(f"Step 2: Got {len(training_data)} training records")
            
            if len(training_data) > 0:
                # Train the model
                print("Step 3: Training model...")
                try:
                    self.predictor.train_models(training_data)
                    if self.predictor.is_trained:
                        self.is_initialized = True
                        print("SUCCESS: Model trained successfully")
                        return  # Success, exit early
                    else:
                        error_msg = "Model training completed but model is not marked as trained"
                        print(f"ERROR: {error_msg}")
                        error_messages.append(error_msg)
                except Exception as train_error:
                    import traceback
                    error_trace = traceback.format_exc()
                    error_msg = f"Error during model training: {str(train_error)}"
                    print(f"ERROR: {error_msg}")
                    print(f"Traceback: {error_trace}")
                    error_messages.append(error_msg)
            else:
                error_msg = "No training data available"
                print(f"ERROR: {error_msg}")
                error_messages.append(error_msg)
            
            # Try to load existing model as fallback
            print("Step 4: Attempting to load existing model...")
            try:
                self.predictor.load_models()
                if self.predictor.is_trained:
                    self.is_initialized = True
                    print("SUCCESS: Loaded existing model")
                    return  # Success, exit early
                else:
                    error_msg = "Loaded model but it is not marked as trained"
                    print(f"ERROR: {error_msg}")
                    error_messages.append(error_msg)
            except FileNotFoundError:
                error_msg = "No saved model found on disk"
                print(f"ERROR: {error_msg}")
                error_messages.append(error_msg)
            except Exception as load_error:
                import traceback
                error_trace = traceback.format_exc()
                error_msg = f"Error loading existing model: {str(load_error)}"
                print(f"ERROR: {error_msg}")
                print(f"Traceback: {error_trace}")
                error_messages.append(error_msg)
                
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            error_msg = f"Error initializing model: {str(e)}"
            print(f"ERROR: {error_msg}")
            print(f"Traceback: {error_trace}")
            error_messages.append(error_msg)
            
            # Try to load existing model as last resort
            print("Attempting to load existing model as last resort...")
            try:
                self.predictor.load_models()
                if self.predictor.is_trained:
                    self.is_initialized = True
                    print("SUCCESS: Loaded existing model after initialization error")
                    return  # Success, exit early
            except Exception as load_error:
                error_msg = f"Could not load existing model: {str(load_error)}"
                print(f"ERROR: {error_msg}")
                error_messages.append(error_msg)
        
        # If we get here, initialization failed
        if not self.is_initialized:
            error_summary = "; ".join(error_messages) if error_messages else "Unknown error"
            raise RuntimeError(f"Model initialization failed: {error_summary}")
    
    async def predict_match(self, home_team: str, away_team: str, season: str = "2023-24") -> Dict[str, Any]:
        """Predict the outcome of a specific match"""
        if not self.is_initialized:
            raise ValueError("Model not initialized. Please wait for the model to finish loading.")
        
        if not self.predictor.is_trained:
            raise ValueError("Model not trained. Please wait for the model to finish training.")
        
        try:
            # Get training data for feature creation
            training_data = self.data_service.get_training_data()
            
            if training_data.empty or len(training_data) == 0:
                raise ValueError("No training data available. Cannot make predictions.")
            
            # Validate team names exist in training data
            all_teams = set(training_data['home_team'].unique()) | set(training_data['away_team'].unique())
            if home_team not in all_teams:
                raise ValueError(f"Team '{home_team}' not found in training data. Available teams: {sorted(all_teams)}")
            if away_team not in all_teams:
                raise ValueError(f"Team '{away_team}' not found in training data. Available teams: {sorted(all_teams)}")
            
            # Make prediction
            prediction = self.predictor.predict_match(home_team, away_team, training_data)
            
            # Format response
            return {
                'home_team': home_team,
                'away_team': away_team,
                'home_win_probability': round(prediction['home_win_probability'], 3),
                'draw_probability': round(prediction['draw_probability'], 3),
                'away_win_probability': round(prediction['away_win_probability'], 3),
                'predicted_score': prediction['predicted_score'],
                'confidence': round(prediction['confidence'], 3),
                'key_factors': prediction['key_factors']
            }
            
        except ValueError as e:
            # Re-raise ValueError as-is
            raise
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Error making prediction: {e}")
            print(f"Traceback: {error_trace}")
            raise ValueError(f"Error making prediction: {str(e)}")
    
    async def get_batch_predictions(self) -> List[Dict[str, Any]]:
        """Get predictions for all upcoming fixtures"""
        if not self.is_initialized:
            raise ValueError("Model not initialized")
        
        try:
            # Get upcoming fixtures
            fixtures = await self.data_service.get_upcoming_fixtures()
            
            predictions = []
            for fixture in fixtures:
                try:
                    prediction = await self.predict_match(
                        fixture['home_team'],
                        fixture['away_team']
                    )
                    prediction['date'] = fixture['date']
                    predictions.append(prediction)
                except Exception as e:
                    print(f"Error predicting {fixture['home_team']} vs {fixture['away_team']}: {e}")
                    continue
            
            return predictions
            
        except Exception as e:
            raise ValueError(f"Error getting batch predictions: {e}")
    