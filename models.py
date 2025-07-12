from datetime import datetime
from pymongo import MongoClient, DESCENDING
from pymongo.collection import Collection
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
client = MongoClient(os.getenv('MONGO_URI'))
db = client.github_events

# Create indexes for better query performance
def setup_indexes():
    # Create indexes for common queries
    db.actions.create_index([('timestamp', DESCENDING)])
    db.actions.create_index([('action', 1)])
    db.actions.create_index([('author', 1)])
    db.actions.create_index([('from_branch', 1)])
    db.actions.create_index([('to_branch', 1)])

def validate_event(event_data: dict) -> bool:
    """
    Validate event data against our schema
    """
    required_fields = {
        'request_id': str,
        'author': str,
        'action': str,
        'timestamp': str
    }
    
    # Check if all required fields are present and of correct type
    for field, field_type in required_fields.items():
        if field not in event_data:
            print(f"Missing required field: {field}")
            return False
        if not isinstance(event_data[field], field_type):
            print(f"Invalid type for field {field}. Expected {field_type}, got {type(event_data[field])}")
            return False
    
    # Validate action type
    valid_actions = {'PUSH', 'PULL_REQUEST', 'MERGE'}
    if event_data['action'] not in valid_actions:
        print(f"Invalid action type: {event_data['action']}")
        return False
    
    # Validate branch fields
    if 'to_branch' not in event_data or (event_data['to_branch'] is not None and not isinstance(event_data['to_branch'], str)):
        print("Invalid or missing to_branch")
        return False
    
    # from_branch is optional for PUSH events
    if event_data['action'] != 'PUSH':
        if 'from_branch' not in event_data or (event_data['from_branch'] is not None and not isinstance(event_data['from_branch'], str)):
            print("Invalid or missing from_branch for non-PUSH event")
            return False
    
    return True

def insert_event(event_data: dict) -> bool:
    """
    Insert a new event into MongoDB with schema validation
    """
    if not validate_event(event_data):
        return False
    
    try:
        result = db.actions.insert_one(event_data)
        return bool(result.inserted_id)
    except Exception as e:
        print(f"Error inserting event: {str(e)}")
        return False

def get_events(
    action: str = None,
    author: str = None,
    branch: str = None,
    limit: int = 10
) -> list:
    """
    Retrieve events with optional filters
    """
    query = {}
    if action:
        query['action'] = action.upper()
    if author:
        query['author'] = author
    if branch:
        query['$or'] = [
            {'from_branch': branch},
            {'to_branch': branch}
        ]
    
    try:
        return list(
            db.actions.find(
                query,
                {'_id': 0}  # Exclude MongoDB _id from results
            ).sort('timestamp', DESCENDING).limit(limit)
        )
    except Exception as e:
        print(f"Error retrieving events: {str(e)}")
        return []

# Set up indexes when the module is imported
setup_indexes() 