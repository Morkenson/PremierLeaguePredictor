import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Log the API URL in development to help debug
if (process.env.NODE_ENV === 'development') {
  console.log('API Base URL:', API_BASE_URL);
}

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
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.baseURL}${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    // Check if response is HTML (error page) instead of JSON
    if (typeof response.data === 'string' && response.data.trim().startsWith('<!')) {
      const error = new Error('API returned HTML instead of JSON. This usually means the request went to the frontend instead of the backend.');
      error.response = response;
      console.error('HTML Response detected:', {
        url: response.config.url,
        baseURL: response.config.baseURL,
        fullURL: `${response.config.baseURL}${response.config.url}`,
        status: response.status,
        headers: response.headers
      });
      return Promise.reject(error);
    }
    return response.data;
  },
  (error) => {
    // Check if error response is HTML
    if (error.response && typeof error.response.data === 'string' && error.response.data.trim().startsWith('<!')) {
      console.error('API Error - Received HTML:', {
        url: error.config?.url,
        baseURL: error.config?.baseURL,
        message: 'Request was sent to frontend instead of backend. Check REACT_APP_API_URL environment variable.'
      });
    }
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
