#!/usr/bin/env python3
"""
Simple API test for workflow endpoints
"""
import requests
import json

def test_components():
    print("🔧 Testing components endpoint...")
    try:
        response = requests.get('http://localhost:8000/api/v1/workflow/components')
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            components = data.get('data', [])
            print(f"✅ Available components: {len(components)}")
            
            # Find Google Drive components
            drive_components = [c for c in components if 'google_drive' in c['type']]
            for comp in drive_components:
                print(f"  📂 {comp['type']}: {comp['name']}")
                print(f"     Description: {comp['description']}")
                print(f"     Parameters: {len(comp.get('parameters', []))}")
                
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_template_creation():
    print("\n🚀 Testing template creation...")
    try:
        url = 'http://localhost:8000/api/v1/workflow/templates'
        template_data = {
            'name': 'API Test - Google Drive',
            'description': 'Test Google Drive Write component via API',
            'workflow_data': {
                'nodes': [
                    {
                        'id': 'trigger-1',
                        'type': 'manual_trigger',
                        'position': {'x': 100, 'y': 100},
                        'data': {'label': 'Start'}
                    },
                    {
                        'id': 'drive-write-1', 
                        'type': 'google_drive_write',
                        'position': {'x': 300, 'y': 100},
                        'data': {
                            'label': 'Google Drive Write',
                            'config': {
                                'file_name': 'APITestFile.json',
                                'file_type': 'json',
                                'folder_id': '14l2RVGPs5Ao1ZwY1ZAjGbvYtwV7ft182',
                                'overwrite': False,
                                'include_timestamp': True
                            }
                        }
                    }
                ],
                'edges': [
                    {
                        'id': 'edge-1',
                        'source': 'trigger-1',
                        'target': 'drive-write-1'
                    }
                ],
                'input_schema': {},
                'output_schema': {}
            }
        }
        
        response = requests.post(url, json=template_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            template = response.json()
            template_id = template['template_id']  # API returns 'template_id' not 'id'
            print(f"✅ Template created: {template_id}")
            print(f"   Message: {template.get('message', 'N/A')}")
            return template_id
        else:
            print(f"❌ Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def test_workflow_execution(template_id):
    print(f"\n🎯 Testing workflow execution for template: {template_id}")
    try:
        # Create instance
        instance_url = 'http://localhost:8000/api/v1/workflow/instances'
        instance_data = {
            'name': 'API Test Instance',
            'template_id': template_id,
            'workflow_data': {
                'nodes': [
                    {
                        'id': 'trigger-1',
                        'type': 'manual_trigger',
                        'position': {'x': 100, 'y': 100},
                        'data': {'label': 'Start'}
                    },
                    {
                        'id': 'drive-write-1', 
                        'type': 'google_drive_write',
                        'position': {'x': 300, 'y': 100},
                        'data': {
                            'label': 'Google Drive Write',
                            'config': {
                                'file_name': 'APITestFile.json',
                                'file_type': 'json',
                                'folder_id': '14l2RVGPs5Ao1ZwY1ZAjGbvYtwV7ft182',
                                'overwrite': False,
                                'include_timestamp': True
                            }
                        }
                    }
                ],
                'edges': [
                    {
                        'id': 'edge-1',
                        'source': 'trigger-1',
                        'target': 'drive-write-1'
                    }
                ]
            },
            'input_data': {'test_data': 'API execution test', 'timestamp': '2025-08-03'}
        }
        
        instance_response = requests.post(instance_url, json=instance_data)
        print(f"Instance creation status: {instance_response.status_code}")
        
        if instance_response.status_code == 200:
            instance = instance_response.json()
            instance_id = instance['instance_id']  # API returns 'instance_id' not 'id'
            print(f"✅ Instance created: {instance_id}")
            
            # Execute instance
            exec_url = f'http://localhost:8000/api/v1/workflow/instances/{instance_id}/execute'
            exec_data = {}
            
            exec_response = requests.post(exec_url, json=exec_data)
            print(f"Execution status: {exec_response.status_code}")
            
            if exec_response.status_code == 200:
                exec_result = exec_response.json()
                print(f"✅ Workflow executed successfully!")
                print(f"   Execution ID: {exec_result.get('execution_id', 'N/A')}")
                print(f"   Status: {exec_result.get('status', 'N/A')}")
                return True
            else:
                print(f"❌ Execution error: {exec_response.text}")
                return False
        else:
            print(f"❌ Instance error: {instance_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    print("=== API Test Suite ===")
    
    # Test 1: Components
    if test_components():
        # Test 2: Template creation
        template_id = test_template_creation()
        if template_id:
            # Test 3: Workflow execution
            if test_workflow_execution(template_id):
                print(f"\n🎉 All tests passed! Google Drive Write component working via API!")
            else:
                print(f"\n❌ Workflow execution failed")
        else:
            print("\n❌ Template creation failed")
    else:
        print("\n❌ Components test failed")
