#!/usr/bin/env python3
"""
Test the complete AI response processing workflow to verify prompt column extraction
"""
import asyncio
import json
from datetime import datetime

async def test_complete_workflow():
    """Test the complete workflow with actual AI response data"""
    
    # Sample processed results data structure as it would come from AI processing
    processed_results = [
        {
            "row_index": 1,
            "input_data": {
                "Description": "Design a Task Manager app logo",
                "Example Asset URL": "https://static.wikia.nocookie.net/logopedia/images/9/97/Task_Manager_2024.png/revision/latest?cb=20240127035026",
                "Desired Output Format": "PNG",
                "Model Specification": "OpenAI",
                "Prompt": ""  # Empty prompt column that should be filled
            },
            "ai_response": {
                "type": "ollama_asset_generation",
                "description": "",
                "output_format": "PNG",
                "generated_url": "https://ollama-assets.local/png/0.png",
                "ai_response": "Okay, here's a comprehensive creative brief for generating a Task Manager app logo, aiming for a professional and detailed response.\n\n**Asset Generation Request: Task Manager App Logo**\n\n**1. TECHNICAL SPECIFICATIONS:**\n\n* **Dimensions:** 800x600 pixels (width x height). This size balances visual impact with scalability across various platforms (iOS, Android, web).\n* **File Format:** PNG (Portable Network Graphics). This format supports transparency, which is crucial for a logo that might be used on backgrounds.\n* **Compression:** We'll use a lossless compression setting (JPEG compression with a quality setting of 80-90%). This preserves image quality while minimizing file size.",
                "metadata": {
                    "model": "gemma3:1b",
                    "provider": "ollama",
                    "quality": "local_generation",
                    "size": "1024x1024",
                    "processing_time": "9868.2ms",
                    "tokens_evaluated": 1135,
                    "eval_duration": "8608.3ms"
                },
                "prompt_used": "Asset Generation Request..."
            },
            "status": "success",
            "provider": "ollama",
            "model": "gemma3:1b",
            "timestamp": "2025-08-04T11:10:50.154613"
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
                "ai_response": "Okay, here's a comprehensive creative brief for generating a Summer Sale banner, designed to produce a high-quality, visually appealing PNG asset.\n\n**Asset Generation Request: Summer Sale Banner for a Fashion Store**\n\n**1. TECHNICAL SPECIFICATIONS:**\n\n* **Dimensions:** 1920 x 1080 pixels (Full HD). This size provides sufficient detail for a large banner display without excessive pixelation.",
                "metadata": {
                    "model": "gemma3:1b",
                    "provider": "ollama",
                    "quality": "local_generation",
                    "size": "1024x1024",
                    "processing_time": "11485.2ms",
                    "tokens_evaluated": 1165,
                    "eval_duration": "11139.7ms"
                },
                "prompt_used": "Asset Generation Request..."
            },
            "status": "success",
            "provider": "ollama",
            "model": "gemma3:1b",
            "timestamp": "2025-08-04T11:11:06.227368"
        }
    ]
    
    # Simulate the GoogleSheetsWriteComponent._format_ai_results_for_sheets method
    def format_ai_results_for_sheets(processed_results):
        """Test version of the formatting method"""
        if not processed_results:
            return []
            
        # Extract headers from first result's input_data
        first_result = processed_results[0]
        input_data = first_result.get("input_data", {})
        
        # Get original headers from input data
        original_headers = list(input_data.keys())
        
        # Check if "Prompt" column already exists, if so replace it, otherwise add it
        if "Prompt" in original_headers:
            # Prompt column already exists, we'll replace its content
            headers = original_headers
        else:
            # Add Prompt column for AI response
            headers = original_headers + ["Prompt"]
        
        # Create data rows
        data_rows = [headers]  # Start with header row
        
        def clean_ai_response(ai_text):
            """Clean AI response by removing <think> tags and their content"""
            if not ai_text:
                return ""
            
            import re
            
            # Remove <think>...</think> blocks (including multiline)
            cleaned = re.sub(r'<think>.*?</think>', '', ai_text, flags=re.DOTALL | re.IGNORECASE)
            
            # Remove any remaining <think> or </think> tags
            cleaned = re.sub(r'</?think>', '', cleaned, flags=re.IGNORECASE)
            
            # Clean up extra whitespace and normalize line breaks
            cleaned = re.sub(r'\n\s*\n+', '\n\n', cleaned)  # Multiple newlines to double newline
            cleaned = re.sub(r'^\s+|\s+$', '', cleaned, flags=re.MULTILINE)  # Trim each line
            cleaned = cleaned.strip()
            
            # If the text is too long, truncate it but keep it readable
            if len(cleaned) > 2000:  # Increased limit for better content
                # Try to cut at a sentence boundary
                truncated = cleaned[:2000]
                last_period = truncated.rfind('.')
                if last_period > 1000:  # Only cut at period if it's not too early
                    cleaned = truncated[:last_period + 1] + " [...]"
                else:
                    cleaned = truncated + " [...]"
            
            return cleaned
        
        for result in processed_results:
            input_data = result.get("input_data", {})
            ai_response = result.get("ai_response", {})
            
            # Extract AI response text
            ai_text = ""
            if ai_response:
                if "ai_response" in ai_response:
                    if isinstance(ai_response["ai_response"], str):
                        ai_text = ai_response["ai_response"]
                        print(f"✅ Found ai_response as string for row {result.get('row_index')}")
                    elif isinstance(ai_response["ai_response"], dict):
                        # Nested structure
                        nested = ai_response["ai_response"]
                        for key in ["ai_response", "text", "content", "response"]:
                            if key in nested:
                                ai_text = nested[key]
                                break
                
                # Fallback to other possible keys
                if not ai_text:
                    for key in ["generated_text", "response", "content", "text", "prompt_used"]:
                        if key in ai_response and isinstance(ai_response[key], str) and ai_response[key].strip():
                            ai_text = ai_response[key]
                            print(f"✅ Found text in {key} for row {result.get('row_index')}")
                            break
                    
                    # If still no text, look for any substantial string value
                    if not ai_text:
                        for key, value in ai_response.items():
                            if isinstance(value, str) and len(value.strip()) > 50:
                                ai_text = value
                                print(f"✅ Found substantial text in {key} for row {result.get('row_index')}")
                                break
            
            # Clean the AI response
            cleaned_prompt = clean_ai_response(ai_text) if ai_text else ""
            
            # Build row with original data, replacing Prompt column if it exists
            row = []
            for header in original_headers:
                if header == "Prompt":
                    # Replace the empty/existing Prompt column with AI response
                    row.append(cleaned_prompt)
                else:
                    row.append(str(input_data.get(header, "")))
            
            # If Prompt column didn't exist in original headers, add it now
            if "Prompt" not in original_headers:
                row.append(cleaned_prompt)
            
            data_rows.append(row)
        
        return data_rows
    
    print("=== Testing Complete AI Response Processing Workflow ===")
    
    # Test the formatting
    formatted_data = format_ai_results_for_sheets(processed_results)
    
    print(f"\n📊 Results:")
    print(f"   - Total rows: {len(formatted_data)}")
    print(f"   - Headers: {formatted_data[0] if formatted_data else 'None'}")
    
    # Check each data row
    for i, row in enumerate(formatted_data[1:], 1):  # Skip header row
        prompt_content = row[-1] if row else ""  # Last column should be Prompt
        print(f"\n📝 Row {i}:")
        print(f"   - Description: {row[0] if row else 'N/A'}")
        print(f"   - Prompt length: {len(prompt_content)}")
        print(f"   - Prompt preview: {prompt_content[:150]}..." if prompt_content else "   - Prompt: EMPTY!")
    
    # Verify the prompt column is properly populated
    prompt_column_index = -1  # Should be last column
    if "Prompt" in formatted_data[0]:
        prompt_column_index = formatted_data[0].index("Prompt")
    
    print(f"\n🎯 Prompt Column Analysis:")
    print(f"   - Prompt column index: {prompt_column_index}")
    
    all_prompts_populated = True
    for i, row in enumerate(formatted_data[1:], 1):  # Skip header
        if len(row) > prompt_column_index and prompt_column_index >= 0:
            prompt_content = row[prompt_column_index]
            is_populated = bool(prompt_content and prompt_content.strip())
            print(f"   - Row {i} prompt populated: {is_populated} ({len(prompt_content)} chars)")
            if not is_populated:
                all_prompts_populated = False
        else:
            print(f"   - Row {i}: Missing prompt column!")
            all_prompts_populated = False
    
    print(f"\n🎉 Test Result: {'SUCCESS' if all_prompts_populated else 'FAILED'}")
    if all_prompts_populated:
        print("   ✅ All AI responses successfully extracted to Prompt column!")
    else:
        print("   ❌ Some AI responses were not properly extracted!")
    
    return formatted_data

if __name__ == "__main__":
    asyncio.run(test_complete_workflow())
