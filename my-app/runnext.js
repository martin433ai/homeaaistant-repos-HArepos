#!/usr/bin/env node

const { spawn, exec } = require('child_process');
const killPort = require('kill-port');

// Default Next.js port
const DEFAULT_PORT = 3000;

// Get command line arguments, removing first two (node and script path)
const args = process.argv.slice(2);

// Extract port from arguments if provided
let port = DEFAULT_PORT;
for (let i = 0; i < args.length; i++) {
  if (args[i] === '-p' || args[i] === '--port') {
    port = parseInt(args[i + 1], 10);
    break;
  }
}

// Special handling for the 'ineaddrinuse' argument
const autoKill = args.includes('ineaddrinuse');
const cleanArgs = args.filter(arg => arg !== 'ineaddrinuse');

/**
 * Run a Next.js command with the given arguments
 */
function runNextCommand(cmdArgs) {
  console.log(`Running Next.js command: next ${cmdArgs.join(' ')}`);
  
  const nextProcess = spawn('npx', ['next', ...cmdArgs], { 
    stdio: 'inherit',
    shell: true 
  });
  
  nextProcess.on('error', (error) => {
    console.error(`Error executing Next.js command: ${error.message}`);
    process.exit(1);
  });
  
  nextProcess.on('close', (code) => {
    // Handle non-zero exit code by checking for EADDRINUSE
    if (code !== 0 && autoKill) {
      // Check if the error is related to EADDRINUSE
      console.log(`Next.js process exited with code ${code}, checking if port ${port} is in use...`);
      checkPortAndRetry(port, cmdArgs);
    } else {
      process.exit(code);
    }
  });
}

/**
 * Check if a port is in use and handle it
 */
function checkPortAndRetry(portToCheck, cmdArgs) {
  exec(`lsof -i :${portToCheck}`, (error, stdout) => {
    if (stdout) {
      console.log(`Port ${portToCheck} is in use. Killing process...`);
      killPort(portToCheck)
        .then(() => {
          console.log(`Successfully killed process on port ${portToCheck}. Retrying command...`);
          // Retry the command after a short delay
          setTimeout(() => runNextCommand(cmdArgs), 1000);
        })
        .catch(err => {
          console.error(`Failed to kill process on port ${portToCheck}: ${err.message}`);
          process.exit(1);
        });
    } else {
      console.log(`No process found using port ${portToCheck}. The error may be unrelated to port usage.`);
      process.exit(1);
    }
  });
}

// Start the process
if (cleanArgs.length === 0) {
  console.log('Usage: runnext [command] [options] [ineaddrinuse]');
  console.log('Example: runnext dev -p 3000 ineaddrinuse');
  process.exit(0);
} else {
  runNextCommand(cleanArgs);
}

