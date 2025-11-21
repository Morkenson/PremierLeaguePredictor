import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const apiService = {
  // Health check
  healthCheck: () => api.get('/health'),

  // Teams
  getTeams: () => api.get('/teams'),
  getTeamStats: (teamName, season = '2023-24') => 
    api.get(`/teams/${encodeURIComponent(teamName)}/stats?season=${season}`),
  getTeamMatches: (teamId, limit = 10) => 
    api.get(`/teams/${teamId}/matches?limit=${limit}`),

  // Predictions
  predictMatch: (data) => api.post('/predict', data),
  getBatchPredictions: () => api.get('/predictions/batch'),

  // Fixtures and League Table
  getUpcomingFixtures: () => api.get('/fixtures'),
  getLeagueTable: (season = '2023-24') => api.get(`/league-table?season=${season}`),
  getLeagueStandings: (season = '2023-24') => api.get(`/league-standings?season=${season}`),

  // Matches
  getMatchDetails: (matchId) => api.get(`/matches/${matchId}`),

  // Competition
  getCompetitionInfo: () => api.get('/competition'),

  // Head-to-head
  getHeadToHead: (team1Id, team2Id) => api.get(`/head-to-head/${team1Id}/${team2Id}`),

  // Admin/Scheduler
  getSchedulerStatus: () => api.get('/admin/scheduler-status'),
  refreshData: () => api.post('/admin/refresh-data'),
};

export { api };
export default apiService;
