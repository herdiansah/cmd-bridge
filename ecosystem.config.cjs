const path = require('node:path');

module.exports = {
  apps: [
    {
      name: 'commandcode-bridge',
      cwd: __dirname,
      script: path.join(__dirname, 'bridge.py'),
      interpreter: process.env.PYTHON || 'python',
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
      watch: false,
    },
  ],
};
