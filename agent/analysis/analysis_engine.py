"""
Analysis Engine for Sentiment, Emotion, Aspect, Comparison, and Summary
Uses Hugging Face Inference API (free tier) for text generation
"""

import os
import json
import logging
import re
from typing import Dict, Any, Optional, List
import requests

logger = logging.getLogger(__name__)

# Try to import transformers for local models
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("transformers not available - will use API or fallback")


class AnalysisEngine:
    """Core analysis engine using Hugging Face for various sentiment analysis tasks"""
    
    def __init__(self, config: Dict):
        """
        Initialize analysis engine
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        hf_config = config.get("huggingface", {})
        self.api_token = os.getenv("HUGGINGFACE_API_TOKEN", hf_config.get("api_token", ""))
        self.model_name = hf_config.get("model", "mistralai/Mistral-7B-Instruct-v0.2")
        self.temperature = hf_config.get("temperature", 0.7)
        self.max_tokens = hf_config.get("max_tokens", 2000)
        self.use_api = hf_config.get("use_api", True)
        
        # Initialize local models for sentiment/emotion analysis
        self.sentiment_pipeline = None
        self.emotion_pipeline = None
        self.use_local_models = hf_config.get("use_local_models", True)
        
        if TRANSFORMERS_AVAILABLE and self.use_local_models:
            logger.info("Initializing local transformer models for better analysis quality...")
            self._init_local_models()
        else:
            logger.info("Using API-based analysis (local models disabled or transformers not available)")
    
    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call LLM via Hugging Face Inference API or local model
        
        Args:
            system_prompt: System instruction
            user_prompt: User query
            
        Returns:
            Generated text response
        """
        # Skip API calls if no token (fail fast to keyword fallback)
        if self.use_api and self.api_token:
            try:
                return self._call_hf_api(system_prompt, user_prompt)
            except Exception as e:
                logger.warning(f"API call failed: {e}, skipping to fallback")
                raise  # Re-raise to trigger fallback
        else:
            # No API token or API disabled - skip to fallback immediately
            raise ValueError("API not available, using fallback")
    
    def _call_hf_api(self, system_prompt: str, user_prompt: str) -> str:
        """Call Hugging Face Inference API"""
        try:
            # Format prompt for instruction-tuned models
            formatted_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            headers = {
                "Content-Type": "application/json"
            }
            
            # Add authorization if token is provided
            if self.api_token:
                headers["Authorization"] = f"Bearer {self.api_token}"
            
            payload = {
                "inputs": formatted_prompt,
                "parameters": {
                    "temperature": self.temperature,
                    "max_new_tokens": self.max_tokens,
                    "return_full_text": False
                }
            }
            
            # Use Hugging Face Router API (new endpoint)
            api_url = f"https://router.huggingface.co/models/{self.model_name}"
            # Reduced timeout for faster failure, will fallback quickly
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                # Handle different response formats
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get("generated_text", "")
                elif isinstance(result, dict):
                    generated_text = result.get("generated_text", "")
                else:
                    generated_text = str(result)
                
                return generated_text.strip()
            elif response.status_code == 503:
                # Model is loading, wait and retry
                logger.warning("Model is loading, using fallback")
                return self._call_local_model(system_prompt, user_prompt)
            else:
                logger.error(f"HF API error: {response.status_code} - {response.text}")
                # Fallback to local model
                return self._call_local_model(system_prompt, user_prompt)
                
        except Exception as e:
            logger.error(f"Error calling Hugging Face API: {e}, using fallback")
            return self._call_local_model(system_prompt, user_prompt)
    
    def _init_local_models(self):
        """Initialize local transformer models for sentiment and emotion analysis"""
        try:
            if not TRANSFORMERS_AVAILABLE:
                logger.warning("transformers library not available - skipping local models")
                return
            
            logger.info("Loading sentiment analysis model: distilbert-base-uncased-finetuned-sst-2-english")
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=-1  # Use CPU (-1) or GPU (0, 1, etc.)
            )
            logger.info("Sentiment model loaded")
            
            try:
                logger.info("Loading emotion analysis model: j-hartmann/emotion-english-distilroberta-base")
                self.emotion_pipeline = pipeline(
                    "text-classification",
                    model="j-hartmann/emotion-english-distilroberta-base",
                    device=-1
                )
                logger.info("Emotion model loaded")
            except Exception as e:
                logger.warning(f"Could not load emotion model: {e} - will use sentiment model for emotions")
                self.emotion_pipeline = None
                
        except Exception as e:
            logger.error(f"Error initializing local models: {e}")
            logger.warning("Will fall back to API or keyword-based analysis")
            self.sentiment_pipeline = None
            self.emotion_pipeline = None
    
    def _call_local_model(self, system_prompt: str, user_prompt: str) -> str:
        """Fallback: Use Hugging Face public API without auth (slower but free)"""
        try:
            # Try using a public model that doesn't require auth
            public_model = "mistralai/Mistral-7B-Instruct-v0.2"
            formatted_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            headers = {"Content-Type": "application/json"}
            payload = {
                "inputs": formatted_prompt,
                "parameters": {
                    "temperature": self.temperature,
                    "max_new_tokens": min(self.max_tokens, 500),  # Limit for free tier
                    "return_full_text": False
                }
            }
            
            api_url = f"https://router.huggingface.co/models/{public_model}"
            # Reduced timeout for faster failure, will fallback quickly
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "").strip()
                elif isinstance(result, dict):
                    return result.get("generated_text", "").strip()
                return str(result).strip()
            else:
                logger.warning(f"Public API also failed: {response.status_code}")
                # Return a basic JSON structure as last resort
                return self._generate_fallback_response(user_prompt)
                
        except Exception as e:
            logger.error(f"Fallback API error: {e}")
            return self._generate_fallback_response(user_prompt)
    
    def _generate_fallback_response(self, prompt: str) -> str:
        """Generate a basic fallback JSON response using local models if available"""
        # Try to use local sentiment model even in fallback
        if self.sentiment_pipeline:
            try:
                result = self.sentiment_pipeline(prompt)[0]
                label = result["label"].lower()
                score_raw = result["score"]
                
                if "positive" in label:
                    sentiment = "positive"
                    score = score_raw
                elif "negative" in label:
                    sentiment = "negative"
                    score = -score_raw
                else:
                    sentiment = "neutral"
                    score = 0.0
                
                return json.dumps({
                    "sentiment": sentiment,
                    "score": score,
                    "reasoning": f"Local model analysis (confidence: {score_raw:.2f})"
                })
            except:
                pass
        
        # Last resort: Simple keyword-based sentiment
        return self._keyword_sentiment_fallback(prompt)
    
    def _keyword_sentiment_fallback(self, text: str) -> Dict[str, Any]:
        """Fast keyword-based sentiment analysis (no API, no models)"""
        text_lower = text.lower()
        positive_words = ["good", "great", "excellent", "love", "amazing", "wonderful", "happy", "satisfied", "perfect", "awesome", "fantastic", "brilliant", "outstanding"]
        negative_words = ["bad", "terrible", "awful", "hate", "disappointed", "angry", "sad", "poor", "worst", "horrible", "disgusting", "frustrated", "annoyed"]
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            sentiment = "positive"
            score = min(0.6 + (pos_count * 0.1), 1.0)
        elif neg_count > pos_count:
            sentiment = "negative"
            score = max(-0.6 - (neg_count * 0.1), -1.0)
        else:
            sentiment = "neutral"
            score = 0.0
        
        return {
            "sentiment": sentiment,
            "score": score,
            "reasoning": "Keyword-based fallback analysis"
        }
    
    def _keyword_emotion_fallback(self, text: str) -> Dict[str, Any]:
        """Fast keyword-based emotion analysis (no API, no models)"""
        text_lower = text.lower()
        
        # Simple emotion detection based on keywords
        joy_words = ["happy", "joy", "excited", "love", "amazing", "wonderful", "great", "excellent"]
        anger_words = ["angry", "mad", "furious", "annoyed", "frustrated", "hate"]
        sadness_words = ["sad", "disappointed", "unhappy", "depressed", "upset"]
        fear_words = ["worried", "afraid", "scared", "anxious", "nervous"]
        
        joy_count = sum(1 for word in joy_words if word in text_lower)
        anger_count = sum(1 for word in anger_words if word in text_lower)
        sadness_count = sum(1 for word in sadness_words if word in text_lower)
        fear_count = sum(1 for word in fear_words if word in text_lower)
        
        # Find dominant emotion
        emotions = {
            "joy": joy_count,
            "anger": anger_count,
            "sadness": sadness_count,
            "fear": fear_count
        }
        
        max_emotion = max(emotions.items(), key=lambda x: x[1])
        
        if max_emotion[1] > 0:
            primary_emotion = max_emotion[0]
            intensity = min(max_emotion[1] * 0.3, 1.0)
        else:
            primary_emotion = "neutral"
            intensity = 0.5
        
        return {
            "primary_emotion": primary_emotion,
            "emotions": {primary_emotion: intensity},
            "intensity": intensity
        }
    
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON from LLM response"""
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                # Try parsing the whole text
                return json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}, text: {text[:200]}")
            return {}
    
    def analyze(self, text: str, input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform comprehensive analysis on input text with NEW format output ONLY
        
        Args:
            text: Input text to analyze
            input_data: Additional input data (user, platform, country, etc.)
            
        Returns:
            Dictionary with analysis results in NEW format (no old fields)
        """
        input_data = input_data or {}
        logger.info(f"Analyzing text: {text[:100]}...")
        
        # Perform core analyses (only what we need for new format)
        # Wrap each in try-except to prevent hanging
        try:
            sentiment = self._detect_sentiment(text)
        except Exception as e:
            logger.error(f"Sentiment detection failed: {e}, using fallback")
            sentiment = {"sentiment": "neutral", "score": 0.0}
        
        try:
            emotion = self._analyze_emotion(text)
        except Exception as e:
            logger.error(f"Emotion analysis failed: {e}, using fallback")
            emotion = {"primary_emotion": "neutral", "emotions": {}, "intensity": 0.0}
        
        # Extract topics from text and hashtags (fast, no API)
        try:
            topics = self._extract_topics(text, input_data)
        except Exception as e:
            logger.error(f"Topic extraction failed: {e}, using fallback")
            topics = []
        
        # Predict engagement (fast, no API)
        try:
            engagement = self._predict_engagement(text, input_data)
        except Exception as e:
            logger.error(f"Engagement prediction failed: {e}, using fallback")
            engagement = "medium"
        
        # Generate recommendation (fast, keyword-based)
        try:
            recommendation = self._generate_recommendation(text, sentiment, emotion, topics, input_data)
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}, using fallback")
            recommendation = "Continue monitoring sentiment and engagement."
        
        # Extract sentiment label and score
        sentiment_label = self._map_sentiment_to_label(sentiment, emotion)
        sentiment_score = sentiment.get("score", 0.0)
        
        # Format emotion analysis as array
        emotion_analysis = self._format_emotion_analysis(emotion)
        
        # Get region from input data (check multiple sources)
        region = (
            input_data.get("country") or 
            input_data.get("region") or 
            (input_data.get("context", {}).get("country") if isinstance(input_data.get("context"), dict) else None) or
            (input_data.get("meta", {}).get("country") if isinstance(input_data.get("meta"), dict) else None)
        )
        
        # Build response in NEW format ONLY (no old fields)
        response = {
            "sentiment_label": sentiment_label,
            "sentiment_score": round(sentiment_score, 2),
            "emotion_analysis": emotion_analysis,
            "engagement_prediction": engagement,
            "topic_extracted": topics,
            "region": region,  # Will be fixed in API layer if still null
            "recommendation": recommendation
        }
        
        return response
    
    def _detect_sentiment(self, text: str) -> Dict[str, Any]:
        """Detect overall sentiment using local model or API"""
        # Try local transformer model first (best quality, no API needed)
        if self.sentiment_pipeline:
            try:
                result = self.sentiment_pipeline(text)[0]
                label = result["label"].lower()
                score_raw = result["score"]
                
                # Convert to our format
                if "positive" in label:
                    sentiment = "positive"
                    score = score_raw
                elif "negative" in label:
                    sentiment = "negative"
                    score = -score_raw
                else:
                    sentiment = "neutral"
                    score = 0.0
                
                return {
                    "sentiment": sentiment,
                    "score": score,
                    "reasoning": f"Analyzed using local DistilBERT model (confidence: {score_raw:.2f})"
                }
            except Exception as e:
                logger.warning(f"Local sentiment model failed: {e}, trying API")
        
        # Fallback to API or LLM
        system_prompt = "You are a sentiment analysis expert. Always respond with valid JSON only."
        user_prompt = f"""Analyze the sentiment of the following text and provide a JSON response with:
- sentiment: "positive", "negative", or "neutral"
- score: a float between -1.0 (very negative) and 1.0 (very positive)
- reasoning: brief explanation

Text: {text}

Respond with ONLY valid JSON, no additional text."""
        
        try:
            # Add timeout protection - fail fast if API hangs
            response_text = self._call_llm(system_prompt, user_prompt)
            result = self._extract_json(response_text)
            
            # Validate result structure
            if not result or "sentiment" not in result:
                raise ValueError("Invalid response format")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in sentiment detection: {e}, using keyword fallback")
            # Fast keyword-based fallback
            return self._keyword_sentiment_fallback(text)
    
    def _analyze_emotion(self, text: str) -> Dict[str, Any]:
        """Analyze emotions in text using local model or API"""
        # Try local transformer model first (best quality, no API needed)
        if self.emotion_pipeline:
            try:
                result = self.emotion_pipeline(text)[0]
                primary_emotion = result["label"].lower()
                confidence = result["score"]
                
                # Map to standard emotion names
                emotion_map = {
                    "joy": ["joy", "happiness", "happy"],
                    "anger": ["anger", "angry", "annoyed"],
                    "sadness": ["sadness", "sad", "disappointment"],
                    "fear": ["fear", "anxiety", "worried"],
                    "surprise": ["surprise", "surprised"],
                    "disgust": ["disgust", "disgusted"],
                    "neutral": ["neutral", "calm"]
                }
                
                # Find matching emotion
                mapped_emotion = "neutral"
                for std_emotion, variants in emotion_map.items():
                    if any(v in primary_emotion for v in variants):
                        mapped_emotion = std_emotion
                        break
                
                emotions = {mapped_emotion: confidence}
                intensity = confidence
                
                return {
                    "primary_emotion": mapped_emotion,
                    "emotions": emotions,
                    "intensity": intensity
                }
            except Exception as e:
                logger.warning(f"Local emotion model failed: {e}, trying API")
        
        # Fallback to API or LLM
        system_prompt = "You are an emotion analysis expert. Always respond with valid JSON only."
        user_prompt = f"""Analyze the emotions expressed in the following text. Provide a JSON response with:
- primary_emotion: the dominant emotion (e.g., "joy", "anger", "sadness", "fear", "surprise", "disgust", "neutral")
- emotions: an object with emotion names as keys and confidence scores (0-1) as values
- intensity: overall emotional intensity (0-1)

Text: {text}

Respond with ONLY valid JSON, no additional text."""
        
        try:
            response_text = self._call_llm(system_prompt, user_prompt)
            result = self._extract_json(response_text)
            
            if not result or "primary_emotion" not in result:
                raise ValueError("Invalid response format")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in emotion analysis: {e}, using fallback")
            # Fast keyword-based emotion fallback
            return self._keyword_emotion_fallback(text)
    
    def _aspect_based_sentiment(self, text: str) -> Dict[str, Any]:
        """Perform aspect-based sentiment analysis"""
        system_prompt = "You are an aspect-based sentiment analysis expert. Always respond with valid JSON only."
        user_prompt = f"""Perform aspect-based sentiment analysis on the following text. Identify different aspects/topics mentioned and their individual sentiments. Provide a JSON response with:
- aspects: an array of objects, each with:
  - aspect: the aspect/topic name
  - sentiment: "positive", "negative", or "neutral"
  - score: sentiment score (-1.0 to 1.0)
  - mention: relevant text snippet

Text: {text}

Respond with ONLY valid JSON, no additional text."""
        
        try:
            response_text = self._call_llm(system_prompt, user_prompt)
            result = self._extract_json(response_text)
            
            if not result or "aspects" not in result:
                raise ValueError("Invalid response format")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in aspect-based sentiment: {e}")
            return {
                "aspects": []
            }
    
    def _comparison_analysis(self, text: str) -> Dict[str, Any]:
        """Perform comparison analysis if multiple entities are mentioned"""
        system_prompt = "You are a comparison analysis expert. Always respond with valid JSON only."
        user_prompt = f"""Analyze the following text for comparisons between entities, products, services, or concepts. Provide a JSON response with:
- has_comparison: boolean indicating if comparison exists
- entities: array of entities being compared
- comparison_points: array of comparison aspects
- winner: which entity is favored (if applicable), or null

Text: {text}

Respond with ONLY valid JSON, no additional text."""
        
        try:
            response_text = self._call_llm(system_prompt, user_prompt)
            result = self._extract_json(response_text)
            
            if not result or "has_comparison" not in result:
                raise ValueError("Invalid response format")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in comparison analysis: {e}")
            return {
                "has_comparison": False,
                "entities": [],
                "comparison_points": [],
                "winner": None
            }
    
    def _generate_summary(self, text: str) -> Dict[str, Any]:
        """Generate feedback summary"""
        system_prompt = "You are a feedback summarization expert. Always respond with valid JSON only."
        user_prompt = f"""Generate a comprehensive feedback summary for the following text. Provide a JSON response with:
- summary: a concise summary of the main points
- key_points: array of key points mentioned
- recommendations: array of any recommendations or suggestions (if any)
- overall_tone: overall tone of the feedback

Text: {text}

Respond with ONLY valid JSON, no additional text."""
        
        try:
            response_text = self._call_llm(system_prompt, user_prompt)
            result = self._extract_json(response_text)
            
            if not result or "summary" not in result:
                raise ValueError("Invalid response format")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in summary generation: {e}")
            return {
                "summary": "",
                "key_points": [],
                "recommendations": [],
                "overall_tone": "neutral"
            }
    
    def _calculate_confidence(self, sentiment: Dict, emotion: Dict, aspects: Dict) -> float:
        """Calculate overall confidence score"""
        try:
            # Simple confidence calculation based on consistency
            scores = []
            
            if "score" in sentiment:
                scores.append(abs(sentiment["score"]))
            
            if "intensity" in emotion:
                scores.append(emotion["intensity"])
            
            if "aspects" in aspects and len(aspects.get("aspects", [])) > 0:
                # Average aspect confidence
                aspect_scores = [abs(a.get("score", 0)) for a in aspects["aspects"]]
                if aspect_scores:
                    scores.append(sum(aspect_scores) / len(aspect_scores))
            
            return sum(scores) / len(scores) if scores else 0.5
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5
    
    def _map_sentiment_to_label(self, sentiment: Dict, emotion: Dict) -> str:
        """Map sentiment and emotion to sentiment label (admiration, disappointment, etc.)"""
        try:
            sentiment_val = sentiment.get("sentiment", "neutral").lower()
            emotion_val = emotion.get("primary_emotion", "neutral").lower()
            score = sentiment.get("score", 0.0)
            
            # Map to sentiment labels based on sentiment + emotion
            if sentiment_val == "positive":
                if emotion_val in ["joy", "happiness"]:
                    return "admiration" if score > 0.7 else "satisfaction"
                elif emotion_val == "surprise":
                    return "excitement"
                else:
                    return "satisfaction"
            elif sentiment_val == "negative":
                if emotion_val in ["anger", "disgust"]:
                    return "anger"
                elif emotion_val == "sadness":
                    return "disappointment"
                elif emotion_val == "fear":
                    return "concern"
                else:
                    return "disappointment"
            else:
                return "neutral"
        except Exception as e:
            logger.error(f"Error mapping sentiment label: {e}")
            return "neutral"
    
    def _format_emotion_analysis(self, emotion: Dict) -> List[Dict[str, Any]]:
        """Format emotion analysis as array of {emotion, score} objects"""
        try:
            emotion_list = []
            
            # Add primary emotion
            primary = emotion.get("primary_emotion", "neutral")
            emotions_dict = emotion.get("emotions", {})
            
            if emotions_dict:
                # Use emotions dict if available
                for emo, score in emotions_dict.items():
                    emotion_list.append({
                        "emotion": emo,
                        "score": round(float(score), 2)
                    })
            else:
                # Fallback to primary emotion with intensity
                intensity = emotion.get("intensity", 0.5)
                emotion_list.append({
                    "emotion": primary,
                    "score": round(float(intensity), 2)
                })
            
            # Sort by score descending
            emotion_list.sort(key=lambda x: x["score"], reverse=True)
            
            return emotion_list[:5]  # Return top 5 emotions
            
        except Exception as e:
            logger.error(f"Error formatting emotion analysis: {e}")
            return [{"emotion": "neutral", "score": 0.5}]
    
    def _extract_topics(self, text: str, input_data: Dict) -> List[str]:
        """Extract topics from text and hashtags"""
        try:
            topics = []
            
            # Extract from hashtags if available
            hashtags = input_data.get("hashtags", [])
            if hashtags:
                topics.extend([h.replace("#", "").lower() for h in hashtags])
            
            # Skip aspect-based analysis (too slow, uses API)
            # Instead, extract simple keywords from text
            # aspects_result = self._aspect_based_sentiment(text)  # Disabled - too slow
            
            # Extract keywords from text (simple extraction)
            text_lower = text.lower()
            common_topics = ["product", "service", "customer", "support", "order", "delivery", 
                           "quality", "price", "innovation", "launch", "feature"]
            for topic in common_topics:
                if topic in text_lower and topic not in topics:
                    topics.append(topic)
            
            return topics[:5]  # Return top 5 topics
            
        except Exception as e:
            logger.error(f"Error extracting topics: {e}")
            return []
    
    def _predict_engagement(self, text: str, input_data: Dict) -> str:
        """Predict engagement level based on text, likes, retweets, sentiment"""
        try:
            sentiment_score = 0.0
            try:
                sentiment = self._detect_sentiment(text)
                sentiment_score = sentiment.get("score", 0.0)
            except:
                pass
            
            # Use existing engagement metrics if available
            likes = input_data.get("likes", 0) or 0
            retweets = input_data.get("retweets", 0) or 0
            total_engagement = likes + (retweets * 2)  # Retweets weighted more
            
            # Predict based on sentiment and engagement metrics
            if total_engagement > 500 or sentiment_score > 0.8:
                return "high"
            elif total_engagement > 100 or sentiment_score > 0.3:
                return "medium"
            elif sentiment_score < -0.5:
                return "low"
            else:
                return "medium"
                
        except Exception as e:
            logger.error(f"Error predicting engagement: {e}")
            return "medium"
    
    def _generate_recommendation(self, text: str, sentiment: Dict, emotion: Dict, 
                                topics: List[str], input_data: Dict) -> str:
        """Generate actionable recommendation based on analysis"""
        try:
            sentiment_score = sentiment.get("score", 0.0)
            sentiment_val = sentiment.get("sentiment", "neutral")
            region = input_data.get("country") or input_data.get("region", "")
            platform = input_data.get("platform", "")
            
            recommendations = []
            
            # Region-based recommendation
            if region:
                if sentiment_score > 0.7:
                    recommendations.append(f"Promote this content in {region} region")
                elif sentiment_score < -0.5:
                    recommendations.append(f"Review customer service in {region} region")
            
            # Topic-based recommendations
            if "innovation" in topics or "launch" in topics:
                if sentiment_score > 0.6:
                    recommendations.append("users respond positively to innovation themes")
            
            if "product" in topics or "quality" in topics:
                if sentiment_score > 0.5:
                    recommendations.append("highlight product quality in marketing")
                else:
                    recommendations.append("address product quality concerns")
            
            # Sentiment-based recommendations
            if sentiment_val == "positive" and sentiment_score > 0.8:
                recommendations.append("consider using as testimonial or case study")
            elif sentiment_val == "negative" and sentiment_score < -0.7:
                recommendations.append("escalate to customer support team immediately")
            
            # Platform-specific
            if platform:
                if platform.lower() == "twitter" and sentiment_score > 0.6:
                    recommendations.append("boost this tweet for wider reach")
            
            # Combine recommendations
            if recommendations:
                return "; ".join(recommendations) + "."
            else:
                return "Monitor engagement and sentiment trends."
                
        except Exception as e:
            logger.error(f"Error generating recommendation: {e}")
            return "Continue monitoring sentiment and engagement."

