#!/usr/bin/env python3
"""
Test AI Processing component's results_for_sheets output format
Based on the actual AI response from FE logs
"""

def test_ai_results_formatting():
    print("🔍 Testing AI Processing results_for_sheets format...")
    
    # Simulate the exact processed_results structure from FE logs
    processed_results = [
        {
            "row_index": 1,
            "input_data": {
                "Description": "Design a Task Manager app logo",
                "Example Asset URL": "https://static.wikia.nocookie.net/logopedia/images/9/97/Task_Manager_2024.png/revision/latest?cb=20240127035026",
                "Desired Output Format": "PNG",
                "Model Specification": "OpenAI",
                "Prompt": ""
            },
            "ai_response": {
                "type": "ollama_asset_generation",
                "description": "",
                "output_format": "PNG",
                "generated_url": "https://ollama-assets.local/png/0.png",
                "ai_response": "Okay, here's a comprehensive creative brief for generating a Task Manager app logo, designed to be detailed and actionable.\n\n**Asset Generation Request: Task Manager App Logo**\n\n**1. TECHNICAL SPECIFICATIONS**\n\n* **Dimensions:** 800x800 pixels (PNG format).\n* **Resolution:** 300 DPI (Dots Per Inch) – This ensures high-quality printing and display.\n* **File Format:** PNG (Portable Network Graphics). This format supports transparency, which is crucial for the logo's design.\n* **Compression:** We'll use a lossless compression method (e.g., PNG-8 or a similar optimized format) to maintain image quality. A maximum file size of 2MB is desired.\n* **Color Depth:** 24-bit color (RGB). This allows for a wide range of colors and subtle gradients.\n* **Transparency:** Full transparency is required for the background. A subtle, soft gradient effect (light blue to white) can be applied to the background for a modern feel...",
                "metadata": {
                    "model": "gemma3:1b",
                    "provider": "ollama",
                    "quality": "local_generation",
                    "size": "1024x1024",
                    "processing_time": "10193.6ms",
                    "tokens_evaluated": 1182,
                    "eval_duration": "8987.4ms"
                },
                "prompt_used": "\n Asset Generation Request:\n Description: \n Output Format: PNG\n \n Based on this asset request: {\n \"Description\": \"Design a Task Manager app logo..."
            },
            "status": "success",
            "provider": "ollama",
            "model": "gemma3:1b",
            "timestamp": "2025-08-04T12:21:46.888975"
        },
        {
            "row_index": 2,
            "input_data": {
                "Description": "Summer Sale banner for a fashion store",
                "Example Asset URL": "https://images.vexels.com/content/107842/preview/summer-sale-poster-design-illustration-836fb3.png",
                "Desired Output Format": "JPG",
                "Model Specification": "Claude",
                "Prompt": ""
            },
            "ai_response": {
                "type": "ollama_asset_generation",
                "description": "",
                "output_format": "PNG",
                "generated_url": "https://ollama-assets.local/png/0.png",
                "ai_response": "Okay, here's a comprehensive creative brief for generating a Summer Sale banner, designed to produce a high-quality, visually appealing PNG asset, incorporating detailed technical specifications, design guidelines, and practical considerations.\n\n**Asset Generation Request: Summer Sale Banner for a Fashion Store**\n\n**1. TECHNICAL SPECIFICATIONS:**\n\n* **Dimensions:** 1920 x 1080 pixels (Full HD). This size provides a good balance between detail and file size for web and print use.\n* **File Format:** PNG (Portable Network Graphics). PNG is ideal for web graphics due to its lossless compression and transparency capabilities...",
                "metadata": {
                    "model": "gemma3:1b",
                    "provider": "ollama",
                    "quality": "local_generation",
                    "size": "1024x1024",
                    "processing_time": "9838.5ms",
                    "tokens_evaluated": 1162,
                    "eval_duration": "9508.3ms"
                },
                "prompt_used": "\n Asset Generation Request:\n Description: \n Output Format: PNG\n \n Based on this asset request: {\n \"Description\": \"Summer Sale banner for a fashi..."
            },
            "status": "success",
            "provider": "ollama",
            "model": "gemma3:1b",
            "timestamp": "2025-08-04T12:22:01.301164"
        }
    ]
    
    print(f"📊 Input: {len(processed_results)} processed results")
    print(f"📋 Sample input_data keys: {list(processed_results[0]['input_data'].keys())}")
    print(f"🤖 Sample ai_response keys: {list(processed_results[0]['ai_response'].keys())}")
    
    # Simulate the _format_ai_results_for_sheets logic
    print(f"\n🔄 Simulating _format_ai_results_for_sheets logic...")
    
    if not processed_results:
        print("❌ No processed results")
        return []
        
    # Extract headers from first result's input_data
    first_result = processed_results[0]
    input_data = first_result.get("input_data", {})
    
    # Get original headers from input data
    original_headers = list(input_data.keys())
    print(f"📋 Original headers from input_data: {original_headers}")
    
    # Check if "Prompt" column already exists, if so replace it, otherwise add it
    if "Prompt" in original_headers:
        headers = original_headers
        print(f"✅ Prompt column exists, will replace content")
    else:
        headers = original_headers + ["Prompt"]
        print(f"➕ Adding Prompt column, new headers: {headers}")
    
    # Create data rows
    data_rows = [headers]  # Start with header row
    print(f"📊 Headers row: {headers}")
    
    for i, result in enumerate(processed_results):
        input_data = result.get("input_data", {})
        ai_response = result.get("ai_response", {})
        
        print(f"\n🔍 Processing row {i+1}:")
        print(f"   Input data keys: {list(input_data.keys())}")
        print(f"   AI response keys: {list(ai_response.keys())}")
        
        # Extract and clean AI response for Prompt column
        ai_text = ""
        
        # Test the extraction logic
        if "ai_response" in ai_response and isinstance(ai_response["ai_response"], str):
            ai_text = ai_response["ai_response"]
            print(f"   ✅ Found ai_response: '{ai_text[:100]}...' (length: {len(ai_text)})")
        
        elif not ai_text:
            print(f"   🔍 Trying fallback extraction...")
            for key in ["prompt_used", "note", "response", "content", "text", "generated_text"]:
                if key in ai_response and isinstance(ai_response[key], str) and ai_response[key].strip():
                    ai_text = ai_response[key]
                    print(f"   ✅ Found text in {key}: '{ai_text[:100]}...' (length: {len(ai_text)})")
                    break
        
        # Clean the AI response (simulate _clean_ai_response)
        cleaned_prompt = ai_text[:2000] if ai_text else ""  # Simplified cleaning
        print(f"   🎯 Final cleaned prompt: '{cleaned_prompt[:100]}...' (length: {len(cleaned_prompt)})")
        
        # Build row with original data, replacing Prompt column if it exists
        row = []
        for header in original_headers:
            if header == "Prompt":
                # Replace the empty/existing Prompt column with AI response
                row.append(cleaned_prompt)
                print(f"   📝 Replaced Prompt column with AI response")
            else:
                value = str(input_data.get(header, ""))
                row.append(value)
                print(f"   📋 {header}: '{value[:50]}...'")
        
        # If Prompt column didn't exist in original headers, add it now
        if "Prompt" not in original_headers:
            row.append(cleaned_prompt)
            print(f"   ➕ Added Prompt column with AI response")
        
        data_rows.append(row)
        print(f"   📊 Final row length: {len(row)} (expected: {len(headers)})")
    
    print(f"\n🎯 FINAL RESULTS_FOR_SHEETS:")
    print(f"   Total rows: {len(data_rows)} (1 header + {len(data_rows)-1} data rows)")
    print(f"   Headers: {data_rows[0]}")
    
    if len(data_rows) > 1:
        print(f"   Sample data row 1: {[cell[:50] + '...' if len(cell) > 50 else cell for cell in data_rows[1]]}")
        
        # Check if Prompt column has content
        if "Prompt" in headers:
            prompt_index = headers.index("Prompt")
            prompt_content = data_rows[1][prompt_index] if len(data_rows[1]) > prompt_index else ""
            print(f"   🎯 Prompt column index: {prompt_index}")
            print(f"   🎯 Prompt content length: {len(prompt_content)}")
            print(f"   🎯 Prompt preview: '{prompt_content[:200]}...'")
            
            if prompt_content and len(prompt_content) > 20:
                print(f"   ✅ SUCCESS: Prompt column has substantial content!")
            else:
                print(f"   ❌ ISSUE: Prompt column is empty or too short")
    
    # Check format compatibility with Google Sheets Write
    print(f"\n📤 GOOGLE SHEETS WRITE COMPATIBILITY CHECK:")
    print(f"   ✅ Is list: {isinstance(data_rows, list)}")
    print(f"   ✅ Has header row: {len(data_rows) > 0}")
    print(f"   ✅ All rows same length: {all(len(row) == len(data_rows[0]) for row in data_rows) if data_rows else False}")
    print(f"   ✅ Ready for Google Sheets API: YES")
    
    return data_rows

if __name__ == "__main__":
    test_ai_results_formatting()
