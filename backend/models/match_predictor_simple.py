import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from joblib import dump, load
import os
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

class MatchPredictor:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_columns = []
        self.is_trained = False
        
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create advanced features for match prediction"""
        df = df.copy()
        
        # Validate required columns exist
        required_cols = ['home_team', 'away_team', 'home_score', 'away_score', 'home_result', 'away_result', 'date', 'season']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Ensure numeric columns are actually numeric
        if 'home_score' in df.columns:
            df['home_score'] = pd.to_numeric(df['home_score'], errors='coerce').fillna(0)
        if 'away_score' in df.columns:
            df['away_score'] = pd.to_numeric(df['away_score'], errors='coerce').fillna(0)
        
        # Ensure date is datetime
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            # Fill any invalid dates with a default date
            if df['date'].isna().any():
                df['date'] = df['date'].fillna(pd.Timestamp('2023-08-01'))
        
        # Ensure season is string
        if 'season' in df.columns:
            df['season'] = df['season'].astype(str)
        
        # Convert results to numeric FIRST (before any rolling operations)
        def result_to_numeric(result):
            if pd.isna(result) or result is None:
                return 0.0
            if result == 'W':
                return 1.0
            elif result == 'D':
                return 0.5
            elif result == 'L':
                return 0.0
            return 0.0
        
        df['home_result_numeric'] = df['home_result'].apply(result_to_numeric)
        df['away_result_numeric'] = df['away_result'].apply(result_to_numeric)
        
        # Basic team performance metrics
        df['home_goals_scored'] = df.groupby('home_team')['home_score'].transform('mean')
        df['away_goals_scored'] = df.groupby('away_team')['away_score'].transform('mean')
        df['home_goals_conceded'] = df.groupby('home_team')['away_score'].transform('mean')
        df['away_goals_conceded'] = df.groupby('away_team')['home_score'].transform('mean')
        
        # Form metrics (last 5 games) - use numeric results for rolling
        # Calculate form points from numeric results (W=1.0, D=0.5, L=0.0)
        # Average form points over last 5 games
        df['home_form'] = df.groupby('home_team')['home_result_numeric'].transform(
            lambda x: x.rolling(5, min_periods=1).mean() * 2  # Scale to match original form points (0-2 range)
        )
        df['away_form'] = df.groupby('away_team')['away_result_numeric'].transform(
            lambda x: x.rolling(5, min_periods=1).mean() * 2  # Scale to match original form points (0-2 range)
        )
        
        # Head-to-head record
        df['h2h_home_wins'] = df.apply(
            lambda row: self._get_h2h_wins(row['home_team'], row['away_team'], df, 'home'), axis=1
        )
        df['h2h_away_wins'] = df.apply(
            lambda row: self._get_h2h_wins(row['away_team'], row['home_team'], df, 'away'), axis=1
        )
        
        # Home/Away advantage
        df['home_advantage'] = df.groupby('home_team')['home_result_numeric'].transform('mean')
        df['away_advantage'] = df.groupby('away_team')['away_result_numeric'].transform('mean')
        
        # Goal difference trends
        df['home_goal_diff'] = df['home_goals_scored'] - df['home_goals_conceded']
        df['away_goal_diff'] = df['away_goals_scored'] - df['away_goals_conceded']
        
        # Recent performance (last 10 games) - use numeric conversion
        df['home_recent_performance'] = df.groupby('home_team')['home_result_numeric'].transform(
            lambda x: x.rolling(10, min_periods=1).mean()
        )
        df['away_recent_performance'] = df.groupby('away_team')['away_result_numeric'].transform(
            lambda x: x.rolling(10, min_periods=1).mean()
        )
        
        # Season progression features - ensure date is datetime before ranking
        if 'date' in df.columns and not df['date'].isna().all():
            try:
                df['matchday'] = df.groupby('season')['date'].rank(method='dense')
            except Exception:
                # Fallback if ranking fails
                df['matchday'] = df.groupby('season').cumcount() + 1
        else:
            df['matchday'] = df.groupby('season').cumcount() + 1
        
        df['home_matches_played'] = df.groupby(['home_team', 'season']).cumcount() + 1
        df['away_matches_played'] = df.groupby(['away_team', 'season']).cumcount() + 1
        
        # Market value and squad strength (simulated)
        df['home_squad_strength'] = df['home_team'].map(self._get_squad_strength)
        df['away_squad_strength'] = df['away_team'].map(self._get_squad_strength)
        
        return df
    
    def _calculate_form_points(self, results: pd.Series) -> float:
        """Calculate form points from recent results"""
        if len(results) == 0:
            return 0.0
        
        points = 0
        for result in results:
            if result == 'W':
                points += 3
            elif result == 'D':
                points += 1
        
        return points / len(results) if len(results) > 0 else 0.0
    
    def _get_h2h_wins(self, team1: str, team2: str, df: pd.DataFrame, venue: str) -> int:
        """Get head-to-head wins between two teams"""
        if venue == 'home':
            mask = (df['home_team'] == team1) & (df['away_team'] == team2)
            return (df[mask]['home_result'] == 'W').sum()
        else:
            mask = (df['home_team'] == team2) & (df['away_team'] == team1)
            return (df[mask]['away_result'] == 'W').sum()
    
    def _get_squad_strength(self, team: str) -> float:
        """Simulate squad strength based on team name (in real app, use actual data)"""
        # This is a simplified version - in production, use actual squad values
        strength_map = {
            'Manchester City': 0.95,
            'Arsenal': 0.90,
            'Liverpool': 0.88,
            'Chelsea': 0.85,
            'Manchester United': 0.82,
            'Tottenham': 0.80,
            'Newcastle': 0.75,
            'Brighton': 0.70,
            'West Ham': 0.68,
            'Aston Villa': 0.65,
            'Crystal Palace': 0.60,
            'Fulham': 0.58,
            'Brentford': 0.55,
            'Wolves': 0.52,
            'Everton': 0.50,
            'Nottingham Forest': 0.48,
            'Luton': 0.45,
            'Burnley': 0.42,
            'Sheffield United': 0.40,
            'Bournemouth': 0.38
        }
        return strength_map.get(team, 0.50)
    
    def prepare_training_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare data for training"""
        # Create features
        df_with_features = self.create_features(df)
        
        # Select feature columns
        feature_cols = [
            'home_goals_scored', 'away_goals_scored', 'home_goals_conceded', 'away_goals_conceded',
            'home_form', 'away_form', 'h2h_home_wins', 'h2h_away_wins',
            'home_advantage', 'away_advantage', 'home_goal_diff', 'away_goal_diff',
            'home_recent_performance', 'away_recent_performance',
            'home_squad_strength', 'away_squad_strength'
        ]
        
        self.feature_columns = feature_cols
        
        # Prepare features and target
        X = df_with_features[feature_cols].fillna(0)
        y = df_with_features['result']  # 'H', 'D', 'A'
        
        return X, y
    
    def train_models(self, df: pd.DataFrame):
        """Train ML models using ensemble approach"""
        try:
            X, y = self.prepare_training_data(df)
            
            # Validate we have enough data
            if len(X) == 0 or len(y) == 0:
                raise ValueError("No training data available after feature preparation")
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            self.scalers['main'] = scaler
            
            # Define models (simplified for Windows compatibility)
            models = {
                'random_forest': RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    min_samples_split=5,
                    min_samples_leaf=2,
                    random_state=42,
                    n_jobs=-1
                ),
                'gradient_boosting': GradientBoostingClassifier(
                    n_estimators=100,
                    learning_rate=0.1,
                    max_depth=6,
                    random_state=42
                )
            }
            
            # Train models
            model_scores = {}
            for name, model in models.items():
                print(f"Training {name}...")
                
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
                
                score = accuracy_score(y_test, y_pred)
                model_scores[name] = score
                self.models[name] = model
                
                print(f"{name} accuracy: {score:.4f}")
            
            # Train ensemble model
            ensemble_model = self._create_ensemble_model()
            ensemble_model.fit(X_train_scaled, y_train)
            ensemble_score = accuracy_score(y_test, ensemble_model.predict(X_test_scaled))
            self.models['ensemble'] = ensemble_model
            
            print(f"Ensemble accuracy: {ensemble_score:.4f}")
            print(f"Best individual model: {max(model_scores, key=model_scores.get)}")
            
            # Verify all models are trained
            if not all(name in self.models for name in ['random_forest', 'gradient_boosting', 'ensemble']):
                raise ValueError("Not all models were trained successfully")
            if 'main' not in self.scalers:
                raise ValueError("Scaler was not created")
            if not self.feature_columns:
                raise ValueError("Feature columns were not set")
            
            self.is_trained = True
            print(f"Model training completed successfully. is_trained = {self.is_trained}")
            
            # Save models
            self.save_models()
            
        except Exception as e:
            # Reset state on error
            self.is_trained = False
            import traceback
            error_trace = traceback.format_exc()
            print(f"Error during model training: {e}")
            print(f"Traceback: {error_trace}")
            raise
    
    def _create_ensemble_model(self):
        """Create ensemble model combining all trained models"""
        from sklearn.ensemble import VotingClassifier
        
        estimators = [
            ('rf', self.models['random_forest']),
            ('gb', self.models['gradient_boosting'])
        ]
        
        return VotingClassifier(estimators=estimators, voting='soft')
    
    def predict_match(self, home_team: str, away_team: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Predict match outcome"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        if 'ensemble' not in self.models:
            raise ValueError("Ensemble model not found. Model may not have been trained properly.")
        
        if not self.feature_columns:
            raise ValueError("Feature columns not defined. Model may not have been trained properly.")
        
        if df.empty or len(df) == 0:
            raise ValueError("Training data is empty. Cannot create features for prediction.")
        
        try:
            # Create match row with placeholder data
            match_data = {
                'home_team': home_team,
                'away_team': away_team,
                'date': pd.Timestamp.now(),
                'season': '2023-24',
                'home_score': 0,  # Placeholder - won't be used for prediction
                'away_score': 0,  # Placeholder - won't be used for prediction
                'result': 'D',  # Placeholder - won't be used for prediction
                'home_result': 'D',  # Placeholder - needed for feature calculation
                'away_result': 'D'  # Placeholder - needed for feature calculation
            }
            
            # Append new match to historical data for feature calculation
            # This ensures features like form, averages, etc. are calculated correctly
            match_df = pd.DataFrame([match_data])
            combined_df = pd.concat([df, match_df], ignore_index=True)
            
            # Create features using the combined dataset (this ensures historical context)
            combined_df_with_features = self.create_features(combined_df)
            
            # Extract only the features for the new match (last row)
            X = combined_df_with_features.iloc[[-1]][self.feature_columns].fillna(0)
            
            # Scale features if scaler exists
            if 'main' in self.scalers:
                X_scaled = self.scalers['main'].transform(X)
            else:
                X_scaled = X
            
            # Get predictions from ensemble model
            probabilities = self.models['ensemble'].predict_proba(X_scaled)[0]
            
            # Map probabilities to outcomes
            classes = self.models['ensemble'].classes_
            prob_dict = dict(zip(classes, probabilities))
            
            # Calculate predicted score based on team statistics and probabilities
            # Use actual team averages from training data for realistic predictions
            home_win_prob = prob_dict.get('H', 0.33)
            away_win_prob = prob_dict.get('A', 0.33)
            draw_prob = prob_dict.get('D', 0.33)
            
            # Get team statistics from features (calculated from training data)
            # These are the actual averages from historical matches
            home_avg_scored = float(X.iloc[0].get('home_goals_scored', 1.5))  # Average goals scored at home
            home_avg_conceded = float(X.iloc[0].get('home_goals_conceded', 1.2))  # Average goals conceded at home
            away_avg_scored = float(X.iloc[0].get('away_goals_scored', 1.2))  # Average goals scored away
            away_avg_conceded = float(X.iloc[0].get('away_goals_conceded', 1.5))  # Average goals conceded away
            
            # Calculate expected goals using Poisson-like model
            # Home team expected goals = (home attack avg + away defense weakness) * home advantage
            # Away team expected goals = (away attack avg + home defense weakness)
            
            # Calculate league averages for normalization
            league_avg_home_goals = df['home_score'].mean() if len(df) > 0 and 'home_score' in df.columns else 1.5
            league_avg_away_goals = df['away_score'].mean() if len(df) > 0 and 'away_score' in df.columns else 1.2
            
            # Home advantage typically adds ~0.3-0.4 goals
            home_advantage = 0.35
            
            # Expected goals calculation:
            # Home: (home team's avg goals scored) * (away team's defense factor) + home advantage
            # Away: (away team's avg goals scored) * (home team's defense factor)
            
            # Defense factor: if opponent concedes more, you score more
            away_defense_factor = away_avg_conceded / league_avg_away_goals if league_avg_away_goals > 0 else 1.0
            home_defense_factor = home_avg_conceded / league_avg_home_goals if league_avg_home_goals > 0 else 1.0
            
            # Base expected goals
            home_expected_goals = home_avg_scored * away_defense_factor + home_advantage
            away_expected_goals = away_avg_scored * home_defense_factor
            
            # Adjust based on win probabilities (favorite gets slight boost)
            prob_adjustment = 0.3
            if home_win_prob > 0.5:
                home_expected_goals += (home_win_prob - 0.5) * prob_adjustment
            elif away_win_prob > 0.5:
                away_expected_goals += (away_win_prob - 0.5) * prob_adjustment
            
            # Round to nearest integer
            home_goals = max(0, round(home_expected_goals))
            away_goals = max(0, round(away_expected_goals))
            
            # Ensure at least one goal if probabilities strongly suggest a result
            if home_win_prob > 0.6 and home_goals == 0:
                home_goals = 1
            if away_win_prob > 0.6 and away_goals == 0:
                away_goals = 1
            
            # Ensure realistic scores (not both 0, cap at 5)
            if home_goals == 0 and away_goals == 0:
                if home_win_prob >= away_win_prob:
                    home_goals = 1
                else:
                    away_goals = 1
            
            home_goals = min(home_goals, 5)
            away_goals = min(away_goals, 5)
            
            return {
                'home_win_probability': prob_dict.get('H', 0.33),
                'draw_probability': prob_dict.get('D', 0.33),
                'away_win_probability': prob_dict.get('A', 0.33),
                'predicted_score': {'home': home_goals, 'away': away_goals},
                'confidence': max(probabilities),
                'key_factors': self._get_key_factors(home_team, away_team, X.iloc[0])
            }
        except KeyError as e:
            raise ValueError(f"Missing required data for prediction: {str(e)}")
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Error in predict_match: {e}")
            print(f"Traceback: {error_trace}")
            raise ValueError(f"Error making prediction: {str(e)}")
    
    def _get_key_factors(self, home_team: str, away_team: str, features: pd.Series) -> List[str]:
        """Get key factors influencing the prediction"""
        factors = []
        
        if features['home_form'] > features['away_form']:
            factors.append(f"{home_team} has better recent form")
        
        if features['home_advantage'] > 0.5:
            factors.append(f"{home_team} has strong home record")
        
        if features['home_squad_strength'] > features['away_squad_strength']:
            factors.append(f"{home_team} has stronger squad")
        
        if features['h2h_home_wins'] > features['h2h_away_wins']:
            factors.append(f"{home_team} has better head-to-head record")
        
        return factors[:3]  # Return top 3 factors
    
    def save_models(self):
        """Save trained models to disk"""
        # Get the directory where this file is located (backend/models/)
        # Then go up one level to backend/ and create models/ there
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(current_dir)  # Go up from models/ to backend/
        models_dir = os.path.join(backend_dir, 'models')
        os.makedirs(models_dir, exist_ok=True)
        
        for name, model in self.models.items():
            model_path = os.path.join(models_dir, f'{name}_model.joblib')
            dump(model, model_path)
        
        dump(self.scalers['main'], os.path.join(models_dir, 'scaler.joblib'))
        dump(self.feature_columns, os.path.join(models_dir, 'feature_columns.joblib'))
        
        print(f"Models saved successfully to {models_dir}")
    
    def load_models(self):
        """Load trained models from disk"""
        try:
            # Get the directory where this file is located (backend/models/)
            # Then go up one level to backend/ and look for models/ there
            current_dir = os.path.dirname(os.path.abspath(__file__))
            backend_dir = os.path.dirname(current_dir)  # Go up from models/ to backend/
            models_dir = os.path.join(backend_dir, 'models')
            
            # Check if models directory exists
            if not os.path.exists(models_dir):
                raise FileNotFoundError(f"Models directory does not exist: {models_dir}")
            
            # Load all required models
            missing_files = []
            for name in ['random_forest', 'gradient_boosting', 'ensemble']:
                model_path = os.path.join(models_dir, f'{name}_model.joblib')
                if not os.path.exists(model_path):
                    missing_files.append(model_path)
                else:
                    self.models[name] = load(model_path)
                    print(f"Loaded {name} model from {model_path}")
            
            # Check for required files
            scaler_path = os.path.join(models_dir, 'scaler.joblib')
            feature_cols_path = os.path.join(models_dir, 'feature_columns.joblib')
            
            if not os.path.exists(scaler_path):
                missing_files.append(scaler_path)
            if not os.path.exists(feature_cols_path):
                missing_files.append(feature_cols_path)
            
            if missing_files:
                raise FileNotFoundError(f"Missing required model files: {', '.join(missing_files)}")
            
            # Load scaler and feature columns
            self.scalers['main'] = load(scaler_path)
            self.feature_columns = load(feature_cols_path)
            
            # Verify all required components are loaded
            if not all(name in self.models for name in ['random_forest', 'gradient_boosting', 'ensemble']):
                raise ValueError("Not all required models were loaded")
            if 'main' not in self.scalers:
                raise ValueError("Scaler was not loaded")
            if not self.feature_columns:
                raise ValueError("Feature columns were not loaded")
            
            self.is_trained = True
            print(f"Models loaded successfully from {models_dir}")
            
        except FileNotFoundError as e:
            print(f"No saved models found: {e}")
            self.is_trained = False
            raise  # Re-raise to let caller know it failed
        except Exception as e:
            print(f"Error loading models: {e}")
            self.is_trained = False
            raise  # Re-raise to let caller know it failed
