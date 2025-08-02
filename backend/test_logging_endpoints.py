#!/usr/bin/env python3
"""
Test script for enhanced logging endpoints
"""
import requests
import json
import sys

def test_logging_endpoints():
    """Test all logging endpoints"""
    print('🧪 Testing Enhanced Logging System')
    print('=' * 50)
    
    base_url = 'http://localhost:8000'
    
    # Test backend health
    try:
        response = requests.get(f'{base_url}/', timeout=5)
        print(f'✅ Backend health: {response.status_code}')
    except Exception as e:
        print(f'❌ Backend not running: {e}')
        return False
    
    # Test enhanced logging endpoints
    endpoints = [
        '/api/v1/workflow/logs/summary',
        '/api/v1/workflow/logs/tasks?limit=5', 
        '/api/v1/workflow/logs/steps?limit=5'
    ]
    
    success_count = 0
    for endpoint in endpoints:
        try:
            response = requests.get(f'{base_url}{endpoint}', timeout=5)
            print(f'📍 {endpoint}')
            print(f'   Status: {response.status_code}')
            
            if response.status_code == 200:
                data = response.json()
                print(f'   ✅ Success: {len(data) if isinstance(data, list) else "OK"}')
                success_count += 1
            elif response.status_code == 422:
                print(f'   ⚠️  Validation error: {response.json()}')
            elif response.status_code == 404:
                print(f'   ❌ Not found - endpoint not registered')
            else:
                print(f'   ❌ Error {response.status_code}: {response.text[:100]}')
                
        except Exception as e:
            print(f'   ❌ Request failed: {e}')
    
    print(f'\n📊 Result: {success_count}/{len(endpoints)} endpoints working')
    return success_count == len(endpoints)

if __name__ == '__main__':
    success = test_logging_endpoints()
    sys.exit(0 if success else 1)
