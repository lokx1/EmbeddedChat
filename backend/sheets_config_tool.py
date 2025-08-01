#!/usr/bin/env python3
"""
Interactive Google Sheets Write Configuration Tool
"""

import requests
import json
from datetime import datetime
import uuid

class GoogleSheetsWriteConfigTool:
    def __init__(self):
        self.base_url = "http://localhost:8000/api/v1"
        self.sheet_id = "1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc"
    
    def show_menu(self):
        """Show configuration menu"""
        print("\n" + "="*60)
        print("📊 GOOGLE SHEETS WRITE CONFIGURATION TOOL")
        print("="*60)
        print(f"🔗 Your Google Sheets: {self.sheet_id}")
        print(f"🔗 Original URL: https://docs.google.com/spreadsheets/d/{self.sheet_id}/edit?gid=0#gid=0")
        print("\n📋 Select configuration option:")
        print("1. 📄 Write to Sheet2 (next tab)")
        print("2. 📈 Write to Results tab")
        print("3. 📅 Write to date-based tab (Data_YYYYMMDD)")
        print("4. ✏️  Custom configuration")
        print("5. 🧪 Test all configurations")
        print("6. ❌ Exit")
        
    def get_sample_data(self, data_type="default"):
        """Get sample data based on type"""
        timestamp = str(datetime.now())
        
        if data_type == "user_registration":
            return [
                ["Timestamp", "User ID", "Email", "Status", "Source"],
                [timestamp, "USR001", "user1@example.com", "Active", "Website"],
                [timestamp, "USR002", "user2@example.com", "Pending", "Mobile App"],
                [timestamp, "USR003", "user3@example.com", "Active", "API"]
            ]
        elif data_type == "sales_data":
            return [
                ["Date", "Product", "Quantity", "Price", "Total"],
                [timestamp, "Product A", "10", "100", "1000"],
                [timestamp, "Product B", "5", "200", "1000"],
                [timestamp, "Product C", "15", "50", "750"]
            ]
        elif data_type == "task_tracking":
            return [
                ["Timestamp", "Task", "Assignee", "Status", "Priority"],
                [timestamp, "Setup Database", "John", "Completed", "High"],
                [timestamp, "Design UI", "Jane", "In Progress", "Medium"],
                [timestamp, "Testing", "Bob", "Pending", "Low"]
            ]
        else:
            return [
                ["Timestamp", "Event", "Details", "Status"],
                [timestamp, "System Check", "All systems operational", "OK"],
                [timestamp, "Data Backup", "Backup completed successfully", "OK"],
                [timestamp, "User Activity", "10 new users registered", "OK"]
            ]
    
    def create_workflow_config(self, sheet_name, mode="append", range_start="A1", data_format="auto"):
        """Create workflow configuration"""
        return {
            "nodes": [
                {
                    "id": "trigger-1",
                    "type": "manual_trigger",
                    "position": {"x": 100, "y": 100},
                    "data": {
                        "label": "Manual Trigger",
                        "type": "manual_trigger",
                        "config": {}
                    }
                },
                {
                    "id": "sheets-write-1",
                    "type": "google_sheets_write",
                    "position": {"x": 400, "y": 100},
                    "data": {
                        "label": f"Write to {sheet_name}",
                        "type": "google_sheets_write",
                        "config": {
                            "sheet_id": self.sheet_id,
                            "sheet_name": sheet_name,
                            "range": range_start,
                            "mode": mode,
                            "data_format": data_format
                        }
                    }
                }
            ],
            "edges": [
                {
                    "id": "edge-1",
                    "source": "trigger-1",
                    "target": "sheets-write-1",
                    "sourceHandle": "output",
                    "targetHandle": "input"
                }
            ],
            "viewport": {"x": 0, "y": 0, "zoom": 1}
        }
    
    def execute_workflow(self, config, sample_data, description):
        """Execute workflow with given configuration"""
        print(f"\n🚀 Executing: {description}")
        print(f"📝 Config: {config['nodes'][1]['data']['config']}")
        
        # Create instance
        instance_payload = {
            "name": f"{description} - {datetime.now().strftime('%H:%M:%S')}",
            "workflow_data": config,
            "input_data": {"data": sample_data},
            "created_by": "config_tool"
        }
        
        try:
            instance_response = requests.post(f"{self.base_url}/workflow/instances", json=instance_payload)
            if instance_response.status_code != 200:
                print(f"❌ Failed to create instance: {instance_response.text}")
                return False
            
            instance_data = instance_response.json()
            instance_id = instance_data["instance_id"]
            
            # Execute
            execute_response = requests.post(f"{self.base_url}/workflow/instances/{instance_id}/execute", json={
                "input_data": sample_data
            })
            
            if execute_response.status_code != 200:
                print(f"❌ Failed to execute: {execute_response.text}")
                return False
            
            # Check result
            import time
            time.sleep(1)
            
            status_response = requests.get(f"{self.base_url}/workflow/instances/{instance_id}")
            if status_response.status_code == 200:
                status_data = status_response.json()
                instance = status_data["data"]["instance"]
                
                print(f"✅ Status: {instance['status']}")
                print(f"📊 Executed nodes: {instance['output_data']['executed_nodes']}")
                
                sheet_name = config['nodes'][1]['data']['config']['sheet_name']
                print(f"🔗 Result URL: https://docs.google.com/spreadsheets/d/{self.sheet_id}/edit#gid=1")
                
                return True
            else:
                print(f"❌ Failed to get status: {status_response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def run_preset_1(self):
        """Write to Sheet2 (next tab)"""
        config = self.create_workflow_config("Sheet2", "append", "A1")
        data = self.get_sample_data("user_registration")
        return self.execute_workflow(config, data, "Write to Sheet2 (Next Tab)")
    
    def run_preset_2(self):
        """Write to Results tab"""
        config = self.create_workflow_config("Results", "overwrite", "A1")
        data = self.get_sample_data("sales_data")
        return self.execute_workflow(config, data, "Write to Results Tab")
    
    def run_preset_3(self):
        """Write to date-based tab"""
        sheet_name = f"Data_{datetime.now().strftime('%Y%m%d')}"
        config = self.create_workflow_config(sheet_name, "clear_write", "A1")
        data = self.get_sample_data("task_tracking")
        return self.execute_workflow(config, data, f"Write to {sheet_name}")
    
    def run_custom(self):
        """Custom configuration"""
        print("\n📝 Custom Configuration:")
        
        sheet_name = input("Sheet name (e.g., MySheet): ").strip() or "MySheet"
        
        print("Mode options: append, overwrite, clear_write")
        mode = input("Mode (default: append): ").strip() or "append"
        
        range_start = input("Starting range (default: A1): ").strip() or "A1"
        
        print("Data format options: auto, json_array, csv_string, key_value")
        data_format = input("Data format (default: auto): ").strip() or "auto"
        
        print("Sample data types: default, user_registration, sales_data, task_tracking")
        data_type = input("Sample data type (default: default): ").strip() or "default"
        
        config = self.create_workflow_config(sheet_name, mode, range_start, data_format)
        data = self.get_sample_data(data_type)
        
        return self.execute_workflow(config, data, f"Custom: {sheet_name}")
    
    def test_all(self):
        """Test all configurations"""
        print("\n🧪 Testing all configurations...")
        
        results = []
        results.append(("Sheet2", self.run_preset_1()))
        results.append(("Results", self.run_preset_2()))
        results.append(("Date-based", self.run_preset_3()))
        
        print("\n📊 Test Results Summary:")
        for name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {name}: {status}")
        
        return all(result[1] for result in results)
    
    def run(self):
        """Main execution loop"""
        while True:
            self.show_menu()
            choice = input("\n👉 Enter your choice (1-6): ").strip()
            
            if choice == "1":
                self.run_preset_1()
            elif choice == "2":
                self.run_preset_2()
            elif choice == "3":
                self.run_preset_3()
            elif choice == "4":
                self.run_custom()
            elif choice == "5":
                self.test_all()
            elif choice == "6":
                print("\n👋 Goodbye!")
                break
            else:
                print("\n❌ Invalid choice. Please try again.")
            
            input("\n📌 Press Enter to continue...")

if __name__ == "__main__":
    tool = GoogleSheetsWriteConfigTool()
    tool.run()
