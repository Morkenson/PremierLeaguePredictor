import pandas as pd
import numpy as np
import requests
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
import aiohttp
from dataclasses import dataclass
import os
from dotenv import load_dotenv

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
        load_dotenv()
        self.base_url = "https://api.football-data.org/v4"
        api_key = os.getenv("FOOTBALL_DATA_API_KEY", "")
        self.headers = {
            "X-Auth-Token": api_key,
            "Content-Type": "application/json"
        }
        self.teams_data = {}
        self.matches_data = {}
        self.standings_data = {}
        self.competition_data = {}
        self.last_update = None
        self._initializing = False  # Add initialization lock
        self._init_lock = asyncio.Lock()  # Add async lock
        
    async def initialize_data(self):
        """Initialize data by fetching from API or using sample data"""
        # Prevent concurrent initialization
        if self._initializing:
            # Wait for ongoing initialization
            while self._initializing:
                await asyncio.sleep(0.1)
            return
        
        async with self._init_lock:
            if self._initializing or self.matches_data:
                return  # Already initialized or initializing
            
            self._initializing = True
            try:
                # Try to fetch real data first
                await self._fetch_real_data()
            except Exception as e:
                print(f"Could not fetch real data: {e}")
                print("Using sample data instead...")
                self._create_sample_data()
            finally:
                self._initializing = False
    
    async def _fetch_real_data(self):
        """Fetch real Premier League data from API"""
        api_key = os.getenv("FOOTBALL_DATA_API_KEY", "")
        
        if not api_key or api_key == "":
            raise ValueError("No API key configured. Set FOOTBALL_DATA_API_KEY in environment variables.")
        
        async with aiohttp.ClientSession() as session:
            try:
                # Fetch competition info
                comp_url = f"{self.base_url}/competitions/PL"
                async with session.get(comp_url, headers=self.headers) as response:
                    if response.status == 200:
                        self.competition_data = await response.json()
                        print(f"✅ Loaded competition data: {self.competition_data.get('name', 'Premier League')}")
                    elif response.status == 403:
                        raise ValueError("Invalid API key or rate limit exceeded")
                    elif response.status == 429:
                        raise ValueError("Rate limit exceeded. Please wait before trying again.")
                
                # Fetch teams
                teams_url = f"{self.base_url}/competitions/PL/teams"
                async with session.get(teams_url, headers=self.headers) as response:
                    if response.status == 200:
                        teams_data = await response.json()
                        self.teams_data = {team['name']: team for team in teams_data['teams']}
                        print(f"✅ Loaded {len(self.teams_data)} teams from API")
                    elif response.status == 403:
                        raise ValueError("Invalid API key or rate limit exceeded")
                    elif response.status == 429:
                        raise ValueError("Rate limit exceeded. Please wait before trying again.")
                
                # Fetch matches
                matches_url = f"{self.base_url}/competitions/PL/matches"
                async with session.get(matches_url, headers=self.headers) as response:
                    if response.status == 200:
                        matches_data = await response.json()
                        self.matches_data = matches_data['matches']
                        print(f"✅ Loaded {len(self.matches_data)} matches from API")
                    elif response.status == 403:
                        raise ValueError("Invalid API key or rate limit exceeded")
                    elif response.status == 429:
                        raise ValueError("Rate limit exceeded. Please wait before trying again.")
                
                # Fetch standings
                standings_url = f"{self.base_url}/competitions/PL/standings"
                async with session.get(standings_url, headers=self.headers) as response:
                    if response.status == 200:
                        standings_data = await response.json()
                        if standings_data.get('standings'):
                            self.standings_data = standings_data['standings'][0]  # Get first standings table
                            print(f"✅ Loaded league standings from API")
                    # Don't fail if standings fail, it's optional
                    
            except aiohttp.ClientError as e:
                raise ConnectionError(f"Failed to connect to API: {e}")
            except Exception as e:
                raise Exception(f"Error fetching data from API: {e}")
            
            # Update last update timestamp
            self.last_update = datetime.now()
            print(f"✅ Data refresh completed at {self.last_update.isoformat()}")
    
    async def refresh_data(self):
        """Refresh all data from API"""
        try:
            print("🔄 Starting daily data refresh...")
            await self._fetch_real_data()
            print("✅ Daily data refresh completed successfully")
            return True
        except Exception as e:
            print(f"❌ Error during data refresh: {e}")
            print("⚠️  Keeping existing data, will retry on next scheduled update")
            return False
    
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
        now = datetime.now()
        
        for week in range(38):  # 38 gameweeks
            week_matches = []
            remaining_teams = teams.copy()
            
            # Create fixtures for this week
            while len(remaining_teams) >= 2:
                home_team = remaining_teams.pop(np.random.randint(len(remaining_teams)))
                away_team = remaining_teams.pop(np.random.randint(len(remaining_teams)))
                
                # Generate match date - for past matches use historical dates, for future use varied future dates
                if week < 20:  # First half of season - mostly in past
                    match_date = start_date + timedelta(weeks=week, days=np.random.randint(7))
                else:  # Second half - create varied future dates
                    days_from_now = (week - 20) * 7 + np.random.randint(0, 7) + np.random.randint(0, 3)
                    match_date = now + timedelta(days=days_from_now)
                    # Add random hours and minutes for variety
                    match_date = match_date.replace(
                        hour=np.random.randint(12, 21),  # Between 12 PM and 9 PM
                        minute=np.random.choice([0, 15, 30, 45])
                    )
                
                # Determine if match is completed
                is_completed = match_date < now
                
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
        if not self.teams_data and not self._initializing:
            await self.initialize_data()
        elif not self.teams_data:
            # If initializing, wait a bit then use sample data as fallback
            await asyncio.sleep(0.5)
            if not self.teams_data:
                self._create_sample_data()  # Quick fallback
        
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
        if not self.matches_data and not self._initializing:
            await self.initialize_data()
        elif not self.matches_data:
            # If initializing, wait a bit then use sample data as fallback
            await asyncio.sleep(0.5)
            if not self.matches_data:
                self._create_sample_data()  # Quick fallback
        
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
        # Initialize if needed, but don't block if it's already initializing
        if not self.matches_data and not self._initializing:
            await self.initialize_data()
        elif not self.matches_data:
            # If initializing, wait a bit then use sample data as fallback
            await asyncio.sleep(0.5)
            if not self.matches_data:
                self._create_sample_data()  # Quick fallback
        
        upcoming_matches = [
            match for match in self.matches_data
            if match.get('status') == 'SCHEDULED' or match.get('status') == 'TIMED'
        ]
        
        # Sort by date - handle both API format and sample data format
        def get_match_date(match):
            # Try different date field names
            date_str = match.get('utcDate') or match.get('date') or match.get('utc_date')
            if date_str:
                return date_str
            return '9999-12-31'  # Put items without dates at the end
        
        upcoming_matches.sort(key=get_match_date)
        
        fixtures = []
        for match in upcoming_matches[:10]:  # Next 10 fixtures
            # Get date from various possible field names
            date_str = match.get('utcDate') or match.get('date') or match.get('utc_date')
            
            # Ensure date is in ISO format with timezone
            if date_str and not date_str.endswith('Z') and '+' not in date_str:
                # If date doesn't have timezone, assume UTC and add Z
                if 'T' in date_str:
                    date_str = date_str + 'Z'
            
            # Get team names - handle both API format and sample format
            home_team = match.get('homeTeam', {}).get('name') if isinstance(match.get('homeTeam'), dict) else match.get('home_team', 'Unknown')
            away_team = match.get('awayTeam', {}).get('name') if isinstance(match.get('awayTeam'), dict) else match.get('away_team', 'Unknown')
            
            fixture = {
                'home_team': home_team,
                'away_team': away_team,
                'date': date_str or datetime.now().isoformat() + 'Z',  # Fallback to current time if no date
                'status': match.get('status', 'SCHEDULED')
            }
            
            fixtures.append(fixture)
            # Debug logging
            print(f"Fixture: {home_team} vs {away_team}, Date: {fixture['date']}")
        
        return fixtures
    
    async def get_league_table(self, season: str = "2023-24") -> List[Dict[str, Any]]:
        """Get current Premier League table - tries API first, falls back to calculated"""
        api_key = os.getenv("FOOTBALL_DATA_API_KEY", "")
        
        # Try to get standings from API first
        if api_key and api_key != "":
            try:
                return await self.get_league_standings_from_api(season)
            except Exception as e:
                print(f"Could not fetch standings from API: {e}, calculating from matches...")
        
        # Fall back to calculating from matches
        if not self.matches_data and not self._initializing:
            await self.initialize_data()
        elif not self.matches_data:
            # If initializing, wait a bit then use sample data as fallback
            await asyncio.sleep(0.5)
            if not self.matches_data:
                self._create_sample_data()  # Quick fallback
        
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
    
    async def get_league_standings_from_api(self, season: str = "2023-24") -> List[Dict[str, Any]]:
        """Get league standings directly from API"""
        api_key = os.getenv("FOOTBALL_DATA_API_KEY", "")
        if not api_key:
            raise ValueError("No API key configured")
        
        async with aiohttp.ClientSession() as session:
            standings_url = f"{self.base_url}/competitions/PL/standings"
            async with session.get(standings_url, headers=self.headers) as response:
                if response.status == 200:
                    standings_data = await response.json()
                    if standings_data.get('standings') and len(standings_data['standings']) > 0:
                        table = standings_data['standings'][0]['table']
                        return [
                            {
                                'position': team['position'],
                                'team_name': team['team']['name'],
                                'team_id': team['team']['id'],
                                'played': team['playedGames'],
                                'wins': team['won'],
                                'draws': team['draw'],
                                'losses': team['lost'],
                                'goals_for': team['goalsFor'],
                                'goals_against': team['goalsAgainst'],
                                'goal_difference': team['goalDifference'],
                                'points': team['points'],
                                'form': team.get('form', '')
                            }
                            for team in table
                        ]
                elif response.status == 403:
                    raise ValueError("Invalid API key or rate limit exceeded")
                elif response.status == 429:
                    raise ValueError("Rate limit exceeded")
                else:
                    raise ValueError(f"API returned status {response.status}")
    
    async def get_team_matches(self, team_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get all matches for a specific team"""
        api_key = os.getenv("FOOTBALL_DATA_API_KEY", "")
        if not api_key:
            raise ValueError("No API key configured")
        
        async with aiohttp.ClientSession() as session:
            matches_url = f"{self.base_url}/teams/{team_id}/matches?limit={limit}"
            async with session.get(matches_url, headers=self.headers) as response:
                if response.status == 200:
                    matches_data = await response.json()
                    matches = matches_data.get('matches', [])
                    return [
                        {
                            'id': match.get('id'),
                            'home_team': match['homeTeam']['name'],
                            'away_team': match['awayTeam']['name'],
                            'date': match['utcDate'],
                            'status': match['status'],
                            'matchday': match.get('matchday'),
                            'score': {
                                'home': match['score']['fullTime'].get('home') if match['score'].get('fullTime') else None,
                                'away': match['score']['fullTime'].get('away') if match['score'].get('fullTime') else None
                            },
                            'competition': match.get('competition', {}).get('name', 'Premier League')
                        }
                        for match in matches
                    ]
                elif response.status == 403:
                    raise ValueError("Invalid API key or rate limit exceeded")
                elif response.status == 429:
                    raise ValueError("Rate limit exceeded")
                else:
                    raise ValueError(f"API returned status {response.status}")
    
    async def get_match_details(self, match_id: int) -> Dict[str, Any]:
        """Get detailed information about a specific match"""
        api_key = os.getenv("FOOTBALL_DATA_API_KEY", "")
        if not api_key:
            raise ValueError("No API key configured")
        
        async with aiohttp.ClientSession() as session:
            match_url = f"{self.base_url}/matches/{match_id}"
            async with session.get(match_url, headers=self.headers) as response:
                if response.status == 200:
                    match_data = await response.json()
                    return {
                        'id': match_data.get('id'),
                        'home_team': match_data['homeTeam']['name'],
                        'away_team': match_data['awayTeam']['name'],
                        'date': match_data['utcDate'],
                        'status': match_data['status'],
                        'matchday': match_data.get('matchday'),
                        'competition': match_data.get('competition', {}).get('name', 'Premier League'),
                        'score': {
                            'full_time': {
                                'home': match_data['score']['fullTime'].get('home') if match_data['score'].get('fullTime') else None,
                                'away': match_data['score']['fullTime'].get('away') if match_data['score'].get('fullTime') else None
                            },
                            'half_time': {
                                'home': match_data['score']['halfTime'].get('home') if match_data['score'].get('halfTime') else None,
                                'away': match_data['score']['halfTime'].get('away') if match_data['score'].get('halfTime') else None
                            }
                        },
                        'venue': match_data.get('venue', ''),
                        'referee': match_data.get('referees', [{}])[0].get('name', '') if match_data.get('referees') else ''
                    }
                elif response.status == 403:
                    raise ValueError("Invalid API key or rate limit exceeded")
                elif response.status == 429:
                    raise ValueError("Rate limit exceeded")
                elif response.status == 404:
                    raise ValueError("Match not found")
                else:
                    raise ValueError(f"API returned status {response.status}")
    
    async def get_competition_info(self) -> Dict[str, Any]:
        """Get Premier League competition information"""
        api_key = os.getenv("FOOTBALL_DATA_API_KEY", "")
        if not api_key:
            raise ValueError("No API key configured")
        
        async with aiohttp.ClientSession() as session:
            comp_url = f"{self.base_url}/competitions/PL"
            async with session.get(comp_url, headers=self.headers) as response:
                if response.status == 200:
                    comp_data = await response.json()
                    return {
                        'id': comp_data.get('id'),
                        'name': comp_data.get('name', 'Premier League'),
                        'code': comp_data.get('code', 'PL'),
                        'type': comp_data.get('type', 'LEAGUE'),
                        'emblem': comp_data.get('emblem', ''),
                        'current_season': {
                            'id': comp_data['currentSeason'].get('id') if comp_data.get('currentSeason') else None,
                            'start_date': comp_data['currentSeason'].get('startDate') if comp_data.get('currentSeason') else None,
                            'end_date': comp_data['currentSeason'].get('endDate') if comp_data.get('currentSeason') else None,
                            'current_matchday': comp_data['currentSeason'].get('currentMatchday') if comp_data.get('currentSeason') else None
                        } if comp_data.get('currentSeason') else None
                    }
                elif response.status == 403:
                    raise ValueError("Invalid API key or rate limit exceeded")
                elif response.status == 429:
                    raise ValueError("Rate limit exceeded")
                else:
                    raise ValueError(f"API returned status {response.status}")
    
    async def get_head_to_head(self, team1_id: int, team2_id: int) -> Dict[str, Any]:
        """Get head-to-head record between two teams"""
        api_key = os.getenv("FOOTBALL_DATA_API_KEY", "")
        if not api_key:
            raise ValueError("No API key configured")
        
        async with aiohttp.ClientSession() as session:
            h2h_url = f"{self.base_url}/teams/{team1_id}/matches?status=FINISHED"
            async with session.get(h2h_url, headers=self.headers) as response:
                if response.status == 200:
                    matches_data = await response.json()
                    matches = matches_data.get('matches', [])
                    
                    # Filter matches between the two teams
                    h2h_matches = [
                        match for match in matches
                        if (match['homeTeam']['id'] == team2_id or match['awayTeam']['id'] == team2_id)
                    ]
                    
                    team1_wins = 0
                    team2_wins = 0
                    draws = 0
                    team1_goals = 0
                    team2_goals = 0
                    
                    recent_matches = []
                    for match in h2h_matches[:5]:  # Last 5 matches
                        home_score = match['score']['fullTime'].get('home') if match['score'].get('fullTime') else 0
                        away_score = match['score']['fullTime'].get('away') if match['score'].get('fullTime') else 0
                        
                        if match['homeTeam']['id'] == team1_id:
                            team1_goals += home_score
                            team2_goals += away_score
                            if home_score > away_score:
                                team1_wins += 1
                            elif away_score > home_score:
                                team2_wins += 1
                            else:
                                draws += 1
                        else:
                            team1_goals += away_score
                            team2_goals += home_score
                            if away_score > home_score:
                                team1_wins += 1
                            elif home_score > away_score:
                                team2_wins += 1
                            else:
                                draws += 1
                        
                        recent_matches.append({
                            'date': match['utcDate'],
                            'home_team': match['homeTeam']['name'],
                            'away_team': match['awayTeam']['name'],
                            'score': {
                                'home': home_score,
                                'away': away_score
                            }
                        })
                    
                    return {
                        'total_matches': len(h2h_matches),
                        'team1_wins': team1_wins,
                        'team2_wins': team2_wins,
                        'draws': draws,
                        'team1_goals': team1_goals,
                        'team2_goals': team2_goals,
                        'recent_matches': recent_matches
                    }
                elif response.status == 403:
                    raise ValueError("Invalid API key or rate limit exceeded")
                elif response.status == 429:
                    raise ValueError("Rate limit exceeded")
                else:
                    raise ValueError(f"API returned status {response.status}")
