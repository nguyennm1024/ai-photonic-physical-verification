"""
Gemini Client Module
====================

Wrapper for Google Gemini API for AI-powered layout analysis.
"""

import os
from typing import Optional
from PIL import Image

try:
    import google.generativeai as genai
except ImportError:
    genai = None


class GeminiClient:
    """
    Wrapper for Google Gemini API.
    Uses two models:
    - gemini-2.5-pro: For detailed discontinuity analysis
    - gemini-2.5-flash: For fast binary classification
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini client.
        
        Args:
            api_key: Google API key (if None, reads from environment)
        """
        if not genai:
            raise ImportError("google-generativeai package not available")
        
        # Get API key from parameter or environment
        if api_key is None:
            api_key = os.getenv('GOOGLE_API_KEY')
        
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not provided and not found in environment")
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Initialize models
        self.analyzer_model = genai.GenerativeModel('gemini-2.5-pro')  # Detailed analysis
        self.classifier_model = genai.GenerativeModel('gemini-2.5-flash')  # Fast classification
        
        print("✅ Initialized Gemini models: Pro (analysis) + Flash (classification)")
    
    def analyze_detailed(self, image: Image.Image, prompt: str) -> str:
        """
        Perform detailed analysis using Gemini Pro.
        
        Args:
            image: PIL Image to analyze
            prompt: Analysis prompt
            
        Returns:
            Detailed analysis result text
        """
        try:
            response = self.analyzer_model.generate_content([prompt, image])
            return response.text
        except Exception as e:
            raise RuntimeError(f"Gemini Pro analysis failed: {e}")
    
    def classify(self, text: str, prompt: str) -> str:
        """
        Fast classification using Gemini Flash.
        
        Args:
            text: Text to classify (typically analysis result)
            prompt: Classification prompt
            
        Returns:
            Classification result (typically one word)
        """
        try:
            response = self.classifier_model.generate_content([prompt])
            return response.text.strip().lower()
        except Exception as e:
            raise RuntimeError(f"Gemini Flash classification failed: {e}")
    
    @staticmethod
    def is_available() -> bool:
        """Check if Gemini API is available"""
        if not genai:
            return False
        
        api_key = os.getenv('GOOGLE_API_KEY')
        return bool(api_key)
    
    @staticmethod
    def get_setup_instructions() -> str:
        """Get instructions for setting up Gemini API"""
        return """
Gemini API Setup Instructions:
==============================

1. Get API Key:
   - Visit: https://makersuite.google.com/app/apikey
   - Sign in with Google account
   - Create a new API key

2. Set Environment Variable:
   
   macOS/Linux:
   export GOOGLE_API_KEY='your_api_key_here'
   
   Windows:
   set GOOGLE_API_KEY=your_api_key_here

3. Make it Permanent (Optional):
   
   macOS/Linux (add to ~/.bashrc or ~/.zshrc):
   echo 'export GOOGLE_API_KEY="your_api_key_here"' >> ~/.zshrc
   
   Windows (System Properties > Environment Variables)

4. Verify:
   python -c "import os; print('API Key set:', bool(os.getenv('GOOGLE_API_KEY')))"
"""

