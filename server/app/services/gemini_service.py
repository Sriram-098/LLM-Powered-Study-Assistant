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
            
            # Try different model names in order of preference
            model_names = [
                'gemini-2.5-flash-lite',      # Current stable model
                'gemini-2.5-pro',        # Pro version
                     
            ]
            
            self.model = None
            for model_name in model_names:
                try:
                    print(f"Trying to initialize model: {model_name}")
                    test_model = genai.GenerativeModel(model_name)
                    
                    # Test the model with a simple request to ensure it works
                    test_response = test_model.generate_content("Hello")
                    if test_response and hasattr(test_response, 'text'):
                        self.model = test_model
                        print(f"✓ Successfully initialized and tested Gemini model: {model_name}")
                        break
                    else:
                        print(f"⚠ Model {model_name} initialized but test failed")
                        continue
                        
                except Exception as model_error:
                    print(f"⚠ Failed to initialize {model_name}: {str(model_error)}")
                    continue
            
            if not self.model:
                print("❌ Failed to initialize any Gemini model")
                print("Listing available models for debugging:")
                self.list_available_models()
                
        except Exception as e:
            print(f"⚠ Failed to configure Gemini AI: {e}")
            self.model = None
    
    def is_configured(self) -> bool:
        """Check if Gemini AI is properly configured."""
        return self.model is not None
    
    def list_available_models(self):
        """List available Gemini models for debugging."""
        try:
            if not self.api_key:
                print("No API key configured")
                return
            
            genai.configure(api_key=self.api_key)
            models = genai.list_models()
            print("Available Gemini models:")
            for model in models:
                print(f"  - {model.name}")
                if hasattr(model, 'supported_generation_methods'):
                    print(f"    Supported methods: {model.supported_generation_methods}")
        except Exception as e:
            print(f"Error listing models: {e}")
    
    def reinitialize_model(self):
        """Reinitialize the model if there are issues."""
        print("Reinitializing Gemini model...")
        self.__init__()  # Reinitialize the service
    
    def generate_summary(self, content: str, max_length: int = 300) -> str:
        """Generate an intelligent, content-focused summary for personalized learning."""
        if not self.is_configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LLM service is not configured. Please set GEMINI_API_KEY."
            )
        
        # Process content for better analysis
        content_preview = content[:3000] if len(content) > 3000 else content
        
        try:
            prompt = f"""
You are an AI summarization assistant.
Your task is to read the following content and write a single, concise, foreword-style summary that introduces what the text is about.

INSTRUCTIONS:
- Use a conversational and engaging tone, as if introducing the reader to the topic.
- Clearly mention the main ideas, themes, and purpose of the content.
- Explain briefly why the topic is interesting or useful to learn.
- Keep the language natural, friendly, and easy to follow.
- The summary must be under 1000 words and written as ONE continuous paragraph.

STRICTLY AVOID:
- Academic, robotic, or overly formal tone.
- Repetition, filler phrases, or vague sentences.
- Long explanations, bullet points, or structured formatting.
- Meta-text like "This passage discusses..." — make it read naturally.

STYLE EXAMPLE:
"This content explores [main topic] and covers [key areas]. You'll learn about [important concepts] and understand how [connections/applications]. This material is valuable for [why it matters] and will help you [practical benefit]."

CONTENT:
{content_preview}

OUTPUT:
Write only the final summary paragraph with no titles, notes, or extra commentary.
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
            
            # If it's a model not found error, try to reinitialize
            if "not found" in str(e).lower() or "404" in str(e):
                print("Model not found error detected, trying to reinitialize...")
                try:
                    self.reinitialize_model()
                    if self.is_configured():
                        print("Retrying summary generation with reinitialized model...")
                        response = self.model.generate_content(prompt)
                        if hasattr(response, 'text') and response.text:
                            return response.text.strip()
                except Exception as retry_error:
                    print(f"Retry failed: {retry_error}")
            
            # Return fallback summary instead of raising error
            return self._generate_fallback_summary(content, max_length)
    

    
    def generate_quiz(self, content: str, num_mcq: int = 8, num_short: int = 4) -> List[Dict[str, Any]]:
        """Generate high-quality, content-specific revision quiz questions."""
        if not self.is_configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LLM service is not configured. Please set GEMINI_API_KEY."
            )
        
        # Calculate question distribution: MCQ (including T/F), Short Answer
        num_true_false = max(2, num_mcq // 3)  # About 1/3 of MCQ questions as T/F
        num_multiple_choice = num_mcq - num_true_false
        total_questions = num_multiple_choice + num_true_false + num_short
        
        # Process content to give AI the best material to work with
        # Take a larger sample but clean it up
        content_length = len(content)
        if content_length > 3000:
            # Take first 1500 and last 1500 characters to get beginning and end context
            content_preview = content[:1500] + "\n\n[...content continues...]\n\n" + content[-1500:]
        else:
            content_preview = content
        
        # Clean up the content preview
        content_preview = content_preview.replace('\n\n\n', '\n\n')  # Remove excessive line breaks
        content_preview = ' '.join(content_preview.split())  # Normalize whitespace but preserve structure
        
        # Try up to 2 times to get good content-specific questions
        for attempt in range(2):
            try:
                attempt_suffix = ""
                if attempt > 0:
                    attempt_suffix = f"""
                    
