#!/usr/bin/env python3
"""
Test Frontend-Backend Connectivity
"""

import requests
import json
from datetime import datetime

def test_frontend_backend_connectivity():
    """Test all API endpoints that frontend uses"""
    print("🔗 Testing Frontend-Backend Connectivity")
    print("="*50)
    
    base_url = "http://localhost:8000/api/v1/workflow"
    
    tests = [
        {
            "name": "Components API",
            "url": f"{base_url}/components",
            "method": "GET"
        },
        {
            "name": "Health Check",
            "url": f"{base_url}/health",
            "method": "GET"
        },
        {
            "name": "Component Metadata",
            "url": f"{base_url}/components/google_sheets_write",
            "method": "GET"
        },
        {
            "name": "Instances List",
            "url": f"{base_url}/instances",
            "method": "GET"
        }
    ]
    
    results = []
    
    for test in tests:
        print(f"\n🧪 Testing: {test['name']}")
        print(f"URL: {test['url']}")
        
        try:
            if test['method'] == 'GET':
                response = requests.get(test['url'], timeout=5)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if test['name'] == 'Components API':
                    component_count = len(data.get('data', []))
                    print(f"✅ Found {component_count} components")
                    
                    # Show some components
                    components = data.get('data', [])[:3]
                    for comp in components:
                        print(f"   - {comp['name']} ({comp['type']})")
                
                elif test['name'] == 'Component Metadata':
                    comp_data = data.get('data', {})
                    print(f"✅ Component: {comp_data.get('name', 'Unknown')}")
                    print(f"   Parameters: {len(comp_data.get('parameters', []))}")
                
                elif test['name'] == 'Health Check':
                    print(f"✅ Service healthy: {data.get('message', 'OK')}")
                
                elif test['name'] == 'Instances List':
                    instances = data.get('data', {}).get('instances', [])
                    print(f"✅ Found {len(instances)} workflow instances")
                
                results.append({"test": test['name'], "status": "PASS", "code": response.status_code})
            
            else:
                print(f"❌ Failed with status {response.status_code}")
                results.append({"test": test['name'], "status": "FAIL", "code": response.status_code})
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {str(e)}")
            results.append({"test": test['name'], "status": "ERROR", "error": str(e)})
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            results.append({"test": test['name'], "status": "ERROR", "error": str(e)})
    
    # Summary
    print(f"\n📊 Test Summary")
    print("="*30)
    
    passed = sum(1 for r in results if r['status'] == 'PASS')
    failed = sum(1 for r in results if r['status'] == 'FAIL')
    errors = sum(1 for r in results if r['status'] == 'ERROR')
    
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️  Errors: {errors}")
    print(f"Total: {len(results)}")
    
    if passed == len(results):
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"Frontend-Backend connectivity is working perfectly!")
        print(f"🔗 Frontend: http://localhost:3000")
        print(f"🔗 Backend:  http://localhost:8000")
        
        return True
    else:
        print(f"\n⚠️  Some tests failed. Check backend configuration.")
        return False

def test_google_sheets_component():
    """Test Google Sheets component specifically"""
    print(f"\n🧪 Testing Google Sheets Component Integration")
    print("="*40)
    
    url = "http://localhost:8000/api/v1/workflow/components/google_sheets_write"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            component = data.get('data', {})
            
            print(f"✅ Component Name: {component.get('name')}")
            print(f"✅ Component Type: {component.get('type')}")
            print(f"✅ Category: {component.get('category')}")
            
            parameters = component.get('parameters', [])
            print(f"✅ Parameters ({len(parameters)}):")
            
            for param in parameters:
                required = "✓" if param.get('required') else "○"
                print(f"   {required} {param['name']} ({param['type']}) - {param.get('description', 'No description')}")
            
            handles = component.get('input_handles', []) + component.get('output_handles', [])
            print(f"✅ Handles ({len(handles)}):")
            
            for handle in handles:
                print(f"   - {handle['type']} ({handle['position']}): {handle.get('label', handle['id'])}")
            
            return True
        else:
            print(f"❌ Failed to get component metadata: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Frontend-Backend Integration Test")
    print("="*55)
    
    # Test general connectivity
    connectivity_ok = test_frontend_backend_connectivity()
    
    if connectivity_ok:
        # Test specific Google Sheets component
        sheets_ok = test_google_sheets_component()
        
        if sheets_ok:
            print(f"\n🎯 INTEGRATION STATUS: READY")
            print(f"✅ Backend APIs working")
            print(f"✅ Google Sheets component configured")
            print(f"✅ Frontend can connect to backend")
            print(f"\n🎨 You can now test the workflow editor!")
            print(f"🔗 Open: http://localhost:3000")
        else:
            print(f"\n⚠️  Google Sheets component needs attention")
    else:
        print(f"\n❌ Backend connectivity issues")
        print(f"💡 Make sure backend is running: python main.py")
