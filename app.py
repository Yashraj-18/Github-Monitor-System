from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
from dotenv import load_dotenv
from models import insert_event, get_events
import logging
import pytz

# Set up enhanced logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure timezone
IST = pytz.timezone('Asia/Kolkata')

app = Flask(__name__)

# Configure CORS with specific settings
CORS(app, resources={
    r"/webhook": {
        "origins": "*",  # Allow all origins for webhook
        "methods": ["POST"],  # Only allow POST for webhook
    },
    r"/events": {
        "origins": ["http://localhost:3000"],  # Only allow frontend origin
        "methods": ["GET"],  # Only allow GET for events
    },
    r"/health": {
        "origins": "*",  # Allow all origins for health check
        "methods": ["GET"],  # Only allow GET for health check
    }
})

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    logger.debug("Health check endpoint called")
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(IST).strftime("%d %B %Y - %I:%M %p IST")
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhooks from GitHub."""
    try:
        # Enhanced logging for debugging
        logger.debug("Received webhook request")
        logger.debug(f"Headers: {dict(request.headers)}")
        logger.debug(f"Raw Data: {request.get_data(as_text=True)}")
        
        data = request.json
        if not data:
            logger.error("No JSON data received")
            return jsonify({"status": "error", "message": "No data received"}), 400
        
        logger.debug(f"Parsed JSON data: {data}")
        
        # Determine action type
        if 'pull_request' in data:
            if data['action'] == 'closed' and data.get('pull_request', {}).get('merged', False):
                action = 'MERGE'
            else:
                action = 'PULL_REQUEST'
            logger.debug(f"Detected action type: {action}")
        elif 'ref' in data:  # Push event
            action = 'PUSH'
            logger.debug("Detected action type: PUSH")
        else:
            logger.error(f"Unknown event type in data: {data}")
            return jsonify({"status": "error", "message": "Unknown event type"}), 400

        # Get author based on event type
        if 'pusher' in data:
            author = data['pusher']['name']
            logger.debug(f"Author from pusher: {author}")
        elif 'sender' in data:
            author = data['sender']['login']
            logger.debug(f"Author from sender: {author}")
        else:
            logger.error("No author information found in payload")
            return jsonify({"status": "error", "message": "No author information"}), 400

        # Format timestamp in IST
        timestamp = datetime.now(IST).strftime("%d %B %Y - %I:%M %p IST")

        # Create entry document
        entry = {
            "request_id": data.get('after') or str(data.get('pull_request', {}).get('id')),
            "author": author,
            "action": action,
            "from_branch": data.get('pull_request', {}).get('head', {}).get('ref') if action != 'PUSH' else None,
            "to_branch": (data.get('pull_request', {}).get('base', {}).get('ref') or 
                         (data.get('ref', '').split('/')[-1] if 'ref' in data else None)),
            "timestamp": timestamp
        }

        logger.debug(f"Created entry document: {entry}")

        # Store in MongoDB using schema validation
        if insert_event(entry):
            logger.info(f"Successfully recorded {action} event from {author}")
            return jsonify({"status": "success", "message": "Event recorded"}), 200
        else:
            logger.error("Failed to insert event into database")
            return jsonify({"status": "error", "message": "Failed to record event"}), 400

    except Exception as e:
        logger.exception("Error processing webhook")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/events', methods=['GET'])
def get_github_events():
    """Retrieve GitHub events with optional filters."""
    try:
        # Get query parameters
        action = request.args.get('action')
        author = request.args.get('author')
        branch = request.args.get('branch')
        limit = int(request.args.get('limit', 10))

        # Get events using schema functions
        events = get_events(action, author, branch, limit)

        return jsonify({
            'status': 'success',
            'count': len(events),
            'events': events
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    # Ensure MongoDB URI is set
    if not os.getenv('MONGO_URI'):
        raise ValueError("MONGO_URI environment variable is not set!")
    
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    app.run(host='0.0.0.0', port=port, debug=debug) 