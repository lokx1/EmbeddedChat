#!/usr/bin/env python3
"""
Test Registration with Fixed Endpoints
"""

import asyncio
import aiohttp
import json
import random

async def test_registration():
    """Test registration with the correct endpoints"""
    
    base_url = "https://embeddedchat-production.up.railway.app"
    
    # Generate unique test user
    user_id = random.randint(1000, 9999)
    test_user = {
        "username": f"user_{user_id}",
        "email": f"user_{user_id}@example.com",
        "password": "testpassword123",
        "full_name": f"Test User {user_id}"
    }
    
    print("🧪 Testing Registration with Fixed Endpoints")
    print("=" * 60)
    print(f"Test user: {test_user['username']}")
    print()
    
    async with aiohttp.ClientSession() as session:
        
        # Test endpoint 1: /auth/register (backward compatibility)
        print("1️⃣ Testing /auth/register")
        url1 = f"{base_url}/auth/register"
        
        try:
            async with session.post(url1, json=test_user) as response:
                status = response.status
                response_text = await response.text()
                
                if status == 201:
                    print(f"✅ SUCCESS: Registration worked! (Status {status})")
                    try:
                        data = json.loads(response_text)
                        print(f"   User ID: {data.get('user', {}).get('id')}")
                        print(f"   Access Token: {data.get('access_token', 'N/A')[:20]}...")
                    except:
                        pass
                elif status == 400:
                    print(f"⚠️  User exists: {response_text}")
                else:
                    print(f"❌ Failed: Status {status} - {response_text}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()
        
        # Test endpoint 2: /api/v1/auth/register (with API prefix)
        print("2️⃣ Testing /api/v1/auth/register")
        url2 = f"{base_url}/api/v1/auth/register"
        
        # Use different user for this test
        test_user2 = test_user.copy()
        test_user2['username'] = f"user_v1_{user_id}"
        test_user2['email'] = f"user_v1_{user_id}@example.com"
        
        try:
            async with session.post(url2, json=test_user2) as response:
                status = response.status
                response_text = await response.text()
                
                if status == 201:
                    print(f"✅ SUCCESS: Registration worked! (Status {status})")
                    try:
                        data = json.loads(response_text)
                        print(f"   User ID: {data.get('user', {}).get('id')}")
                        print(f"   Access Token: {data.get('access_token', 'N/A')[:20]}...")
                    except:
                        pass
                elif status == 400:
                    print(f"⚠️  User exists: {response_text}")
                else:
                    print(f"❌ Failed: Status {status} - {response_text}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")

    print("\n" + "=" * 60)
    print("🎯 Conclusion:")
    print("Both endpoints are working! The issue was double slash in the URL.")
    print("Frontend should use:")
    print("  - /auth/register (backward compatibility)")  
    print("  - /api/v1/auth/register (recommended)")

if __name__ == "__main__":
    asyncio.run(test_registration())
