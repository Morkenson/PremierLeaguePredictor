const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // Only proxy API requests, not static files or hot-reload files
  app.use(
    [
      '/teams',
      '/predict', 
      '/fixtures',
      '/league-table',
      '/league-standings',
      '/matches',
      '/competition',
      '/head-to-head',
      '/admin',
      '/health'
    ],
    createProxyMiddleware({
      target: 'http://localhost:8000',
      changeOrigin: true,
      logLevel: 'debug',
    })
  );
};

