import re
import json
import asyncio
from typing import Dict, List, Any, Optional, AsyncGenerator
from datetime import datetime

class ResponseProcessor:
    """Processes and enhances AI responses"""
    
    def __init__(self):
        self.markdown_patterns = self._init_markdown_patterns()
        self.code_block_pattern = re.compile(r'```(\w+)?\n(.*?)```', re.DOTALL)
        self.thinking_pattern = re.compile(r'<thinking>(.*?)</thinking>', re.DOTALL | re.IGNORECASE)
        
    def _init_markdown_patterns(self) -> Dict[str, re.Pattern]:
        """Initialize common markdown patterns"""
        return {
            'headers': re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE),
            'bold': re.compile(r'\*\*(.*?)\*\*'),
            'italic': re.compile(r'\*(.*?)\*'),
            'code_inline': re.compile(r'`([^`]+)`'),
            'links': re.compile(r'\[([^\]]+)\]\(([^)]+)\)'),
            'lists': re.compile(r'^[-*+]\s+(.+)$', re.MULTILINE),
            'numbered_lists': re.compile(r'^\d+\.\s+(.+)$', re.MULTILINE)
        }
    
    async def process_streaming_response(
        self,
        response_stream: AsyncGenerator[str, None],
        extract_thinking: bool = True,
        format_markdown: bool = True,
        track_metrics: bool = True
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Process streaming response with enhancements"""
        
        full_response = ""
        thinking_content = ""
        chunk_count = 0
        start_time = datetime.now()
        
        async for chunk in response_stream:
            chunk_count += 1
            full_response += chunk
            
            # Extract thinking if present
            if extract_thinking:
                thinking_match = self.thinking_pattern.search(full_response)
                if thinking_match:
                    thinking_content = thinking_match.group(1).strip()
                    # Remove thinking from main response
                    chunk = self.thinking_pattern.sub('', chunk)
            
            # Process chunk
            processed_chunk = {
                "content": chunk,
                "chunk_id": chunk_count,
                "timestamp": datetime.now().isoformat(),
                "type": "content"
            }
            
            # Add thinking if found
            if thinking_content and chunk_count == 1:
                yield {
                    "content": thinking_content,
                    "type": "thinking",
                    "timestamp": datetime.now().isoformat()
                }
            
            yield processed_chunk
        
        # Final processing metrics
        if track_metrics:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            yield {
                "type": "metrics",
                "total_chunks": chunk_count,
                "total_characters": len(full_response),
                "duration_seconds": duration,
                "words_per_second": len(full_response.split()) / duration if duration > 0 else 0,
                "timestamp": end_time.isoformat()
            }
    
    def extract_thinking_content(self, text: str) -> tuple[str, str]:
        """Extract thinking content from response"""
        thinking_match = self.thinking_pattern.search(text)
        
        if thinking_match:
            thinking = thinking_match.group(1).strip()
            cleaned_text = self.thinking_pattern.sub('', text).strip()
            return thinking, cleaned_text
        
        return "", text
    
    def format_markdown(self, text: str) -> Dict[str, Any]:
        """Parse and format markdown content"""
        formatted_content = {
            "raw_text": text,
            "formatted_html": self._markdown_to_html(text),
            "elements": self._extract_markdown_elements(text),
            "word_count": len(text.split()),
            "reading_time_minutes": max(1, len(text.split()) // 200)  # ~200 words per minute
        }
        
        return formatted_content
    
    def _markdown_to_html(self, text: str) -> str:
        """Convert markdown to HTML"""
        html = text
        
        # Headers
        html = self.markdown_patterns['headers'].sub(
            lambda m: f'<h{len(m.group(1))}>{m.group(2)}</h{len(m.group(1))}>',
            html
        )
        
        # Bold and italic
        html = self.markdown_patterns['bold'].sub(r'<strong>\1</strong>', html)
        html = self.markdown_patterns['italic'].sub(r'<em>\1</em>', html)
        
        # Code blocks
        html = self.code_block_pattern.sub(
            lambda m: f'<pre><code class="language-{m.group(1) or ""}">{m.group(2)}</code></pre>',
            html
        )
        
        # Inline code
        html = self.markdown_patterns['code_inline'].sub(r'<code>\1</code>', html)
        
        # Links
        html = self.markdown_patterns['links'].sub(r'<a href="\2">\1</a>', html)
        
        # Lists
        html = self.markdown_patterns['lists'].sub(r'<li>\1</li>', html)
        html = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', html, flags=re.DOTALL)
        
        # Paragraphs
        paragraphs = html.split('\n\n')
        html = '\n'.join(f'<p>{p.strip()}</p>' for p in paragraphs if p.strip())
        
        return html
    
    def _extract_markdown_elements(self, text: str) -> Dict[str, List[Any]]:
        """Extract structured elements from markdown"""
        elements = {
            "headers": [],
            "code_blocks": [],
            "links": [],
            "lists": [],
            "emphasis": []
        }
        
        # Extract headers
        for match in self.markdown_patterns['headers'].finditer(text):
            elements["headers"].append({
                "level": len(match.group(1)),
                "text": match.group(2),
                "position": match.span()
            })
        
        # Extract code blocks
        for match in self.code_block_pattern.finditer(text):
            elements["code_blocks"].append({
                "language": match.group(1) or "text",
                "code": match.group(2).strip(),
                "position": match.span()
            })
        
        # Extract links
        for match in self.markdown_patterns['links'].finditer(text):
            elements["links"].append({
                "text": match.group(1),
                "url": match.group(2),
                "position": match.span()
            })
        
        # Extract lists
        for match in self.markdown_patterns['lists'].finditer(text):
            elements["lists"].append({
                "type": "unordered",
                "text": match.group(1),
                "position": match.span()
            })
        
        for match in self.markdown_patterns['numbered_lists'].finditer(text):
            elements["lists"].append({
                "type": "ordered", 
                "text": match.group(1),
                "position": match.span()
            })
        
        return elements
    
    def extract_code_blocks(self, text: str) -> List[Dict[str, Any]]:
        """Extract code blocks with metadata"""
        code_blocks = []
        
        for match in self.code_block_pattern.finditer(text):
            language = match.group(1) or "text"
            code = match.group(2).strip()
            
            code_blocks.append({
                "language": language,
                "code": code,
                "line_count": len(code.split('\n')),
                "character_count": len(code),
                "position": match.span(),
                "is_executable": language in ['python', 'javascript', 'bash', 'sql']
            })
        
        return code_blocks
    
    def analyze_response_quality(self, text: str) -> Dict[str, Any]:
        """Analyze response quality metrics"""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        
        quality_metrics = {
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "avg_sentence_length": len(words) / max(1, len([s for s in sentences if s.strip()])),
            "paragraph_count": len([p for p in text.split('\n\n') if p.strip()]),
            "code_blocks": len(self.code_block_pattern.findall(text)),
            "has_thinking": bool(self.thinking_pattern.search(text)),
            "readability_score": self._calculate_readability(text),
            "structure_score": self._calculate_structure_score(text)
        }
        
        return quality_metrics
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate basic readability score (0-1)"""
        words = text.split()
        if not words:
            return 0.0
        
        # Simple readability based on average word length and sentence length
        avg_word_length = sum(len(word.strip('.,!?;:')) for word in words) / len(words)
        sentences = re.split(r'[.!?]+', text)
        avg_sentence_length = len(words) / max(1, len([s for s in sentences if s.strip()]))
        
        # Normalize scores (ideal: 5-6 chars per word, 15-20 words per sentence)
        word_score = max(0, 1 - abs(avg_word_length - 5.5) / 10)
        sentence_score = max(0, 1 - abs(avg_sentence_length - 17.5) / 20)
        
        return (word_score + sentence_score) / 2
    
    def _calculate_structure_score(self, text: str) -> float:
        """Calculate structure quality score (0-1)"""
        score = 0.0
        
        # Check for headers
        if self.markdown_patterns['headers'].search(text):
            score += 0.3
        
        # Check for lists
        if self.markdown_patterns['lists'].search(text) or self.markdown_patterns['numbered_lists'].search(text):
            score += 0.2
        
        # Check for code blocks
        if self.code_block_pattern.search(text):
            score += 0.2
        
        # Check for paragraphs
        paragraphs = len([p for p in text.split('\n\n') if p.strip()])
        if paragraphs > 1:
            score += 0.2
        
        # Check for emphasis
        if self.markdown_patterns['bold'].search(text) or self.markdown_patterns['italic'].search(text):
            score += 0.1
        
        return min(1.0, score)
    
    def create_response_summary(self, text: str) -> Dict[str, Any]:
        """Create comprehensive response summary"""
        thinking, main_content = self.extract_thinking_content(text)
        formatted = self.format_markdown(main_content)
        quality = self.analyze_response_quality(main_content)
        code_blocks = self.extract_code_blocks(main_content)
        
        return {
            "summary": {
                "has_thinking": bool(thinking),
                "thinking_length": len(thinking.split()) if thinking else 0,
                "main_content_length": len(main_content.split()),
                "total_length": len(text.split()),
                "processing_timestamp": datetime.now().isoformat()
            },
            "thinking_content": thinking,
            "main_content": main_content,
            "formatted_content": formatted,
            "quality_metrics": quality,
            "code_blocks": code_blocks,
            "elements": formatted["elements"]
        }
    
    async def enhance_response_with_context(
        self,
        response: str,
        context: Dict[str, Any],
        user_preferences: Dict[str, Any] = None
    ) -> str:
        """Enhance response based on context and preferences"""
        enhanced = response
        
        # Add context references if relevant
        if context.get("relevant_memories"):
            # Could add subtle references to previous conversations
            pass
        
        # Apply user preferences
        if user_preferences:
            # Adjust tone, verbosity, technical level based on preferences
            if user_preferences.get("prefer_concise"):
                # Logic to make response more concise
                pass
            
            if user_preferences.get("technical_level") == "beginner":
                # Logic to simplify technical terms
                pass
        
        return enhanced

# Global instance
response_processor = ResponseProcessor()
