import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
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
        try:
            # Initialize data service
            await self.data_service.initialize_data()
            
            # Get training data
            training_data = self.data_service.get_training_data()
            
            if len(training_data) > 0:
                # Train the model
                self.predictor.train_models(training_data)
                self.is_initialized = True
                print("SUCCESS: Model trained successfully")
            else:
                print("ERROR: No training data available")
                
        except Exception as e:
            print(f"ERROR: Error initializing model: {e}")
            # Try to load existing model
            try:
                self.predictor.load_models()
                self.is_initialized = True
                print("SUCCESS: Loaded existing model")
            except:
                print("ERROR: Could not load existing model")
    
    async def predict_match(self, home_team: str, away_team: str, season: str = "2023-24") -> Dict[str, Any]:
        """Predict the outcome of a specific match"""
        if not self.is_initialized:
            raise ValueError("Model not initialized")
        
        try:
            # Get training data for feature creation
            training_data = self.data_service.get_training_data()
            
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
            
        except Exception as e:
            raise ValueError(f"Error making prediction: {e}")
    
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
    
    async def get_prediction_analysis(self, home_team: str, away_team: str) -> Dict[str, Any]:
        """Get detailed analysis for a match prediction"""
        if not self.is_initialized:
            raise ValueError("Model not initialized")
        
        try:
            # Get team stats
            home_stats = await self.data_service.get_team_stats(home_team)
            away_stats = await self.data_service.get_team_stats(away_team)
            
            # Get prediction
            prediction = await self.predict_match(home_team, away_team)
            
            # Calculate additional insights
            home_advantage = self._calculate_home_advantage(home_stats)
            form_comparison = self._compare_form(home_stats, away_stats)
            head_to_head = await self._get_head_to_head(home_team, away_team)
            
            return {
                'prediction': prediction,
                'home_team_stats': home_stats,
                'away_team_stats': away_stats,
                'home_advantage': home_advantage,
                'form_comparison': form_comparison,
                'head_to_head': head_to_head,
                'analysis': self._generate_analysis(prediction, home_stats, away_stats)
            }
            
        except Exception as e:
            raise ValueError(f"Error getting prediction analysis: {e}")
    
    def _calculate_home_advantage(self, home_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate home advantage metrics"""
        home_record = home_stats['home_record']
        total_home_matches = home_record['wins'] + home_record['draws'] + home_record['losses']
        
        if total_home_matches > 0:
            home_win_rate = home_record['wins'] / total_home_matches
            home_points_per_game = (home_record['wins'] * 3 + home_record['draws']) / total_home_matches
        else:
            home_win_rate = 0
            home_points_per_game = 0
        
        return {
            'win_rate': round(home_win_rate, 3),
            'points_per_game': round(home_points_per_game, 2),
            'total_matches': total_home_matches
        }
    
    def _compare_form(self, home_stats: Dict[str, Any], away_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Compare recent form between teams"""
        home_form = home_stats['form']
        away_form = away_stats['form']
        
        home_form_points = sum(3 if result == 'W' else 1 if result == 'D' else 0 for result in home_form)
        away_form_points = sum(3 if result == 'W' else 1 if result == 'D' else 0 for result in away_form)
        
        return {
            'home_form': home_form,
            'away_form': away_form,
            'home_form_points': home_form_points,
            'away_form_points': away_form_points,
            'form_advantage': 'home' if home_form_points > away_form_points else 'away' if away_form_points > home_form_points else 'even'
        }
    
    async def _get_head_to_head(self, home_team: str, away_team: str) -> Dict[str, Any]:
        """Get head-to-head record between teams"""
        training_data = self.data_service.get_training_data()
        
        h2h_matches = training_data[
            ((training_data['home_team'] == home_team) & (training_data['away_team'] == away_team)) |
            ((training_data['home_team'] == away_team) & (training_data['away_team'] == home_team))
        ]
        
        if len(h2h_matches) == 0:
            return {'total_matches': 0, 'home_wins': 0, 'away_wins': 0, 'draws': 0}
        
        home_wins = 0
        away_wins = 0
        draws = 0
        
        for _, match in h2h_matches.iterrows():
            if match['home_team'] == home_team:
                if match['result'] == 'H':
                    home_wins += 1
                elif match['result'] == 'A':
                    away_wins += 1
                else:
                    draws += 1
            else:
                if match['result'] == 'A':
                    home_wins += 1
                elif match['result'] == 'H':
                    away_wins += 1
                else:
                    draws += 1
        
        return {
            'total_matches': len(h2h_matches),
            'home_wins': home_wins,
            'away_wins': away_wins,
            'draws': draws,
            'home_win_rate': round(home_wins / len(h2h_matches), 3) if len(h2h_matches) > 0 else 0
        }
    
    def _generate_analysis(self, prediction: Dict[str, Any], home_stats: Dict[str, Any], away_stats: Dict[str, Any]) -> List[str]:
        """Generate analysis insights"""
        analysis = []
        
        # Probability analysis
        max_prob = max(prediction['home_win_probability'], prediction['draw_probability'], prediction['away_win_probability'])
        
        if max_prob == prediction['home_win_probability']:
            analysis.append(f"{prediction['home_team']} are favorites to win ({prediction['home_win_probability']:.1%} probability)")
        elif max_prob == prediction['away_win_probability']:
            analysis.append(f"{prediction['away_team']} are favorites to win ({prediction['away_win_probability']:.1%} probability)")
        else:
            analysis.append(f"The match is expected to be close, with a draw being the most likely outcome ({prediction['draw_probability']:.1%} probability)")
        
        # Form analysis
        home_form_points = sum(3 if result == 'W' else 1 if result == 'D' else 0 for result in home_stats['form'])
        away_form_points = sum(3 if result == 'W' else 1 if result == 'D' else 0 for result in away_stats['form'])
        
        if home_form_points > away_form_points:
            analysis.append(f"{prediction['home_team']} have better recent form ({home_form_points} points vs {away_form_points})")
        elif away_form_points > home_form_points:
            analysis.append(f"{prediction['away_team']} have better recent form ({away_form_points} points vs {home_form_points})")
        
        # Goal scoring analysis
        if home_stats['goals_for'] > away_stats['goals_for']:
            analysis.append(f"{prediction['home_team']} have scored more goals this season ({home_stats['goals_for']} vs {away_stats['goals_for']})")
        elif away_stats['goals_for'] > home_stats['goals_for']:
            analysis.append(f"{prediction['away_team']} have scored more goals this season ({away_stats['goals_for']} vs {home_stats['goals_for']})")
        
        return analysis
