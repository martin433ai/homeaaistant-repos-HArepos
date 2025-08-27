module.exports = {
  apps: [
    {
      name: "eaddrinuse",
      script: "./start-script.sh",
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: "1G",
      env: {
        NODE_ENV: "development",
        PORT: 3002 // Using a different port to avoid EADDRINUSE errors
      },
      env_development: {
        NODE_ENV: "development",
        PORT: 3002 // Using a different port to avoid EADDRINUSE errors
      },
      env_production: {
        NODE_ENV: "production",
        PORT: 3000
      },
      // Error management
      max_restarts: 10,
      restart_delay: 3000, // Wait 3 seconds between restarts
      // Watching specific files/directories (enable if needed)
      // watch: ["pages", "components", "public"],
      // ignore_watch: ["node_modules", ".git", ".next"],
      // Logs configuration
      log_date_format: "YYYY-MM-DD HH:mm:ss Z",
      error_file: "logs/error.log",
      out_file: "logs/out.log",
      merge_logs: true,
      // Specific handling for EADDRINUSE errors
      listen_timeout: 5000,
      kill_timeout: 3000,
      // Custom hooks for handling specific actions
      post_update: [
        "npm install", // Run npm install after code update
        "echo 'App has been updated!'"
      ],
      // Graceful shutdown
      kill_signal: "SIGINT",
      shutdown_with_message: true
    }
  ],
  // You can also define deploy configuration here
  deploy: {
    development: {
      user: "user",
      host: "localhost",
      ref: "origin/main",
      repo: "git@github.com:repo/project.git",
      path: "/var/www/development",
      "post-deploy": "npm install && pm2 reload ecosystem.config.js --env development"
    },
    production: {
      user: "user",
      host: "server_ip",
      ref: "origin/main",
      repo: "git@github.com:repo/project.git",
      path: "/var/www/production",
      "post-deploy": "npm install && npm run build && pm2 reload ecosystem.config.js --env production"
    }
  }
};

