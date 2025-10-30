import os
import json
from typing import List, Dict, Any
import google.generativeai as genai
from fastapi import HTTPException, status
from dotenv import load_dotenv

load_dotenv()

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        try:
            genai.configure(api_key=self.api_key)
            try:
                self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
            except:
                try:
                    self.model = genai.GenerativeModel('gemini-1.5-flash')
                except:
                    try:
                        self.model = genai.GenerativeModel('gemini-pro')
                    except:
                        self.model = genai.GenerativeModel('models/gemini-pro')
            print("✓ Gemini AI service initialized successfully")
        except Exception as e:
            print(f"⚠ Failed to initialize Gemini AI: {e}")
            self.model = None
    
    def is_configured(self) -> bool:
        """Check if Gemini AI is properly configured."""
        return self.model is not None
    
    def generate_summary(self, content: str, max_length: int = 300) -> str:
        """Generate a concise summary of the given content."""
        if not self.is_configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LLM service is not configured. Please set GEMINI_API_KEY."
            )
        
        try:
            prompt = f"""
Please provide a concise summary of the following text in approximately {max_length} words. 
Focus on the main concepts, key points, and important information.

Text to summarize:
{content}

Summary:
"""
            
            print(f"Generating summary with model: {self.model}")
            response = self.model.generate_content(prompt)
            print(f"Response received: {response}")
            
            if hasattr(response, 'text') and response.text:
                summary = response.text.strip()
            elif hasattr(response, 'candidates') and response.candidates:
                summary = response.candidates[0].content.parts[0].text.strip()
            else:
                print(f"Unexpected response format: {response}")
                summary = self._generate_fallback_summary(content, max_length)
            
            if not summary:
                summary = self._generate_fallback_summary(content, max_length)
            
            return summary
            
        except Exception as e:
            print(f"Gemini summary error: {e}")
            print(f"Error type: {type(e)}")
            # Return fallback summary instead of raising error
            return self._generate_fallback_summary(content, max_length)
    
    def generate_quiz(self, content: str, num_mcq: int = 10, num_short: int = 5) -> List[Dict[str, Any]]:
        """Generate quiz questions from the given content with specified MCQ and short answer counts."""
        if not self.is_configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LLM service is not configured. Please set GEMINI_API_KEY."
            )
        
        total_questions = num_mcq + num_short
        
        try:
            prompt = f"""
Based on the following text, create exactly {total_questions} quiz questions:
- {num_mcq} multiple choice questions (MCQs) with 4 options each
- {num_short} short answer questions

Make sure the questions cover different aspects of the content and vary in difficulty.
Format your response as a JSON array with the following structure:

[
  {{
    "question": "Question text here",
    "type": "multiple_choice",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": "Option A",
    "explanation": "Brief explanation of why this is correct",
    "difficulty": "easy|medium|hard"
  }},
  {{
    "question": "Question text here",
    "type": "short_answer",
    "sample_answer": "Sample answer here",
    "explanation": "What should be included in the answer",
    "difficulty": "easy|medium|hard"
  }}
]

Text content:
{content}

Quiz Questions (JSON format only):
"""
            
            response = self.model.generate_content(prompt)
            quiz_text = response.text.strip()
            
            # Clean up the response to extract JSON
            if "```json" in quiz_text:
                quiz_text = quiz_text.split("```json")[1].split("```")[0].strip()
            elif "```" in quiz_text:
                quiz_text = quiz_text.split("```")[1].strip()
            
            try:
                quiz_questions = json.loads(quiz_text)
                con
                # Validate the structure
                if not isinstance(quiz_questions, list):
                    raise ValueError("Response is not a list")
                
                for q in quiz_questions:
                    if not isinstance(q, dict) or "question" not in q or "type" not in q:
                        raise ValueError("Invalid question structure")
                
                return quiz_questions
                
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                print(f"Raw response: {quiz_text}")
                
                # Fallback: create a simple quiz structure
                return self._create_fallback_quiz(content, num_mcq, num_short)
            
        except Exception as e:
            print(f"Gemini quiz error: {e}")
            # Return fallback quiz instead of raising error
            return self._create_fallback_quiz(content, num_mcq, num_short)
    
    def extract_concepts(self, content: str, max_concepts: int = 10) -> List[str]:
        """Extract key concepts and terms from the given content."""
        if not self.is_configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LLM service is not configured. Please set GEMINI_API_KEY."
            )
        
        try:
            prompt = f"""
Analyze the following text and extract the most important key concepts, terms, and topics.
Return only the concepts as a JSON array of strings, with no additional text or formatting.
Limit to {max_concepts} most important concepts.

Example format: ["Concept 1", "Concept 2", "Concept 3"]

Text content:
{content}

Key Concepts (JSON array only):
"""
            
            response = self.model.generate_content(prompt)
            concepts_text = response.text.strip()
            
            # Clean up the response to extract JSON
            if "```json" in concepts_text:
                concepts_text = concepts_text.split("```json")[1].split("```")[0].strip()
            elif "```" in concepts_text:
                concepts_text = concepts_text.split("```")[1].strip()
            
            try:
                concepts = json.loads(concepts_text)
                
                # Validate the structure
                if not isinstance(concepts, list):
                    raise ValueError("Response is not a list")
                
                # Ensure all items are strings and limit the count
                concepts = [str(concept) for concept in concepts if concept][:max_concepts]
                
                return concepts
                
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                print(f"Raw response: {concepts_text}")
                
                return self._extract_fallback_concepts(content, max_concepts)
            
        except Exception as e:
            print(f"Gemini concepts error: {e}")
            # Return fallback concepts instead of raising error
            return self._extract_fallback_concepts(content, max_concepts)
    
    def _create_fallback_quiz(self, content: str, num_mcq: int = 10, num_short: int = 5) -> List[Dict[str, Any]]:
        """Create a simple fallback quiz when AI generation fails."""
        mcq_questions = []
        short_questions = []
        
        # Generate MCQ questions
        mcq_templates = [
            {
                "question": "Which of the following best describes the main topic of this material?",
                "options": ["Educational content", "Technical documentation", "Research material", "General information"],
                "correct_answer": "Educational content"
            },
            {
                "question": "What type of document is this most likely to be?",
                "options": ["Study notes", "Technical manual", "News article", "Fiction"],
                "correct_answer": "Study notes"
            },
            {
                "question": "Based on the content, what is the primary purpose?",
                "options": ["Learning and education", "Entertainment", "News reporting", "Marketing"],
                "correct_answer": "Learning and education"
            },
            {
                "question": "What would be the best way to use this material?",
                "options": ["For studying and review", "For entertainment", "For reference only", "For criticism"],
                "correct_answer": "For studying and review"
            }
        ]
        
        short_templates = [
            {
                "question": "What is the main topic discussed in this material?",
                "sample_answer": "Based on the provided content, identify the primary subject matter and key themes.",
                "explanation": "Look for recurring themes and central ideas in the text."
            },
            {
                "question": "Summarize the key points covered in this material.",
                "sample_answer": "Provide a brief overview of the main concepts and important information presented.",
                "explanation": "Focus on the most important ideas and concepts."
            },
            {
                "question": "What are the main learning objectives of this material?",
                "sample_answer": "Identify what students should understand or be able to do after studying this content.",
                "explanation": "Consider the educational goals and outcomes."
            }
        ]
        
        # Create MCQ questions
        for i in range(min(num_mcq, len(mcq_templates))):
            template = mcq_templates[i % len(mcq_templates)]
            mcq_questions.append({
                "question": template["question"],
                "type": "multiple_choice",
                "options": template["options"],
                "correct_answer": template["correct_answer"],
                "explanation": f"This is a fallback question generated when AI processing is unavailable.",
                "difficulty": "easy"
            })
        
        # Create short answer questions
        for i in range(min(num_short, len(short_templates))):
            template = short_templates[i % len(short_templates)]
            short_questions.append({
                "question": template["question"],
                "type": "short_answer",
                "sample_answer": template["sample_answer"],
                "explanation": template["explanation"],
                "difficulty": "medium"
            })
        
        return mcq_questions + short_questions
    
    def _extract_fallback_concepts(self, content: str, max_concepts: int) -> List[str]:
        """Extract basic concepts when AI extraction fails."""
        # Simple keyword extraction as fallback
        words = content.lower().split()
        
        # Filter out common words and get unique terms
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
        
        concepts = []
        for word in words:
            clean_word = word.strip('.,!?;:"()[]{}').title()
            if len(clean_word) > 3 and clean_word.lower() not in common_words and clean_word not in concepts:
                concepts.append(clean_word)
        
        return concepts[:max_concepts]

    def _generate_fallback_summary(self, content: str, max_length: int) -> str:
        """Generate a simple fallback summary when AI generation fails."""
        words = content.split()
        
        if len(words) <= max_length:
            return content
        
        # Take first portion of content as summary
        summary_words = words[:max_length]
        summary = " ".join(summary_words)
        
        # Try to end at a sentence boundary
        sentences = summary.split('.')
        if len(sentences) > 1:
            summary = '. '.join(sentences[:-1]) + '.'
        
        return f"Summary: {summary}"

# Create a singleton instance
gemini_service = GeminiService()