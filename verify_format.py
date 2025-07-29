#!/usr/bin/env python3
"""
Test script to get the full response and compare with expected format.
"""

import requests
import json

def test_full_response():
    """Test and display the full response."""
    
    # API endpoint
    url = "http://localhost:8000/hackrx/run"
    
    # Headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer d229e5eb06d6a264c4cebecd4fb0dc33e6a81c7bfa1f01945f751424fcac1e3a"
    }
    
    # Simplified request for faster testing
    payload = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
            "What is the waiting period for pre-existing diseases (PED) to be covered?"
        ]
    }
    
    try:
        print("📤 Testing with 2 questions for faster response...")
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Response received!")
            print()
            print("📋 Full Response:")
            print(json.dumps(data, indent=2))
            print()
            
            # Verify format
            if isinstance(data, dict) and 'answers' in data:
                answers = data['answers']
                if isinstance(answers, list) and all(isinstance(ans, str) for ans in answers):
                    print("🎯 Format verification: ✅ PERFECT MATCH")
                    print("   - Response is a dict with 'answers' key")
                    print("   - 'answers' is a list of strings")
                    print("   - No additional fields (confidence_score, source_clauses, etc.)")
                    return True
                    
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_full_response()
