# GitHub Events Monitor

A real-time monitoring system for GitHub events using Flask, React, and MongoDB.

## Features

- Real-time monitoring of GitHub webhook events
- Support for Push, Pull Request, and Merge events
- Automatic event filtering and sorting
- MongoDB storage with schema validation
- Auto-refreshing frontend display

## Prerequisites

- Python 3.8+
- Node.js 14+
- MongoDB 4.4+
- ngrok (for webhook testing)

## Setup

1. **Install Backend Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Frontend Dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

3. **Configure Environment**
   Create a `.env` file in the root directory:
   ```
   MONGO_URI=mongodb://localhost:27017/github_events
   FLASK_ENV=development
   ```

4. **Start the Application**
   ```bash
   python start_all.py
   ```
   This will:
   - Start the Flask backend on port 5000
   - Start the React frontend on port 3000
   - Configure ngrok for webhook access
   - Set up MongoDB connections

## GitHub Webhook Setup

1. Go to your GitHub repository
2. Click Settings > Webhooks > Add webhook
3. Set Payload URL to the ngrok URL shown in the console
4. Set Content type to `application/json`
5. Select events:
   - Push
   - Pull requests
   - Pull request reviews

## Development

- Backend API: http://localhost:5000
- Frontend UI: http://localhost:3000
- MongoDB: localhost:27017
- Webhook URL: Provided by ngrok

## API Endpoints

- `GET /health` - Health check endpoint
- `POST /webhook` - GitHub webhook endpoint
- `GET /events` - Retrieve stored events
  - Query params:
    - `action`: Filter by event type (PUSH, PULL_REQUEST, MERGE)
    - `author`: Filter by author
    - `branch`: Filter by branch name
    - `limit`: Limit number of results (default: 10)

## Architecture

- **Backend**: Flask with MongoDB for storage
- **Frontend**: React with TypeScript and Tailwind CSS
- **Database**: MongoDB with schema validation
- **Webhook**: GitHub webhooks via ngrok tunnel

## Troubleshooting

1. **MongoDB Connection Issues**
   - Ensure MongoDB is running: `mongod`
   - Check connection string in `.env`

2. **Webhook Not Working**
   - Verify ngrok is running
   - Check GitHub webhook configuration
   - Ensure correct payload URL

3. **Frontend Not Updating**
   - Check browser console for errors
   - Verify backend is accessible
   - Check CORS configuration