IMPORTANT: The previous attempt generated generic questions. This time, focus ONLY on the specific content provided. 
Create questions that someone could only answer if they read THIS specific material.
Use actual names, terms, concepts, and facts from the content above."""
                
                prompt = f"""
You are an intelligent quiz generation assistant. Your task is to create high-quality quiz questions based ONLY on the content provided below. 
Carefully read the text and ensure every question and answer directly references information from it — no general knowledge or assumptions.

CONTENT:
{content_preview}

TASK:
Generate exactly {total_questions} questions divided as follows:
- {num_multiple_choice} multiple choice questions (4 options each)
- {num_true_false} true/false questions
- {num_short} short answer questions

INSTRUCTIONS:
- All questions MUST be factual and directly derived from the given content.
- Avoid repeating ideas or using vague wording.
- Ensure every correct answer is explicitly supported by the text.
- Do NOT include questions about the type of document, studying methods, or unrelated topics.
- Maintain a balance of easy, medium, and hard difficulty levels.

OUTPUT STRICTLY in valid JSON format:
[
  {{
    "question": "Specific question about the content",
    "type": "multiple_choice",
    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
    "correct_answer": "Exact correct option text",
    "explanation": "Why this answer is correct, citing the text",
    "difficulty": "medium",
    "concept": "Key topic or idea from content"
  }},
  {{
    "question": "True or false question directly from the content",
    "type": "true_false",
    "options": ["True", "False"],
    "correct_answer": "True",
    "explanation": "Brief explanation referencing the text",
    "difficulty": "easy",
    "concept": "Main concept involved"
  }},
  {{
    "question": "Short answer question requiring understanding of a key concept",
    "type": "short_answer",
    "sample_answer": "Answer written based on content facts",
    "explanation": "What the learner should mention in their answer",
    "difficulty": "hard",
    "concept": "Topic the question tests"
  }}
]

