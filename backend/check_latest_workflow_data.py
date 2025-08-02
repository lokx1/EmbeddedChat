#!/usr/bin/env python3
"""Check workflow execution and data flow between nodes"""

import requests
import json

def main():
    print("🔍 Checking Latest Workflow Execution")
    print("=" * 50)
    
    try:
        # Get latest instance
        response = requests.get("http://localhost:8000/api/v1/workflow/instances")
        if response.status_code == 200:
            instances = response.json()['data']['instances']
            if instances:
                latest = instances[0]
                instance_id = latest['id']
                print(f"📋 Latest instance: {instance_id}")
                print(f"📝 Name: {latest.get('name', 'Unknown')}")
                print(f"📊 Status: {latest.get('status', 'Unknown')}")
                
                # Check output data
                if 'output_data' in latest and latest['output_data']:
                    output_data = latest['output_data']
                    node_outputs = output_data.get('node_outputs', {})
                    
                    print(f"\n📦 Node Outputs:")
                    for node_id, output in node_outputs.items():
                        print(f"  {node_id}:")
                        if output:
                            if isinstance(output, dict) and 'processed_results' in output:
                                print(f"    ✅ Has AI processing results: {len(output['processed_results'])} items")
                            elif isinstance(output, dict) and 'values' in output:
                                print(f"    ✅ Has Google Sheets data: {len(output['values'])} rows")
                            else:
                                print(f"    📊 Output: {str(output)[:100]}...")
                        else:
                            print(f"    ❌ No output data")
                    
                    # Check specific nodes
                    ai_node_output = node_outputs.get('ai-processing-3', {})
                    sheets_write_output = node_outputs.get('sheets-write-4', {})
                    
                    print(f"\n🤖 AI Processing Output:")
                    if ai_node_output and 'processed_results' in ai_node_output:
                        results = ai_node_output['processed_results']
                        print(f"  ✅ Processed {len(results)} items")
                        for i, result in enumerate(results[:2]):  # Show first 2
                            print(f"    Item {i+1}: {str(result)[:200]}...")
                    else:
                        print(f"  ❌ No AI processing results")
                    
                    print(f"\n📝 GoogleSheetsWrite Output:")
                    if sheets_write_output:
                        print(f"  📊 Output: {sheets_write_output}")
                    else:
                        print(f"  ❌ No write output (expected - write failed)")
                
                else:
                    print("❌ No output data found")
            else:
                print("❌ No instances found")
        else:
            print(f"❌ Failed to get instances: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
