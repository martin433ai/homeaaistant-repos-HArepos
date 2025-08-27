#!/bin/bash

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the Next.js application with port 3002 explicitly
exec ./node_modules/.bin/next start -p 3002
