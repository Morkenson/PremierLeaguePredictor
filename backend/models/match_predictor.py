import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import xgboost as xgb
import lightgbm as lgb
from joblib import dump, load
import os
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

class MatchPredictor:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.label_encoders = {}
        self.feature_columns = []
        self.is_trained = False
        
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create advanced features for match prediction"""
        df = df.copy()
        
        # Basic team performance metrics
        df['home_goals_scored'] = df.groupby('home_team')['home_score'].transform('mean')
        df['away_goals_scored'] = df.groupby('away_team')['away_score'].transform('mean')
        df['home_goals_conceded'] = df.groupby('home_team')['away_score'].transform('mean')
        df['away_goals_conceded'] = df.groupby('away_team')['home_score'].transform('mean')
        
        # Form metrics (last 5 games)
        df['home_form'] = df.groupby('home_team')['home_result'].transform(
            lambda x: x.rolling(5, min_periods=1).apply(self._calculate_form_points)
        )
        df['away_form'] = df.groupby('away_team')['away_result'].transform(
            lambda x: x.rolling(5, min_periods=1).apply(self._calculate_form_points)
        )
        
        # Head-to-head record
        df['h2h_home_wins'] = df.apply(
            lambda row: self._get_h2h_wins(row['home_team'], row['away_team'], df, 'home'), axis=1
        )
        df['h2h_away_wins'] = df.apply(
            lambda row: self._get_h2h_wins(row['away_team'], row['home_team'], df, 'away'), axis=1
        )
        
        # Home/Away advantage
        df['home_advantage'] = df.groupby('home_team')['home_result'].transform('mean')
        df['away_advantage'] = df.groupby('away_team')['away_result'].transform('mean')
        
        # Goal difference trends
        df['home_goal_diff'] = df['home_goals_scored'] - df['home_goals_conceded']
        df['away_goal_diff'] = df['away_goals_scored'] - df['away_goals_conceded']
        
        # Recent performance (last 10 games)
        df['home_recent_performance'] = df.groupby('home_team')['home_result'].transform(
            lambda x: x.rolling(10, min_periods=1).mean()
        )
        df['away_recent_performance'] = df.groupby('away_team')['away_result'].transform(
            lambda x: x.rolling(10, min_periods=1).mean()
        )
        
        # Season progression features
        df['matchday'] = df.groupby('season')['date'].rank(method='dense')
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
        """Train multiple ML models using ensemble approach"""
        X, y = self.prepare_training_data(df)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        self.scalers['main'] = scaler
        
        # Define models
        models = {
            'random_forest': RandomForestClassifier(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            ),
            'gradient_boosting': GradientBoostingClassifier(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=8,
                random_state=42
            ),
            'xgboost': xgb.XGBClassifier(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=8,
                random_state=42,
                eval_metric='mlogloss'
            ),
            'lightgbm': lgb.LGBMClassifier(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=8,
                random_state=42,
                verbose=-1
            )
        }
        
        # Train models
        model_scores = {}
        for name, model in models.items():
            print(f"Training {name}...")
            
            if name in ['xgboost', 'lightgbm']:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
            else:
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
            
            score = accuracy_score(y_test, y_pred)
            model_scores[name] = score
            self.models[name] = model
            
            print(f"{name} accuracy: {score:.4f}")
        
        # Train ensemble model
        ensemble_model = self._create_ensemble_model()
        ensemble_model.fit(X_train, y_train)
        ensemble_score = accuracy_score(y_test, ensemble_model.predict(X_test))
        self.models['ensemble'] = ensemble_model
        
        print(f"Ensemble accuracy: {ensemble_score:.4f}")
        print(f"Best individual model: {max(model_scores, key=model_scores.get)}")
        
        self.is_trained = True
        
        # Save models
        self.save_models()
    
    def _create_ensemble_model(self):
        """Create ensemble model combining all trained models"""
        from sklearn.ensemble import VotingClassifier
        
        estimators = [
            ('rf', self.models['random_forest']),
            ('gb', self.models['gradient_boosting']),
            ('xgb', self.models['xgboost']),
            ('lgb', self.models['lightgbm'])
        ]
        
        return VotingClassifier(estimators=estimators, voting='soft')
    
    def predict_match(self, home_team: str, away_team: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Predict match outcome"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Create match row
        match_data = {
            'home_team': home_team,
            'away_team': away_team,
            'date': pd.Timestamp.now(),
            'season': '2023-24',
            'home_score': 0,  # Placeholder
            'away_score': 0,  # Placeholder
            'result': 'D'  # Placeholder
        }
        
        match_df = pd.DataFrame([match_data])
        match_df_with_features = self.create_features(match_df)
        
        # Prepare features
        X = match_df_with_features[self.feature_columns].fillna(0)
        
        # Get predictions from ensemble model
        probabilities = self.models['ensemble'].predict_proba(X)[0]
        
        # Map probabilities to outcomes
        classes = self.models['ensemble'].classes_
        prob_dict = dict(zip(classes, probabilities))
        
        # Calculate predicted score (simplified)
        home_goals = max(0, int(np.random.poisson(1.5 + prob_dict.get('H', 0.3))))
        away_goals = max(0, int(np.random.poisson(1.2 + prob_dict.get('A', 0.3))))
        
        return {
            'home_win_probability': prob_dict.get('H', 0.33),
            'draw_probability': prob_dict.get('D', 0.33),
            'away_win_probability': prob_dict.get('A', 0.33),
            'predicted_score': {'home': home_goals, 'away': away_goals},
            'confidence': max(probabilities),
            'key_factors': self._get_key_factors(home_team, away_team, X.iloc[0])
        }
    
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
        os.makedirs('models', exist_ok=True)
        
        for name, model in self.models.items():
            dump(model, f'models/{name}_model.joblib')
        
        dump(self.scalers['main'], 'models/scaler.joblib')
        dump(self.feature_columns, 'models/feature_columns.joblib')
        
        print("Models saved successfully")
    
    def load_models(self):
        """Load trained models from disk"""
        try:
            for name in ['random_forest', 'gradient_boosting', 'xgboost', 'lightgbm', 'ensemble']:
                self.models[name] = load(f'models/{name}_model.joblib')
            
            self.scalers['main'] = load('models/scaler.joblib')
            self.feature_columns = load('models/feature_columns.joblib')
            self.is_trained = True
            
            print("Models loaded successfully")
        except FileNotFoundError:
            print("No saved models found. Train the model first.")
            self.is_trained = False
