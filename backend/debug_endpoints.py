#!/usr/bin/env python3
"""
Debug API Endpoints
Test which endpoints are actually available and working
"""

import asyncio
import aiohttp
import json
import os

async def test_endpoints():
    """Test various endpoint configurations"""
    
    # Base URL (từ Railway hoặc local)
    base_url = "https://embeddedchat-production.up.railway.app"
    
    # Các endpoints có thể có
    endpoints_to_test = [
        "/auth/register",
        "/api/v1/auth/register", 
        "/api/auth/register",
        "/register",
        "/health",
        "/api/v1/health",
        "/",
        "/api/docs"
    ]
    
    test_data = {
        "username": "testuser123",
        "email": "test123@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    
    print("🧪 Testing API Endpoints")
    print("=" * 60)
    print(f"Base URL: {base_url}")
    print()
    
    async with aiohttp.ClientSession() as session:
        
        for endpoint in endpoints_to_test:
            url = f"{base_url}{endpoint}"
            print(f"Testing: {url}")
            
            try:
                # Test với GET trước
                async with session.get(url) as response:
                    status = response.status
                    if status == 200:
                        print(f"  ✅ GET {status} - Available")
                    elif status == 405:
                        print(f"  ⚠️  GET {status} - Method not allowed (endpoint exists)")
                    elif status == 404:
                        print(f"  ❌ GET {status} - Not found")
                    else:
                        print(f"  ℹ️  GET {status}")
                
                # Test với POST cho register endpoints
                if "register" in endpoint:
                    async with session.post(url, json=test_data) as response:
                        status = response.status
                        if status == 201:
                            print(f"  ✅ POST {status} - Registration works!")
                        elif status == 422:
                            print(f"  ✅ POST {status} - Validation error (endpoint works)")
                        elif status == 400:
                            print(f"  ⚠️  POST {status} - Bad request (check response)")
                            response_text = await response.text()
                            print(f"      Response: {response_text[:100]}...")
                        elif status == 500:
                            print(f"  ❌ POST {status} - Server error")
                            response_text = await response.text()
                            print(f"      Response: {response_text[:100]}...")
                        elif status == 404:
                            print(f"  ❌ POST {status} - Not found")
                        else:
                            print(f"  ℹ️  POST {status}")
                            
            except Exception as e:
                print(f"  ❌ Error: {e}")
            
            print()
    
    print("=" * 60)
    print("🎯 Summary:")
    print("Look for endpoints that return:")
    print("- ✅ 200/201: Working endpoints")
    print("- ⚠️  405: Endpoint exists but wrong method")
    print("- ⚠️  422: Validation error (endpoint works)")
    print("- ❌ 404: Endpoint not found")

async def test_docs_endpoints():
    """Test documentation endpoints to see available routes"""
    
    base_url = "https://embeddedchat-production.up.railway.app"
    
    print("\n🔍 Checking API Documentation...")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        
        docs_endpoints = [
            "/api/docs",
            "/api/redoc", 
            "/api/openapi.json",
            "/docs",
            "/redoc",
            "/openapi.json"
        ]
        
        for endpoint in docs_endpoints:
            url = f"{base_url}{endpoint}"
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        print(f"✅ {url} - Available")
                        if "openapi.json" in endpoint:
                            try:
                                data = await response.json()
                                if "paths" in data:
                                    print("   Available paths:")
                                    for path in list(data["paths"].keys())[:10]:  # Show first 10
                                        print(f"     - {path}")
                                    if len(data["paths"]) > 10:
                                        print(f"     ... and {len(data['paths']) - 10} more")
                            except:
                                pass
                    else:
                        print(f"❌ {url} - Status {response.status}")
            except Exception as e:
                print(f"❌ {url} - Error: {e}")

async def main():
    """Main function"""
    await test_endpoints()
    await test_docs_endpoints()

if __name__ == "__main__":
    asyncio.run(main())
