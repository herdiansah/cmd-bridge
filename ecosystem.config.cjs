const path = require('node:path');

module.exports = {
  apps: [
    {
      name: 'commandcode-bridge',
      cwd: __dirname,
      script: path.join(__dirname, 'bridge.py'),
      interpreter: process.env.PYTHON || 'python',
      env: {
        COMMAND_CODE_API_KEY: process.env.COMMAND_CODE_API_KEY,
        COMMANDCODE_BRIDGE_HOST: '127.0.0.1',
        COMMANDCODE_BRIDGE_PORT: '8320',
        COMMANDCODE_BRIDGE_TIMEOUT: '600',
      },
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
      watch: false,
    },
  ],
};
