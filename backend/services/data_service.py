import pandas as pd
import numpy as np
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
import aiohttp
import os
from dotenv import load_dotenv

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
        
        # Cache configuration
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(current_dir)  # Go up from services/ to backend/
        self.cache_dir = os.path.join(backend_dir, 'data_cache')
        self.cache_expiry_hours = 24  # Cache expires after 24 hours
        os.makedirs(self.cache_dir, exist_ok=True)
        
    async def initialize_data(self):
        """Initialize data by loading from cache or fetching from API"""
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
                # Try to load from cache first
                if self._load_from_cache():
                    print("SUCCESS: Loaded data from cache")
                    return
                
                # If cache not available or expired, fetch from API
                print("Cache not available or expired, fetching from API...")
                await self._fetch_real_data()
                
                # Save to cache after successful fetch
                self._save_to_cache()
                print("SUCCESS: Data saved to cache")
                
            except Exception as e:
                # If API fetch fails, try to use stale cache
                if self._load_from_cache(allow_stale=True):
                    print(f"WARNING: API fetch failed: {str(e)}. Using stale cache data.")
                    return
                
                error_msg = f"Failed to fetch data from API: {str(e)}. No cache available. Please ensure FOOTBALL_DATA_API_KEY is set and valid."
                print(f"ERROR: {error_msg}")
                self._initializing = False
                raise ValueError(error_msg)
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
                        print(f"SUCCESS: Loaded competition data: {self.competition_data.get('name', 'Premier League')}")
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
                        print(f"SUCCESS: Loaded {len(self.teams_data)} teams from API")
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
                        print(f"SUCCESS: Loaded {len(self.matches_data)} matches from API")
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
                            print(f"SUCCESS: Loaded league standings from API")
                    # Don't fail if standings fail, it's optional
                    
            except aiohttp.ClientError as e:
                raise ConnectionError(f"Failed to connect to API: {e}")
            except Exception as e:
                raise Exception(f"Error fetching data from API: {e}")
            
            # Update last update timestamp
            self.last_update = datetime.now()
            print(f"SUCCESS: Data refresh completed at {self.last_update.isoformat()}")
    
    def _get_cache_file_path(self, filename: str) -> str:
        """Get the full path to a cache file"""
        return os.path.join(self.cache_dir, filename)
    
    def _save_to_cache(self):
        """Save current data to cache files"""
        try:
            cache_data = {
                'teams_data': self.teams_data,
                'matches_data': self.matches_data,
                'standings_data': self.standings_data,
                'competition_data': self.competition_data,
                'last_update': self.last_update.isoformat() if self.last_update else None
            }
            
            cache_file = self._get_cache_file_path('api_data.json')
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, default=str)
            
            print(f"SUCCESS: Saved data to cache: {cache_file}")
        except Exception as e:
            print(f"WARNING: Failed to save cache: {e}")
    
    def _load_from_cache(self, allow_stale: bool = False) -> bool:
        """Load data from cache if available and not expired
        
        Args:
            allow_stale: If True, load cache even if expired (for fallback)
        
        Returns:
            True if data was loaded successfully, False otherwise
        """
        try:
            cache_file = self._get_cache_file_path('api_data.json')
            
            if not os.path.exists(cache_file):
                print("INFO: No cache file found")
                return False
            
            # Check cache age
            cache_mtime = datetime.fromtimestamp(os.path.getmtime(cache_file))
            cache_age = datetime.now() - cache_mtime
            
            if not allow_stale and cache_age > timedelta(hours=self.cache_expiry_hours):
                print(f"INFO: Cache expired ({cache_age.total_seconds() / 3600:.1f} hours old)")
                return False
            
            # Load cache data
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            self.teams_data = cache_data.get('teams_data', {})
            self.matches_data = cache_data.get('matches_data', [])
            self.standings_data = cache_data.get('standings_data', {})
            self.competition_data = cache_data.get('competition_data', {})
            
            # Restore last_update timestamp
            last_update_str = cache_data.get('last_update')
            if last_update_str:
                try:
                    self.last_update = datetime.fromisoformat(last_update_str)
                except:
                    self.last_update = cache_mtime
            else:
                self.last_update = cache_mtime
            
            cache_age_str = f"({cache_age.total_seconds() / 3600:.1f} hours old)" if cache_age.total_seconds() > 0 else ""
            print(f"SUCCESS: Loaded from cache: {len(self.teams_data)} teams, {len(self.matches_data)} matches {cache_age_str}")
            
            return True
            
        except Exception as e:
            print(f"WARNING: Failed to load cache: {e}")
            return False
    
    async def refresh_data(self):
        """Refresh all data from API"""
        try:
            print("Starting daily data refresh...")
            await self._fetch_real_data()
            
            # Save to cache after successful refresh
            self._save_to_cache()
            
            print("SUCCESS: Daily data refresh completed successfully")
            return True
        except Exception as e:
            print(f"ERROR: Error during data refresh: {e}")
            print("WARNING: Keeping existing data, will retry on next scheduled update")
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
        
        # Ensure we have enough finished matches for training (at least 30 matches)
        finished_count = 0
        target_finished = max(30, len(teams) * 2)  # At least 30, or 2 per team
        
        for week in range(38):  # 38 gameweeks
            week_matches = []
            remaining_teams = teams.copy()
            
            # Create fixtures for this week (10 matches per week for 20 teams)
            while len(remaining_teams) >= 2:
                home_team = remaining_teams.pop(np.random.randint(len(remaining_teams)))
                away_team = remaining_teams.pop(np.random.randint(len(remaining_teams)))
                
                # Generate match date - prioritize finished matches for training data
                if finished_count < target_finished:
                    # Create past matches to ensure we have training data
                    days_ago = np.random.randint(1, 200)  # Random date in past 200 days
                    match_date = now - timedelta(days=days_ago)
                    is_completed = True
                elif week < 25:  # First 25 weeks - mostly in past
                    match_date = start_date + timedelta(weeks=week, days=np.random.randint(7))
                    is_completed = match_date < now
                else:  # Remaining weeks - future matches
                    days_from_now = (week - 25) * 7 + np.random.randint(0, 7)
                    match_date = now + timedelta(days=days_from_now)
                    match_date = match_date.replace(
                        hour=np.random.randint(12, 21),
                        minute=np.random.choice([0, 15, 30, 45])
                    )
                    is_completed = False
                
                if is_completed:
                    finished_count += 1
                    # Generate realistic scores based on team strength
                    home_strength = self._get_team_strength(home_team)
                    away_strength = self._get_team_strength(away_team)
                    
                    home_score = max(0, int(np.random.poisson(1.5 + home_strength)))
                    away_score = max(0, int(np.random.poisson(1.2 + away_strength)))
                    
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
        
        print(f"Generated {len(matches)} matches, {finished_count} finished matches for training")
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
            # If initializing, wait a bit
            await asyncio.sleep(0.5)
            if not self.teams_data:
                raise ValueError("No team data available. Please ensure data is initialized from API first.")
        
        if not self.teams_data:
            raise ValueError("No team data available. Please ensure data is initialized from API first.")
        
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
            # If initializing, wait a bit
            await asyncio.sleep(0.5)
            if not self.matches_data:
                raise ValueError("No match data available. Please ensure data is initialized from API first.")
        
        if not self.matches_data:
            raise ValueError("No match data available. Please ensure data is initialized from API first.")
        
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
            # If initializing, wait a bit
            await asyncio.sleep(0.5)
            if not self.matches_data:
                raise ValueError("No match data available. Please ensure data is initialized from API first.")
        
        if not self.matches_data:
            raise ValueError("No match data available. Please ensure data is initialized from API first.")
        
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
            
            # Get team names - handle API format
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
            # If initializing, wait a bit
            await asyncio.sleep(0.5)
            if not self.matches_data:
                raise ValueError("No match data available. Please ensure data is initialized from API first.")
        
        if not self.matches_data:
            raise ValueError("No match data available. Please ensure data is initialized from API first.")
        
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
        """Get training data for ML model - raises error if no data available"""
        if not self.matches_data:
            raise ValueError("No match data available. Please ensure data is initialized from API first.")
        
        training_data = []
        
        for match in self.matches_data:
            if match.get('status') == 'FINISHED':
                try:
                    # Safely get scores
                    score_data = match.get('score', {})
                    full_time = score_data.get('fullTime', {}) if isinstance(score_data, dict) else {}
                    home_score = full_time.get('home')
                    away_score = full_time.get('away')
                    
                    # Skip if scores are None or not valid numbers
                    if home_score is None or away_score is None:
                        continue
                    
                    # Get team names safely
                    home_team_data = match.get('homeTeam', {})
                    away_team_data = match.get('awayTeam', {})
                    home_team = home_team_data.get('name') if isinstance(home_team_data, dict) else str(home_team_data)
                    away_team = away_team_data.get('name') if isinstance(away_team_data, dict) else str(away_team_data)
                    
                    if not home_team or not away_team:
                        continue
                    
                    # Determine result based on scores
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
                    
                    # Get date safely
                    date_str = match.get('utcDate') or match.get('date')
                    if date_str:
                        try:
                            match_date = pd.to_datetime(date_str)
                        except:
                            match_date = pd.Timestamp.now()
                    else:
                        match_date = pd.Timestamp.now()
                    
                    training_data.append({
                        'home_team': home_team,
                        'away_team': away_team,
                        'date': match_date,
                        'season': '2023-24',
                        'home_score': int(home_score),
                        'away_score': int(away_score),
                        'result': result,
                        'home_result': home_result,
                        'away_result': away_result
                    })
                except Exception as e:
                    print(f"Error processing match data: {e}")
                    continue
        
        if len(training_data) == 0:
            print("WARNING: No valid training data found")
            return pd.DataFrame()
        
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
    