#!/usr/bin/env python3
"""
Test script for the Solana Flask API
"""

import requests

# Start the Flask app in another terminal with:
# /www/solana-helper/.venv/bin/python app.py

API_URL = "http://localhost:20251"

def test_verify_signature():
    """Test the verify_signature endpoint"""
    print("Testing /verify_signature endpoint...")
    
    # Sample data (this would fail since it's not a real signature)
    test_data = {
        "message": "Sign in to V2EX: 1751620507",
        "signature": "63837bc12d4a7876866b1cd21caafbf471daffc37cf10731aa3d046c2eaf1e01ac0088e7f7d69f72d7e7b4c0f8240ca6de0fe882f7c8a8715e901bb4d7fbfe01",
        "public_key": "4JBz4tAKgAmxjDPHHi9HRLj14RsCQJyuCkCFKnpz7B9s"
    }
    
    try:
        response = requests.post(f"{API_URL}/verify_signature", json=test_data)
        result = response.json()
        print(f"Response: {result}")
    except Exception as e:
        print(f"Error: {e}")

def test_get_balance():
    """Test the get_balance endpoint"""
    print("\nTesting /get_balance endpoint...")
    
    # Sample Solana public key
    test_data = {
        "public_key": "4JBz4tAKgAmxjDPHHi9HRLj14RsCQJyuCkCFKnpz7B9s"  # test key
    }
    
    try:
        response = requests.post(f"{API_URL}/get_balance", json=test_data)
        result = response.json()
        print(f"Response: {result}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Solana Flask API Test")
    print("Make sure the Flask app is running on port 20251")
    print("-" * 40)
    
    test_verify_signature()
    test_get_balance()
