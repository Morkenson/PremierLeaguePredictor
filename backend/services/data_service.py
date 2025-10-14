import pandas as pd
import numpy as np
import requests
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
import aiohttp
from dataclasses import dataclass

@dataclass
class Team:
    name: str
    id: int
    short_name: str = ""
    logo_url: str = ""

@dataclass
class Match:
    home_team: str
    away_team: str
    date: datetime
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    status: str = "scheduled"

class DataService:
    def __init__(self):
        self.base_url = "https://api.football-data.org/v4"
        self.headers = {
            "X-Auth-Token": "YOUR_API_KEY_HERE",  # Replace with actual API key
            "Content-Type": "application/json"
        }
        self.teams_data = {}
        self.matches_data = {}
        
    async def initialize_data(self):
        """Initialize data by fetching from API or using sample data"""
        try:
            # Try to fetch real data first
            await self._fetch_real_data()
        except Exception as e:
            print(f"Could not fetch real data: {e}")
            print("Using sample data instead...")
            self._create_sample_data()
    
    async def _fetch_real_data(self):
        """Fetch real Premier League data from API"""
        async with aiohttp.ClientSession() as session:
            # Fetch teams
            teams_url = f"{self.base_url}/competitions/PL/teams"
            async with session.get(teams_url, headers=self.headers) as response:
                if response.status == 200:
                    teams_data = await response.json()
                    self.teams_data = {team['name']: team for team in teams_data['teams']}
            
            # Fetch matches
            matches_url = f"{self.base_url}/competitions/PL/matches"
            async with session.get(matches_url, headers=self.headers) as response:
                if response.status == 200:
                    matches_data = await response.json()
                    self.matches_data = matches_data['matches']
    
    def _create_sample_data(self):
        """Create sample Premier League data for demonstration"""
        # Sample teams
        teams = [
            "Manchester City", "Arsenal", "Liverpool", "Chelsea", "Manchester United",
            "Tottenham", "Newcastle", "Brighton", "West Ham", "Aston Villa",
            "Crystal Palace", "Fulham", "Brentford", "Wolves", "Everton",
            "Nottingham Forest", "Luton", "Burnley", "Sheffield United", "Bournemouth"
        ]
        
        self.teams_data = {
            team: {
                'id': i + 1,
                'name': team,
                'shortName': team.split()[-1],
                'crest': f"https://example.com/logos/{team.lower().replace(' ', '_')}.png"
            }
            for i, team in enumerate(teams)
        }
        
        # Generate sample matches
        self.matches_data = self._generate_sample_matches(teams)
    
    def _generate_sample_matches(self, teams: List[str]) -> List[Dict]:
        """Generate sample match data"""
        matches = []
        np.random.seed(42)  # For reproducible results
        
        # Generate matches for current season
        start_date = datetime(2023, 8, 12)  # Premier League start date
        
        for week in range(38):  # 38 gameweeks
            week_matches = []
            remaining_teams = teams.copy()
            
            # Create fixtures for this week
            while len(remaining_teams) >= 2:
                home_team = remaining_teams.pop(np.random.randint(len(remaining_teams)))
                away_team = remaining_teams.pop(np.random.randint(len(remaining_teams)))
                
                match_date = start_date + timedelta(weeks=week, days=np.random.randint(7))
                
                # Determine if match is completed
                is_completed = match_date < datetime.now()
                
                if is_completed:
                    # Generate realistic scores based on team strength
                    home_strength = self._get_team_strength(home_team)
                    away_strength = self._get_team_strength(away_team)
                    
                    home_score = np.random.poisson(1.5 + home_strength)
                    away_score = np.random.poisson(1.2 + away_strength)
                    
                    # Determine result
                    if home_score > away_score:
                        result = 'H'
                    elif away_score > home_score:
                        result = 'A'
                    else:
                        result = 'D'
                else:
                    home_score = None
                    away_score = None
                    result = None
                
                match = {
                    'homeTeam': {'name': home_team},
                    'awayTeam': {'name': away_team},
                    'utcDate': match_date.isoformat(),
                    'status': 'FINISHED' if is_completed else 'SCHEDULED',
                    'score': {
                        'fullTime': {
                            'home': home_score,
                            'away': away_score
                        }
                    },
                    'result': result
                }
                
                matches.append(match)
        
        return matches
    
    def _get_team_strength(self, team: str) -> float:
        """Get team strength for realistic score generation"""
        strength_map = {
            'Manchester City': 0.8,
            'Arsenal': 0.7,
            'Liverpool': 0.6,
            'Chelsea': 0.5,
            'Manchester United': 0.4,
            'Tottenham': 0.3,
            'Newcastle': 0.2,
            'Brighton': 0.1,
            'West Ham': 0.0,
            'Aston Villa': -0.1,
            'Crystal Palace': -0.2,
            'Fulham': -0.3,
            'Brentford': -0.4,
            'Wolves': -0.5,
            'Everton': -0.6,
            'Nottingham Forest': -0.7,
            'Luton': -0.8,
            'Burnley': -0.9,
            'Sheffield United': -1.0,
            'Bournemouth': -1.1
        }
        return strength_map.get(team, 0.0)
    
    async def get_teams(self) -> List[Dict[str, Any]]:
        """Get list of all Premier League teams"""
        if not self.teams_data:
            await self.initialize_data()
        
        return [
            {
                'name': team_data['name'],
                'id': team_data['id'],
                'short_name': team_data.get('shortName', ''),
                'logo_url': team_data.get('crest', '')
            }
            for team_data in self.teams_data.values()
        ]
    
    async def get_team_stats(self, team_name: str, season: str = "2023-24") -> Dict[str, Any]:
        """Get detailed statistics for a specific team"""
        if not self.matches_data:
            await self.initialize_data()
        
        # Filter matches for the team
        team_matches = [
            match for match in self.matches_data
            if (match['homeTeam']['name'] == team_name or 
                match['awayTeam']['name'] == team_name) and
               match['status'] == 'FINISHED'
        ]
        
        wins = draws = losses = 0
        goals_for = goals_against = 0
        home_wins = home_draws = home_losses = 0
        away_wins = away_draws = away_losses = 0
        form = []
        
        for match in team_matches[-10:]:  # Last 10 matches for form
            is_home = match['homeTeam']['name'] == team_name
            
            if is_home:
                team_score = match['score']['fullTime']['home']
                opp_score = match['score']['fullTime']['away']
            else:
                team_score = match['score']['fullTime']['away']
                opp_score = match['score']['fullTime']['home']
            
            goals_for += team_score
            goals_against += opp_score
            
            if team_score > opp_score:
                wins += 1
                form.append('W')
                if is_home:
                    home_wins += 1
                else:
                    away_wins += 1
            elif team_score < opp_score:
                losses += 1
                form.append('L')
                if is_home:
                    home_losses += 1
                else:
                    away_losses += 1
            else:
                draws += 1
                form.append('D')
                if is_home:
                    home_draws += 1
                else:
                    away_draws += 1
        
        points = wins * 3 + draws
        
        return {
            'team_name': team_name,
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'goals_for': goals_for,
            'goals_against': goals_against,
            'points': points,
            'form': form[-5:] if form else [],  # Last 5 results
            'home_record': {
                'wins': home_wins,
                'draws': home_draws,
                'losses': home_losses
            },
            'away_record': {
                'wins': away_wins,
                'draws': away_draws,
                'losses': away_losses
            }
        }
    
    async def get_upcoming_fixtures(self) -> List[Dict[str, Any]]:
        """Get upcoming Premier League fixtures"""
        if not self.matches_data:
            await self.initialize_data()
        
        upcoming_matches = [
            match for match in self.matches_data
            if match['status'] == 'SCHEDULED'
        ]
        
        # Sort by date
        upcoming_matches.sort(key=lambda x: x['utcDate'])
        
        return [
            {
                'home_team': match['homeTeam']['name'],
                'away_team': match['awayTeam']['name'],
                'date': match['utcDate'],
                'status': match['status']
            }
            for match in upcoming_matches[:10]  # Next 10 fixtures
        ]
    
    async def get_league_table(self, season: str = "2023-24") -> List[Dict[str, Any]]:
        """Get current Premier League table"""
        if not self.matches_data:
            await self.initialize_data()
        
        team_stats = {}
        
        # Calculate stats for all teams
        for team_name in self.teams_data.keys():
            stats = await self.get_team_stats(team_name, season)
            team_stats[team_name] = stats
        
        # Sort by points, then goal difference
        sorted_teams = sorted(
            team_stats.items(),
            key=lambda x: (x[1]['points'], x[1]['goals_for'] - x[1]['goals_against']),
            reverse=True
        )
        
        table = []
        for position, (team_name, stats) in enumerate(sorted_teams, 1):
            table.append({
                'position': position,
                'team_name': team_name,
                'played': stats['wins'] + stats['draws'] + stats['losses'],
                'wins': stats['wins'],
                'draws': stats['draws'],
                'losses': stats['losses'],
                'goals_for': stats['goals_for'],
                'goals_against': stats['goals_against'],
                'goal_difference': stats['goals_for'] - stats['goals_against'],
                'points': stats['points']
            })
        
        return table
    
    def get_training_data(self) -> pd.DataFrame:
        """Get training data for ML model"""
        if not self.matches_data:
            self._create_sample_data()
        
        training_data = []
        
        for match in self.matches_data:
            if match['status'] == 'FINISHED':
                # Determine result based on scores
                home_score = match['score']['fullTime']['home']
                away_score = match['score']['fullTime']['away']
                
                if home_score > away_score:
                    result = 'H'
                    home_result = 'W'
                    away_result = 'L'
                elif away_score > home_score:
                    result = 'A'
                    home_result = 'L'
                    away_result = 'W'
                else:
                    result = 'D'
                    home_result = 'D'
                    away_result = 'D'
                
                training_data.append({
                    'home_team': match['homeTeam']['name'],
                    'away_team': match['awayTeam']['name'],
                    'date': pd.to_datetime(match['utcDate']),
                    'season': '2023-24',
                    'home_score': home_score,
                    'away_score': away_score,
                    'result': result,
                    'home_result': home_result,
                    'away_result': away_result
                })
        
        return pd.DataFrame(training_data)
