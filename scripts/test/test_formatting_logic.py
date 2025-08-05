#!/usr/bin/env python3
"""
Quick test of AI Processing formatting logic  
"""
import sys
sys.path.append('d:/EmbeddedChat/backend/src')

def test_ai_formatting():
    print("🔧 Testing AI formatting logic...")
    
    # Import the component class
    from services.workflow.component_registry import AIProcessingComponent
    
    # Create test data similar to actual workflow output
    test_processed_results = [
        {
            "row_index": 1,
            "input_data": {
                "Name": "Pha cafe",
                "Task": "Tạo ra câu chuyện về pha cafe",
                "Prompt": ""  # Empty prompt column
            },
            "ai_response": {
                "ai_response": "Câu chuyện về pha cafe: Trong không gian ấm cúng của quán cafe nhỏ, barista khéo léo đổ nước nóng vào filter, tạo nên những giọt cafe đen đậm đà. Mùi hương quyến rũ lan tỏa khắp không gian..."
            },
            "status": "success",
            "provider": "ollama",
            "model": "llama3.2"
        },
        {
            "row_index": 2, 
            "input_data": {
                "Name": "Đọc sách",
                "Task": "Tạo ra câu chuyện về đọc sách",
                "Prompt": ""
            },
            "ai_response": {
                "ai_response": "Câu chuyện về đọc sách: Dưới ánh đèn vàng ấm áp, cô gái trẻ lật từng trang sách một cách nhẹ nhàng. Những dòng chữ như những cánh cửa mở ra thế giới mới..."
            },
            "status": "success",
            "provider": "ollama", 
            "model": "llama3.2"
        }
    ]
    
    # Create AI Processing component instance
    ai_component = AIProcessingComponent()
    
    # Test the formatting method
    print("🔄 Calling _format_ai_results_for_sheets...")
    formatted_data = ai_component._format_ai_results_for_sheets(test_processed_results)
    
    print(f"\n📊 Formatted data structure:")
    print(f"   Total rows: {len(formatted_data)}")
    
    if len(formatted_data) > 0:
        headers = formatted_data[0]
        print(f"   Headers: {headers}")
        
        # Check if Prompt column exists
        if "Prompt" in headers:
            prompt_index = headers.index("Prompt")
            print(f"   ✅ Prompt column found at index: {prompt_index}")
            
            # Check data rows
            for i, row in enumerate(formatted_data[1:], 1):
                if len(row) > prompt_index:
                    prompt_content = row[prompt_index]
                    print(f"   Row {i} Prompt: '{prompt_content[:100]}...' (length: {len(prompt_content)})")
                    
                    if prompt_content and len(prompt_content) > 10:
                        print(f"   ✅ Row {i}: SUCCESS - Prompt has content!")
                    else:
                        print(f"   ❌ Row {i}: FAIL - Prompt is empty")
                else:
                    print(f"   ❌ Row {i}: FAIL - Row too short")
        else:
            print(f"   ❌ FAIL: No Prompt column found in headers")
    else:
        print(f"   ❌ FAIL: No formatted data returned")
    
    return formatted_data

if __name__ == "__main__":
    test_ai_formatting()
