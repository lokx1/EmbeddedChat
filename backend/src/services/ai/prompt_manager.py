from typing import Dict, List, Optional, Any
import json
import os
from datetime import datetime

class PromptManager:
    """Manages AI prompts and templates"""
    
    def __init__(self):
        self.system_prompts = self._load_system_prompts()
        self.templates = self._load_templates()
        
    def _load_system_prompts(self) -> Dict[str, str]:
        """Load system prompts for different AI providers"""
        return {
            "default": """You are a helpful, harmless, and honest AI assistant. 
You provide accurate, informative responses while being respectful and considerate.
Always aim to be helpful while maintaining safety and ethical guidelines.""",
            
            "chat_assistant": """You are an advanced AI chat assistant with the following capabilities:

🧠 **Thinking Process**: Before responding, you think through problems step-by-step
📚 **Memory System**: You remember important context from conversations
🔍 **Context Awareness**: You use relevant information from previous interactions
💡 **Problem Solving**: You break down complex questions into manageable parts

**Your Response Style:**
- Be conversational and engaging
- Show your reasoning when helpful
- Ask clarifying questions when needed
- Provide actionable insights and solutions
- Remember user preferences and context

**Memory Guidelines:**
- Extract key facts, preferences, and context from conversations
- Store important decisions and outcomes
- Remember user's goals and ongoing projects
- Note personal preferences and communication style""",

            "thinking_display": """When showing your thinking process, structure it as follows:

1. **Understanding**: What is the user asking?
2. **Analysis**: What information do I need to consider?
3. **Context**: What relevant background knowledge applies?
4. **Approach**: How should I structure my response?
5. **Verification**: Does my reasoning make sense?

Be transparent about your thought process while keeping it concise and relevant.""",

            "memory_extraction": """You are an expert at extracting key information for memory storage.

From each conversation, identify:
- **Facts**: Concrete information, decisions, or outcomes
- **Preferences**: User likes, dislikes, or stated preferences  
- **Context**: Background information relevant to future conversations
- **Goals**: Stated objectives or projects the user is working on
- **Patterns**: Recurring themes or topics of interest

Format as structured data that will be useful for future reference.""",

            "code_assistant": """You are an expert programming assistant with deep knowledge across multiple languages and frameworks.

**Your Expertise Includes:**
- Frontend: React, Vue, Angular, TypeScript, JavaScript
- Backend: Python, Node.js, Java, C#, Go
- Databases: SQL, NoSQL, ORM patterns
- DevOps: Docker, CI/CD, cloud platforms
- Architecture: Design patterns, system design, best practices

**When Helping With Code:**
- Provide complete, working examples
- Explain your reasoning and choices
- Suggest best practices and optimizations
- Consider security, performance, and maintainability
- Ask about requirements and constraints when needed""",

            "document_analysis": """You are specialized in analyzing and understanding documents.

**Your Capabilities:**
- Extract key information and summaries
- Identify important concepts and relationships
- Answer questions based on document content
- Compare and contrast information across documents
- Provide structured analysis and insights

**Analysis Approach:**
- Read thoroughly and identify main themes
- Extract factual information accurately
- Provide relevant context and explanations
- Highlight important details and implications"""
        }
    
    def _load_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load prompt templates for different scenarios"""
        return {
            "conversation_summary": {
                "template": """Summarize this conversation focusing on:
- Main topics discussed
- Key decisions or outcomes
- Important facts or information shared
- Action items or next steps

Conversation:
{conversation_text}

Provide a concise summary that captures the essential points.""",
                "variables": ["conversation_text"]
            },
            
            "memory_extraction": {
                "template": """Extract key information from this conversation that should be remembered:

User message: {user_message}
Assistant response: {assistant_response}
Context: {context}

Extract:
1. Important facts or information
2. User preferences revealed
3. Context for future conversations
4. Relevance score (0-1)

Format as JSON with clear, actionable memory items.""",
                "variables": ["user_message", "assistant_response", "context"]
            },
            
            "thinking_process": {
                "template": """Think through this request step by step:

User request: {user_request}
Available context: {context}
Previous conversation: {history}

