#!/usr/bin/env python3
"""
Simple debug check for AI Response write issue
Check the logs and outputs from recent workflow execution
"""

def check_execution_monitor_log():
    """Check the execution monitor screenshot for clues"""
    print("🔍 ANALYZING EXECUTION MONITOR SCREENSHOT")
    print("="*50)
    
    # From the screenshot provided:
    log_content = """
    "Example Asset URL": "https://static.wikimedia.org/wikipedia/images/9/97/Task_manager_app_logo.png",
    "Desired Output Format": "PNG",
    "Model Specification": "OpenAI", 
    "ai_response": {
        "type": "asset_generation",
        "generated_url": "https://ollama-assets.local/png/0000.png",
        "ai_response": "<think>\\nOkay, the user wants me to generate a prompt for a Task Manager app logo based on their asset request. Let me understand the details: they want a task manager app logo, they provided an example URL, wanted in PNG format, and specified OpenAI model. The needs to be informative, descriptive, and professional.\\n\\nFirst, technical specifications: The output format is PNG, so I should mention resolution, transparency, style guidelines, color palette, and implementation notes.\\n\\nFirst, technical specifications:\n\nThe example image from the URL probably has a certain size. Let me check the example URL. Wait, I can't access external links, but I might be able to tell from the standard task manager app logo size. Common logo sizes are 512x512 or 1024x1024 for high resolution. Also, PNG with transparency might be needed, so I'll include that in the specification.\n\nSecond, the style should be clean and professional. The example task manager app logo has a minimalist design with a clean sans-serif font. The logo should be scalable, so vector elements are preferred.\\n\\nThird, color palette: The example might have a checkmark and clock, so the implementation notes should include: checkmark and clock are common icons for a task manager, a clean color palette with primary color, and a clean sans-serif font.\\n\"</think>\\n\\nBased on your task manager app logo request, I'll provide a comprehensive specification for a Task Manager app logo:\n\n### Design Specifications\n- **Style**: Modern, minimalist design with clean lines\n- **Color Palette**: Primary blue (#2563EB) with accent gray (#64748B)\n- **Format**: PNG with transparent background\n- **Dimensions**: 1024x1024px for optimal scalability"
    }
    """
    
    print("📊 KEY FINDINGS:")
    print("-" * 30)
    
    # 1. AI Response is generated
    print("✅ 1. AI Response IS generated:")
    print("   - Contains 'ai_response' field with actual content")
    print("   - Has <think> tags that need to be cleaned")
    print("   - Contains comprehensive task manager logo specification")
    
    # 2. Check if the content is being processed
    print("\n✅ 2. Content Structure:")
    print("   - 'ai_response' nested inside 'ai_response' object")
    print("   - This matches the expected format in component_registry.py")
    print("   - The _clean_ai_response() should process this")
    
    # 3. Check the flow
    print("\n🔍 3. Expected Flow:")
    print("   AI Processing → _format_results_for_sheets() → results_for_sheets")
    print("   GoogleSheetsWrite → should find 'results_for_sheets' data")
    print("   GoogleSheetsWrite → should write data including Prompt column")
    
    print("\n❓ 4. POTENTIAL ISSUES:")
    print("-" * 20)
    print("   A. Data not passed correctly between components")
    print("   B. 'results_for_sheets' not found by GoogleSheetsWrite")
    print("   C. Google Sheets API not authenticating properly")
    print("   D. Data format issues during write operation")
    
    return True

def check_google_sheets_output():
    """Check what should be in Google Sheets"""
    print("\n📊 EXPECTED GOOGLE SHEETS OUTPUT")
    print("="*40)
    
    expected_headers = [
        "Row Index", "Original Description", "Output Format", "Status", 
        "Generated URL", "Prompt", "Provider", "Model", "Quality", "Size", 
        "Processing Time", "Timestamp", "Notes"
    ]
    
    print("📝 Expected Headers (13 columns):")
    for i, header in enumerate(expected_headers, 1):
        marker = "⭐" if header == "Prompt" else "  "
        print(f"   {marker} {i:2d}. {header}")
    
    print("\n📝 Expected Prompt Column Content:")
    print("   - Column F (6th column)")
    print("   - Should contain cleaned AI response text")
    print("   - No <think> tags")
    print("   - Full specification text from AI")
    
    print("\n🎯 WHAT TO CHECK IN GOOGLE SHEETS:")
    print("   1. Does column F exist?")
    print("   2. Does it have 'Prompt' header?")
    print("   3. Does it contain AI response text?")
    print("   4. Is the text cleaned (no <think> tags)?")

def suggest_debugging_steps():
    """Suggest debugging steps"""
    print("\n🔧 DEBUGGING STEPS")
    print("="*30)
    
    print("1️⃣ Check Backend Logs:")
    print("   - Look for 'results_for_sheets' in logs")
    print("   - Check if GoogleSheetsWrite finds the data")
    print("   - Verify Google Sheets API calls")
    
    print("\n2️⃣ Check Google Sheets:")
    print("   - Open your sheet: 1Wly5cBDxYoPJE3gJtvyPXUpRBzEzuzYOpZPl_Sj4hIc")
    print("   - Look for recent data")
    print("   - Check if Prompt column (F) exists")
    print("   - Check if it has AI response content")
    
    print("\n3️⃣ Check Component Registry:")
    print("   - Verify _format_results_for_sheets() is called")
    print("   - Verify 'results_for_sheets' is added to output_data")
    print("   - Verify GoogleSheetsWrite finds this data")
    
    print("\n4️⃣ Check Authentication:")
    print("   - Verify Google Sheets API credentials")
    print("   - Check if GOOGLE_SHEETS_AVAILABLE = True")
    print("   - Look for authentication success logs")

def main():
    print("🚀 AI RESPONSE WRITE ISSUE ANALYSIS")
    print("="*60)
    
    check_execution_monitor_log()
    check_google_sheets_output()
    suggest_debugging_steps()
    
    print("\n🎯 SUMMARY")
    print("="*20)
    print("✅ AI Response is generated correctly")
    print("✅ Format should include Prompt column")
    print("❓ Need to verify data reaches Google Sheets")
    print("❓ Need to check Google Sheets API authentication")
    
    print("\n💡 NEXT STEPS:")
    print("1. Check your Google Sheets for new data")
    print("2. Look for column F (Prompt)")
    print("3. If missing, check backend logs for API errors")
    print("4. Verify Google Sheets API authentication")

if __name__ == "__main__":
    main()
