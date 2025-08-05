#!/usr/bin/env python3
"""
Simulate AI response structures to test extraction logic
"""

def test_ai_extraction_logic():
    print("🧪 Testing AI extraction logic with different response structures...")
    
    # Simulate different AI response structures
    test_cases = [
        {
            "name": "Ollama Response",
            "ai_response": {
                "ai_response": "Đây là câu trả lời từ Ollama AI. Nội dung rất chi tiết và hữu ích cho người dùng.",
                "type": "ollama_asset_generation",
                "description": "Test description",
                "metadata": {"model": "llama3.2", "provider": "ollama"}
            }
        },
        {
            "name": "OpenAI Response",
            "ai_response": {
                "prompt_used": "Đây là câu trả lời từ OpenAI. Content được tạo ra từ GPT model.",
                "type": "asset_generation",
                "generated_url": "https://example.com/asset.png",
                "metadata": {"model": "gpt-4o", "provider": "openai"}
            }
        },
        {
            "name": "Simulation Response",
            "ai_response": {
                "note": "This is a simulated response for demonstration purposes. Đây là nội dung demo.",
                "type": "simulated_asset_generation",
                "generated_url": "https://demo.com/asset.png"
            }
        },
        {
            "name": "Claude Response",
            "ai_response": {
                "content": "Đây là response từ Claude AI. Nội dung được tạo bởi Anthropic Claude model.",
                "type": "asset_generation",
                "metadata": {"model": "claude-3-5-sonnet", "provider": "claude"}
            }
        }
    ]
    
    # Test extraction logic
    for test_case in test_cases:
        print(f"\n🔬 Testing: {test_case['name']}")
        ai_response = test_case["ai_response"]
        
        print(f"   Input structure: {list(ai_response.keys())}")
        
        # Simulate the extraction logic
        ai_text = ""
        
        # FIXED logic from our update
        if "ai_response" in ai_response and isinstance(ai_response["ai_response"], str):
            ai_text = ai_response["ai_response"]
            print(f"   ✅ Found ai_response (Ollama): {ai_text[:50]}...")
        
        elif not ai_text:
            # Try direct text fields from different providers
            for key in ["prompt_used", "note", "response", "content", "text", "generated_text"]:
                if key in ai_response and isinstance(ai_response[key], str) and ai_response[key].strip():
                    ai_text = ai_response[key]
                    print(f"   ✅ Found text in {key}: {ai_text[:50]}...")
                    break
            
            # If still no text, look for any substantial string value
            if not ai_text:
                for key, value in ai_response.items():
                    if isinstance(value, str) and len(value.strip()) > 20:
                        ai_text = value
                        print(f"   ✅ Found substantial text in {key}: {ai_text[:50]}...")
                        break
            
            # Last resort: create summary
            if not ai_text:
                summary_parts = []
                for key, value in ai_response.items():
                    if isinstance(value, str) and value.strip() and key not in ["type", "provider", "model"]:
                        summary_parts.append(f"{key}: {value}")
                
                if summary_parts:
                    ai_text = " | ".join(summary_parts[:3])
                    print(f"   ⚠️ Created summary: {ai_text[:50]}...")
        
        # Final result
        if ai_text:
            print(f"   🎯 EXTRACTED: '{ai_text[:80]}...' (length: {len(ai_text)})")
        else:
            print(f"   ❌ FAILED: No text extracted")
    
    print(f"\n✅ Extraction logic test completed!")

if __name__ == "__main__":
    test_ai_extraction_logic()