Show your thinking process:
1. What is the user asking for?
2. What information do I need to consider?
3. How should I approach this?
4. What's the best way to help?

Then provide your response.""",
                "variables": ["user_request", "context", "history"]
            },
            
            "document_qa": {
                "template": """Based on the following document content, answer the user's question:

Document: {document_title}
Content: {document_content}

User question: {user_question}

Provide a comprehensive answer based on the document content. 
If the information isn't in the document, clearly state that.""",
                "variables": ["document_title", "document_content", "user_question"]
            },
            
            "code_review": {
                "template": """Review this code and provide feedback:

Language: {language}
Purpose: {purpose}
Code:
```{language}
{code}
```

Please analyze:
1. Code quality and best practices
2. Potential bugs or issues
3. Performance considerations
4. Security implications
5. Suggestions for improvement

Provide constructive, specific feedback.""",
                "variables": ["language", "purpose", "code"]
            }
        }
    
    def get_system_prompt(self, prompt_type: str = "default") -> str:
        """Get system prompt by type"""
        return self.system_prompts.get(prompt_type, self.system_prompts["default"])
    
    def get_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get prompt template by name"""
        return self.templates.get(template_name)
    
    def format_prompt(self, template_name: str, **variables) -> str:
        """Format a prompt template with variables"""
        template_data = self.get_template(template_name)
        if not template_data:
            raise ValueError(f"Template '{template_name}' not found")
        
        template = template_data["template"]
        required_vars = template_data.get("variables", [])
        
        # Check for missing variables
        missing_vars = [var for var in required_vars if var not in variables]
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")
        
        return template.format(**variables)
    
    def create_conversation_messages(
        self,
        user_message: str,
        system_prompt_type: str = "chat_assistant",
        conversation_history: List[Dict[str, str]] = None,
        context: str = ""
    ) -> List[Dict[str, str]]:
        """Create formatted messages for AI providers"""
        
        messages = []
        
        # Add system prompt
        system_prompt = self.get_system_prompt(system_prompt_type)
        if context:
            system_prompt += f"\n\nRelevant Context:\n{context}"
        
        messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current user message
        messages.append({
            "role": "user", 
            "content": user_message
        })
        
        return messages
    
    def create_thinking_prompt(
        self,
        user_request: str,
        context: str = "",
        history: str = ""
    ) -> str:
        """Create a prompt for thinking display"""
        return self.format_prompt(
            "thinking_process",
            user_request=user_request,
            context=context or "No specific context provided",
            history=history or "No previous conversation"
        )
    
    def create_memory_extraction_prompt(
        self,
        user_message: str,
        assistant_response: str,
        context: str = ""
    ) -> str:
        """Create prompt for memory extraction"""
        return self.format_prompt(
            "memory_extraction",
            user_message=user_message,
            assistant_response=assistant_response,
            context=context or "General conversation"
        )
    
    def create_document_qa_prompt(
        self,
        document_title: str,
        document_content: str,
        user_question: str
    ) -> str:
        """Create prompt for document Q&A"""
        return self.format_prompt(
            "document_qa",
            document_title=document_title,
            document_content=document_content,
            user_question=user_question
        )
    
    def add_custom_prompt(self, name: str, content: str, prompt_type: str = "system"):
        """Add custom prompt"""
        if prompt_type == "system":
            self.system_prompts[name] = content
        elif prompt_type == "template":
            self.templates[name] = {
                "template": content,
                "variables": []  # Will need to be set manually
            }
    
    def get_available_prompts(self) -> Dict[str, List[str]]:
        """Get list of available prompts"""
        return {
            "system_prompts": list(self.system_prompts.keys()),
            "templates": list(self.templates.keys())
        }
    
    def export_prompts(self, filepath: str):
        """Export prompts to JSON file"""
        data = {
            "system_prompts": self.system_prompts,
            "templates": self.templates,
            "exported_at": datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def import_prompts(self, filepath: str):
        """Import prompts from JSON file"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Prompt file not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if "system_prompts" in data:
            self.system_prompts.update(data["system_prompts"])
        
        if "templates" in data:
            self.templates.update(data["templates"])

# Global instance
prompt_manager = PromptManager()