RULES:
- Output only valid JSON (no extra text, no markdown).
- Every question must be traceable to the provided content.
- If the text lacks enough data, focus only on available facts and reduce difficulty accordingly.
{attempt_suffix}
"""

                
                print(f"Generating high-quality quiz with model: {self.model}")
                response = self.model.generate_content(prompt)
                
                if not response or not hasattr(response, 'text'):
                    print("No valid response from Gemini")
                    if attempt == 1:
                        return self._create_fallback_quiz(content, num_mcq, num_short)
                    continue
                
                quiz_text = response.text.strip()
                print(f"Raw quiz response length: {len(quiz_text)}")
                
                # More robust JSON extraction
                json_text = quiz_text
                
                # Remove markdown code blocks
                if "```json" in json_text:
                    json_text = json_text.split("```json")[1].split("```")[0].strip()
                elif "```" in json_text:
                    json_text = json_text.split("```")[1].split("```")[0].strip()
                
                # Remove any leading/trailing text that's not JSON
                json_start = json_text.find('[')
                json_end = json_text.rfind(']')
                
                if json_start != -1 and json_end != -1 and json_end > json_start:
                    json_text = json_text[json_start:json_end + 1]
                
                # Clean up common JSON issues
                json_text = json_text.replace('\n', ' ').replace('\r', ' ')
                json_text = ' '.join(json_text.split())  # Normalize whitespace
                
                try:
                    quiz_questions = json.loads(json_text)
                    
                    # Validate the structure
                    if not isinstance(quiz_questions, list):
                        print(f"Response is not a list: {type(quiz_questions)}")
                        if attempt == 1:
                            return self._create_fallback_quiz(content, num_mcq, num_short)
                        continue
                    
                    if len(quiz_questions) == 0:
                        print("Empty questions list received")
                        if attempt == 1:
                            return self._create_fallback_quiz(content, num_mcq, num_short)
                        continue
                    
                    # Validate each question and check for content specificity
                    valid_questions = []
                    generic_indicators = [
                        'type of document', 'study material', 'educational purposes', 'best way to',
                        'primary purpose', 'main topic', 'document is', 'material contains',
                        'content is', 'information is', 'text is', 'suitable for', 'designed for',
                        'would be best', 'most likely', 'general information', 'basic information'
                    ]
                    
                    for i, q in enumerate(quiz_questions):
                        if not isinstance(q, dict):
                            print(f"Question {i} is not a dict: {type(q)}")
                            continue
                        
                        required_fields = ["question", "type", "correct_answer", "explanation"]
                        if not all(field in q for field in required_fields):
                            print(f"Question {i} missing required fields: {q.keys()}")
                            continue
                        
                        # Validate question types
                        if q["type"] not in ["multiple_choice", "true_false", "short_answer"]:
                            print(f"Question {i} has invalid type: {q['type']}")
                            continue
                        
                        # Validate options for multiple choice and true/false
                        if q["type"] in ["multiple_choice", "true_false"] and "options" not in q:
                            print(f"Question {i} missing options for {q['type']}")
                            continue
                        
                        # Check if question is too generic
                        question_text = q["question"].lower()
                        is_generic = any(indicator in question_text for indicator in generic_indicators)
                        
                        if is_generic:
                            print(f"Question {i} appears to be generic: {q['question'][:50]}...")
                            continue
                        
                        # Check if multiple choice options are too generic
                        if q["type"] == "multiple_choice" and "options" in q:
                            generic_options = [
                                'educational content', 'study notes', 'technical manual', 
                                'learning and education', 'for studying', 'general information',
                                'research material', 'technical documentation'
                            ]
                            options_text = ' '.join(q["options"]).lower()
                            if any(generic_opt in options_text for generic_opt in generic_options):
                                print(f"Question {i} has generic options: {q['options']}")
                                continue
                        
                        valid_questions.append(q)
                    
                    if len(valid_questions) >= total_questions // 2:  # At least half the questions are valid
                        print(f"Successfully generated {len(valid_questions)} valid questions on attempt {attempt + 1}")
                        return valid_questions
                    else:
                        print(f"Attempt {attempt + 1}: Too few valid questions: {len(valid_questions)} out of {total_questions}")
                        if attempt == 1:  # Last attempt
                            return self._create_fallback_quiz(content, num_mcq, num_short)
                        # Continue to next attempt
                
                except json.JSONDecodeError as e:
                    print(f"Attempt {attempt + 1}: JSON parsing error: {e}")
                    print(f"Cleaned JSON text: {json_text[:500]}...")
                    if attempt == 1:  # Last attempt
                        return self._create_fallback_quiz(content, num_mcq, num_short)
                    # Continue to next attempt
                
            except Exception as e:
                print(f"Attempt {attempt + 1}: Error during quiz generation: {e}")
                if attempt == 1:  # Last attempt
                    return self._create_fallback_quiz(content, num_mcq, num_short)
                # Continue to next attempt
        
        # If we get here, all attempts failed
        print("All attempts failed, using fallback quiz")
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
You are an AI assistant that extracts and explains key concepts from text.

TASK:
- Identify the {max_concepts} most relevant and meaningful key concepts or terms.
- For each concept, provide a short, clear one-line explanation.
- Present them in a clean HTML-ready format, where:
  • The concept name appears as a heading (<h3> with black color).
  • The explanation appears as a short descriptive line (<p>) below it.
- Avoid generic or unrelated words like "introduction", "summary", "education", etc.
- Use simple, natural language that anyone can understand.
- Do NOT include JSON, lists, or any extra text outside the concept–explanation pairs.

EXAMPLE STYLE:
<h3 style="color:black;">Extractive Summarization</h3>
<p>A method that selects and combines key sentences directly from the original document.</p>

TEXT CONTENT:
{content}

OUTPUT:
Write only the formatted concept headings and their one-line explanations in the above HTML pattern.
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
    
    def _create_fallback_quiz(self, content: str, num_mcq: int = 8, num_short: int = 4) -> List[Dict[str, Any]]:
        """Create a content-aware fallback quiz when AI generation fails."""
        questions = []
        
        # Calculate question distribution
        num_true_false = max(2, num_mcq // 3)
        num_multiple_choice = num_mcq - num_true_false
        
        # Try to extract some basic information from content for better questions
        content_words = content.lower().split()
        content_sentences = content.split('.')[:10]  # First 10 sentences
        
        # Extract potential key terms (words longer than 4 characters, not common words)
        common_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did', 'man', 'way', 'she', 'use', 'your', 'said', 'each', 'make', 'most', 'over', 'such', 'time', 'very', 'what', 'with', 'have', 'from', 'they', 'know', 'want', 'been', 'good', 'much', 'some', 'well', 'were', 'this', 'that', 'will', 'would', 'there', 'their', 'could', 'should', 'about', 'after', 'first', 'never', 'these', 'think', 'where', 'being', 'every', 'great', 'might', 'shall', 'still', 'those', 'under', 'while', 'before', 'through', 'between', 'important', 'example', 'because', 'however', 'therefore', 'although', 'including', 'according', 'different', 'following', 'information'}
        
        key_terms = []
        for word in content_words:
            clean_word = word.strip('.,!?;:"()[]{}').title()
            if len(clean_word) > 4 and clean_word.lower() not in common_words and clean_word not in key_terms:
                key_terms.append(clean_word)
        
        key_terms = key_terms[:20]  # Limit to top 20 terms
        
        # Content-aware multiple choice templates
        mcq_templates = []
        
        # Add content-specific questions if we have key terms
        if key_terms:
            mcq_templates.extend([
                {
                    "question": f"Which of the following terms is most relevant to the main concepts discussed in this material?",
                    "options": [key_terms[0] if len(key_terms) > 0 else "Main concept", 
                              "Unrelated term", "Generic concept", "Random topic"],
                    "correct_answer": key_terms[0] if len(key_terms) > 0 else "Main concept",
                    "concept": "Key term identification"
                },
                {
                    "question": f"Based on the content, which concept is most emphasized?",
                    "options": [key_terms[1] if len(key_terms) > 1 else "Primary concept",
                              key_terms[2] if len(key_terms) > 2 else "Secondary concept", 
                              "Unrelated concept", "Minor detail"],
                    "correct_answer": key_terms[1] if len(key_terms) > 1 else "Primary concept",
                    "concept": "Concept emphasis"
                }
            ])
        
        # Add general but improved templates
        mcq_templates.extend([
            {
                "question": "What is the primary focus of this study material?",
                "options": ["The main concepts and ideas presented", "Unrelated topics", "General knowledge", "Basic information"],
                "correct_answer": "The main concepts and ideas presented",
                "concept": "Content focus"
            },
            {
                "question": "How would you best describe the level of detail in this material?",
                "options": ["Comprehensive and detailed", "Very basic", "Extremely complex", "Incomplete"],
                "correct_answer": "Comprehensive and detailed",
                "concept": "Content depth"
            },
            {
                "question": "What type of learning approach would work best with this material?",
                "options": ["Active study and review", "Passive reading only", "Memorization without understanding", "Casual browsing"],
                "correct_answer": "Active study and review",
                "concept": "Learning strategy"
            }
        ])
        
        # Content-aware True/False templates
        tf_templates = []
        
        # Add content-specific true/false questions
        if len(content_sentences) > 2:
            tf_templates.extend([
                {
                    "question": f"The material discusses concepts that require careful study and understanding.",
                    "correct_answer": "True",
                    "explanation": f"Based on the content structure and depth, this material contains concepts that benefit from thorough study.",
                    "concept": "Study requirements"
                },
                {
                    "question": f"This material covers only surface-level information without depth.",
                    "correct_answer": "False",
                    "explanation": f"The content demonstrates depth and complexity that goes beyond surface-level treatment.",
                    "concept": "Content depth"
                }
            ])
        
        # Add improved general templates
        tf_templates.extend([
            {
                "question": "This material is structured to facilitate learning and comprehension.",
                "correct_answer": "True",
                "explanation": "The organization and presentation of the content supports effective learning.",
                "concept": "Learning structure"
            },
            {
                "question": "The content can be fully understood without any active engagement.",
                "correct_answer": "False",
                "explanation": "Effective learning from this material requires active reading and engagement with the concepts.",
                "concept": "Active learning"
            },
            {
                "question": "This material would benefit from review and practice to master the concepts.",
                "correct_answer": "True",
                "explanation": "Complex educational content typically requires multiple exposures and practice for mastery.",
                "concept": "Mastery requirements"
            }
        ])
        
        # Content-aware short answer templates
        short_templates = []
        
        # Add content-specific short answer questions
        if key_terms:
            short_templates.extend([
                {
                    "question": f"Explain the significance of the key concepts presented in this material and how they relate to each other.",
                    "sample_answer": f"The material presents several important concepts including {', '.join(key_terms[:3])}. These concepts are interconnected and build upon each other to create a comprehensive understanding of the subject matter.",
                    "explanation": "Students should identify the main concepts and explain their relationships and importance.",
                    "concept": "Concept relationships"
                },
                {
                    "question": f"Describe how you would use the information in this material to solve a related problem or answer questions in this field.",
                    "sample_answer": f"The material provides foundational knowledge about {key_terms[0] if key_terms else 'the main topic'} that can be applied by analyzing the key principles and applying them systematically to new situations.",
                    "explanation": "Students should demonstrate understanding by showing how to apply the concepts practically.",
                    "concept": "Practical application"
                }
            ])
        
        # Add improved general templates
        short_templates.extend([
            {
                "question": "What are the most important takeaways from this material, and why are they significant?",
                "sample_answer": "The most important takeaways include the core concepts, their practical implications, and how they contribute to understanding the broader subject area. These are significant because they form the foundation for further learning and application.",
                "explanation": "Students should identify key concepts and explain their importance and relevance.",
                "concept": "Key takeaways"
            },
            {
                "question": "How would you explain the main ideas in this material to someone unfamiliar with the topic?",
                "sample_answer": "I would start with the basic concepts, provide clear definitions, use examples to illustrate key points, and show how the ideas connect to create a complete understanding of the subject.",
                "explanation": "Students should demonstrate understanding by being able to teach or explain the concepts clearly.",
                "concept": "Concept explanation"
            },
            {
                "question": "What questions would you ask to test someone's understanding of this material?",
                "sample_answer": "I would ask about the main concepts, their relationships, practical applications, and how they fit into the broader context of the subject area.",
                "explanation": "Students should understand the material well enough to identify what aspects are most important to test.",
                "concept": "Assessment understanding"
            }
        ])
        
        # Create multiple choice questions
        for i in range(min(num_multiple_choice, len(mcq_templates))):
            template = mcq_templates[i % len(mcq_templates)]
            questions.append({
                "question": template["question"],
                "type": "multiple_choice",
                "options": template["options"],
                "correct_answer": template["correct_answer"],
                "explanation": "This is a fallback question generated when AI processing is unavailable.",
                "difficulty": "easy",
                "concept": template["concept"]
            })
        
        # Create true/false questions
        for i in range(min(num_true_false, len(tf_templates))):
            template = tf_templates[i % len(tf_templates)]
            questions.append({
                "question": template["question"],
                "type": "true_false",
                "options": ["True", "False"],
                "correct_answer": template["correct_answer"],
                "explanation": template["explanation"],
                "difficulty": "easy",
                "concept": template["concept"]
            })
        
        # Create short answer questions
        for i in range(min(num_short, len(short_templates))):
            template = short_templates[i % len(short_templates)]
            questions.append({
                "question": template["question"],
                "type": "short_answer",
                "sample_answer": template["sample_answer"],
                "explanation": template["explanation"],
                "difficulty": "medium",
                "concept": template["concept"]
            })
        
        return questions
    
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
        """Generate a concise, foreword-style fallback summary."""
        words = content.split()
        sentences = content.split('.')
        
        # Get the opening content
        first_sentence = sentences[0].strip() if sentences else ""
        
        # Extract key terms
        meaningful_words = []
        common_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'this', 'that', 'with', 'have', 'from', 'they', 'been', 'said', 'each', 'make', 'most', 'over', 'such', 'time', 'very', 'what', 'will', 'would', 'there', 'could', 'should'}
        
        for word in words:
            clean_word = word.strip('.,!?;:"()[]{}').title()
            if len(clean_word) > 4 and clean_word.lower() not in common_words:
                meaningful_words.append(clean_word)
        
        key_terms = list(set(meaningful_words))[:3]  # Just top 3 terms
        
        # Create simple foreword-style summary
        summary_parts = []
        
        if first_sentence:
            summary_parts.append(first_sentence + ".")
        
        if key_terms:
            summary_parts.append(f"\nThis material covers {', '.join(key_terms[:-1])} and {key_terms[-1]}." if len(key_terms) > 1 else f"\nThis material focuses on {key_terms[0]}.")
        
        # Add a simple learning note
        if len(sentences) > 2:
            summary_parts.append("\nThis content will help you understand the key concepts and their practical applications.")
        
        return "\n".join(summary_parts)
    


# Create a singleton instance
gemini_service = GeminiService()