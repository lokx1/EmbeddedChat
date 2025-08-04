#!/usr/bin/env python3
"""
Test script to verify AI response extraction logic
"""

def test_ai_response_extraction():
    """Test the AI response extraction logic with the actual data structure"""
    
    # Sample AI response data structure based on the frontend logs
    sample_ai_response = {
        "type": "ollama_asset_generation",
        "description": "",
        "output_format": "PNG",
        "generated_url": "https://ollama-assets.local/png/0.png",
        "ai_response": """Okay, here's a comprehensive creative brief for generating a Task Manager app logo, aiming for a professional and detailed response.

**Asset Generation Request: Task Manager App Logo**

**1. TECHNICAL SPECIFICATIONS:**

* **Dimensions:** 800x600 pixels (width x height). This size balances visual impact with scalability across various platforms (iOS, Android, web).
* **File Format:** PNG (Portable Network Graphics). This format supports transparency, which is crucial for a logo that might be used on backgrounds.
* **Compression:** We'll use a lossless compression setting (JPEG compression with a quality setting of 80-90%). This preserves image quality while minimizing file size. We'll also consider a slightly higher compression setting (70%) for web use to optimize loading times.
* **Resolution:** 300 DPI (Dots Per Inch). This ensures high print quality and prevents pixelation when scaled down.
* **Color Depth:** 24-bit color (RGB). This provides a wider color gamut, resulting in richer and more vibrant colors.
* **Transparency:** A subtle, semi-transparent background is desired for the logo. We'll use a light gray (#F5F5F5) as the background for the logo.

**2. DESIGN & STYLE GUIDELINES:**

* **Visual Style:** Modern, minimalist, and slightly geometric. Avoid overly detailed illustrations. We're aiming for a clean, professional look. Think Scandinavian design principles – understated elegance.
* **Layout & Composition:** A circular or slightly offset arrangement would be ideal. The logo should be centered or slightly off-center for a dynamic feel. The text "Task Manager" should be prominent but not overwhelming.""",
        "metadata": {
            "model": "gemma3:1b",
            "provider": "ollama",
            "quality": "local_generation",
            "size": "1024x1024",
            "processing_time": "9868.2ms",
            "tokens_evaluated": 1135,
            "eval_duration": "8608.3ms"
        },
        "prompt_used": "\n Asset Generation Request:\n Description: \n Output Format: PNG\n \n Based on this asset request: {\n \"Description\": \"Design a Task Manager app logo..."
    }
    
    # Test the extraction logic
    def extract_ai_response_text(ai_response):
        """Extract AI response text using the same logic as the backend"""
        ai_text = ""
        if ai_response:
            # Enhanced extraction logic based on the actual AI response structure
            if "ai_response" in ai_response:
                if isinstance(ai_response["ai_response"], str):
                    ai_text = ai_response["ai_response"]
                    print(f"✅ Found ai_response as string: {ai_text[:100]}...")
                elif isinstance(ai_response["ai_response"], dict):
                    # Nested structure - try to get text from nested object
                    nested = ai_response["ai_response"]
                    print(f"🔍 Nested ai_response keys: {list(nested.keys())}")
                    if "ai_response" in nested:
                        ai_text = nested["ai_response"]
                    elif "text" in nested:
                        ai_text = nested["text"]
                    elif "content" in nested:
                        ai_text = nested["content"]
                    elif "response" in nested:
                        ai_text = nested["response"]
            
            # Fallback to other possible keys if ai_response didn't yield text
            if not ai_text:
                print(f"🔍 Trying fallback extraction methods...")
                # Try direct text fields
                for key in ["generated_text", "response", "content", "text", "prompt_used"]:
                    if key in ai_response and isinstance(ai_response[key], str) and ai_response[key].strip():
                        ai_text = ai_response[key]
                        print(f"✅ Found text in {key}: {ai_text[:100]}...")
                        break
                
                # If still no text, look for any substantial string value
                if not ai_text:
                    for key, value in ai_response.items():
                        if isinstance(value, str) and len(value.strip()) > 50:  # Substantial text content
                            ai_text = value
                            print(f"✅ Found substantial text in {key}: {ai_text[:100]}...")
                            break
        
        return ai_text
    
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
    
    print("=== Testing AI Response Extraction ===")
    print(f"Sample AI response keys: {list(sample_ai_response.keys())}")
    print(f"AI response type: {type(sample_ai_response.get('ai_response'))}")
    
    # Extract text
    extracted_text = extract_ai_response_text(sample_ai_response)
    print(f"\n📝 Extracted text length: {len(extracted_text)}")
    print(f"📝 First 200 chars: {extracted_text[:200]}...")
    
    # Clean text
    cleaned_text = clean_ai_response(extracted_text)
    print(f"\n🧹 Cleaned text length: {len(cleaned_text)}")
    print(f"🧹 First 200 chars: {cleaned_text[:200]}...")
    
    # Test with the actual structure from the user's logs
    processed_result = {
        "row_index": 1,
        "input_data": {
            "Description": "Design a Task Manager app logo",
            "Example Asset URL": "https://static.wikia.nocookie.net/logopedia/images/9/97/Task_Manager_2024.png/revision/latest?cb=20240127035026",
            "Desired Output Format": "PNG",
            "Model Specification": "OpenAI",
            "Prompt": ""
        },
        "ai_response": sample_ai_response,
        "status": "success",
        "provider": "ollama",
        "model": "gemma3:1b",
        "timestamp": "2025-08-04T11:10:50.154613"
    }
    
    print(f"\n=== Testing Complete Workflow ===")
    
    # Simulate the format_ai_results_for_sheets method
    input_data = processed_result.get("input_data", {})
    ai_response = processed_result.get("ai_response", {})
    
    # Get original headers
    original_headers = list(input_data.keys())
    print(f"📊 Original headers: {original_headers}")
    
    # Build row
    row = []
    for header in original_headers:
        row.append(str(input_data.get(header, "")))
    
    # Extract and clean AI response
    ai_text = extract_ai_response_text(ai_response)
    cleaned_prompt = clean_ai_response(ai_text)
    row.append(cleaned_prompt)
    
    print(f"📋 Final row length: {len(row)}")
    print(f"📋 Headers + Prompt: {original_headers + ['Prompt']}")
    print(f"📋 Row data (first 3 fields): {row[:3]}")
    print(f"📋 Prompt content (first 200 chars): {row[-1][:200]}...")
    
    return row

if __name__ == "__main__":
    test_ai_response_extraction()
