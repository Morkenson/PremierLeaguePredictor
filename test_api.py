#!/usr/bin/env python3
"""
Test script for Premier League Predictor API
This script tests all the main endpoints to ensure they're working correctly
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_endpoint(method: str, endpoint: str, data: Dict[Any, Any] = None) -> bool:
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        if response.status_code == 200:
            print(f"✅ {method} {endpoint} - Status: {response.status_code}")
            return True
        else:
            print(f"❌ {method} {endpoint} - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ {method} {endpoint} - Error: {e}")
        return False

def main():
    """Run all API tests"""
    print("🧪 Testing Premier League Predictor API")
    print("=" * 50)
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(2)
    
    # Test health endpoint
    print("\n🔍 Testing Health Endpoint:")
    test_endpoint("GET", "/health")
    
    # Test root endpoint
    print("\n🔍 Testing Root Endpoint:")
    test_endpoint("GET", "/")
    
    # Test teams endpoint
    print("\n🔍 Testing Teams Endpoint:")
    test_endpoint("GET", "/teams")
    
    # Test league table endpoint
    print("\n🔍 Testing League Table Endpoint:")
    test_endpoint("GET", "/league-table")
    
    # Test fixtures endpoint
    print("\n🔍 Testing Fixtures Endpoint:")
    test_endpoint("GET", "/fixtures")
    
    # Test prediction endpoint
    print("\n🔍 Testing Prediction Endpoint:")
    prediction_data = {
        "home_team": "Manchester City",
        "away_team": "Arsenal",
        "season": "2023-24"
    }
    test_endpoint("POST", "/predict", prediction_data)
    
    # Test batch predictions endpoint
    print("\n🔍 Testing Batch Predictions Endpoint:")
    test_endpoint("GET", "/predictions/batch")
    
    # Test team stats endpoint
    print("\n🔍 Testing Team Stats Endpoint:")
    test_endpoint("GET", "/teams/Manchester%20City/stats")
    
    print("\n" + "=" * 50)
    print("🎉 API testing completed!")
    print("\n📖 For interactive API documentation, visit:")
    print(f"   {BASE_URL}/docs")

if __name__ == "__main__":
    main()
