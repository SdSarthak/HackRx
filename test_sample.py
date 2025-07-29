#!/usr/bin/env python3
"""
Test script that matches the exact sample request from the user.
"""

import requests
import json

def test_sample_request():
    """Test the exact sample request provided by the user."""
    
    # API endpoint
    url = "http://localhost:8000/hackrx/run"
    
    # Headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer d229e5eb06d6a264c4cebecd4fb0dc33e6a81c7bfa1f01945f751424fcac1e3a"
    }
    
    # Request payload (exact sample from user)
    payload = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
            "What is the waiting period for pre-existing diseases (PED) to be covered?",
            "Does this policy cover maternity expenses, and what are the conditions?",
            "What is the waiting period for cataract surgery?",
            "Are the medical expenses for an organ donor covered under this policy?",
            "What is the No Claim Discount (NCD) offered in this policy?",
            "Is there a benefit for preventive health check-ups?",
            "How does the policy define a 'Hospital'?",
            "What is the extent of coverage for AYUSH treatments?",
            "Are there any sub-limits on room rent and ICU charges for Plan A?"
        ]
    }
    
    print("🧪 Testing Sample Request")
    print("=" * 50)
    print(f"URL: {url}")
    print(f"Questions: {len(payload['questions'])}")
    print(f"Document: {payload['documents'][:60]}...")
    print()
    
    try:
        # Make the request
        print("📤 Sending request...")
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Request successful!")
            print()
            print("📋 Response format:")
            print(f"  - Type: {type(data)}")
            print(f"  - Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            
            if 'answers' in data:
                answers = data['answers']
                print(f"  - Number of answers: {len(answers)}")
                print(f"  - Answer types: {[type(ans).__name__ for ans in answers[:3]]}")
                print()
                
                print("🎯 Sample answers:")
                for i, answer in enumerate(answers[:3]):
                    print(f"  Q{i+1}: {answer[:100]}{'...' if len(str(answer)) > 100 else ''}")
                print()
                
                # Check if format matches expected
                expected_format = all(isinstance(ans, str) for ans in answers)
                print(f"🔍 Format check: {'✅ All answers are strings' if expected_format else '❌ Not all answers are strings'}")
                
            return True
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_sample_request()
    exit(0 if success else 1)
