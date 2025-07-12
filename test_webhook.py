import requests
import json
from datetime import datetime

def test_webhook():
    """
    Test the webhook endpoint with sample data for each event type
    """
    webhook_url = "http://localhost:5000/webhook"
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'GitHub-Hookshot/test'
    }

    # Test Push Event
    push_data = {
        "ref": "refs/heads/main",
        "after": "abc123",
        "pusher": {
            "name": "TestUser"
        }
    }
    
    print("Testing Push Event...")
    response = requests.post(webhook_url, json=push_data, headers=headers)
    print(f"Push Event Response: {response.status_code}")
    print(response.json())

    # Test Pull Request Event
    pr_data = {
        "action": "opened",
        "pull_request": {
            "id": 123,
            "head": {
                "ref": "feature-branch"
            },
            "base": {
                "ref": "main"
            },
            "merged": False
        },
        "sender": {
            "login": "TestUser"
        }
    }
    
    print("\nTesting Pull Request Event...")
    response = requests.post(webhook_url, json=pr_data, headers=headers)
    print(f"Pull Request Event Response: {response.status_code}")
    print(response.json())

    # Test Merge Event
    merge_data = {
        "action": "closed",
        "pull_request": {
            "id": 124,
            "head": {
                "ref": "feature-branch"
            },
            "base": {
                "ref": "main"
            },
            "merged": True
        },
        "sender": {
            "login": "TestUser"
        }
    }
    
    print("\nTesting Merge Event...")
    response = requests.post(webhook_url, json=merge_data, headers=headers)
    print(f"Merge Event Response: {response.status_code}")
    print(response.json())

if __name__ == "__main__":
    test_webhook() 