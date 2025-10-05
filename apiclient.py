"""
API Client wrapper for website API calls
Handles retry logic, error handling, and fallback to mock API
"""

import os
import aiohttp
import asyncio
from typing import Dict, Any, Optional
import mock_api

# Environment variables
WEBSITE_API_URL = os.getenv("WEBSITE_API_URL", "")
WEBSITE_API_KEY = os.getenv("WEBSITE_API_KEY", "")
USE_MOCK_API = not WEBSITE_API_URL or WEBSITE_API_URL == ""

class APIClient:
    """Website API client with retry logic and error handling"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.use_mock = USE_MOCK_API
    
    async def init_session(self):
        """Initialize aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def get_answer(self, question: str, uid: int, mode: str = "short", retry_count: int = 0) -> Dict[str, Any]:
        """
        Get answer from website API with retry logic
        
        Args:
            question: Question text
            uid: User ID
            mode: "short" or "detailed"
            retry_count: Current retry attempt
        
        Returns:
            Dict with answer data or error
        """
        # Use mock API if no real API URL configured
        if self.use_mock:
            print(f"🔄 Using mock API for question: {question[:50]}...")
            return await mock_api.get_mock_answer(question, uid, mode)
        
        # Initialize session if needed
        await self.init_session()
        
        # Prepare request
        headers = {}
        if WEBSITE_API_KEY:
            headers["Authorization"] = f"Bearer {WEBSITE_API_KEY}"
        
        payload = {
            "q": question,
            "uid": uid,
            "mode": mode
        }
        
        try:
            # Make API call with timeout
            if self.session:
                async with self.session.post(
                    WEBSITE_API_URL,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        error_msg = f"API returned status {response.status}"
                        print(f"❌ API Error: {error_msg}")
                        
                        # Retry logic with exponential backoff
                        if retry_count < 2:
                            wait_time = (retry_count + 1) * 2
                            print(f"⏳ Retrying in {wait_time} seconds...")
                            await asyncio.sleep(wait_time)
                            return await self.get_answer(question, uid, mode, retry_count + 1)
                        
                        # Fallback to mock after retries
                        print("🔄 Falling back to mock API")
                        return await mock_api.get_mock_answer(question, uid, mode)
            else:
                return await mock_api.get_mock_answer(question, uid, mode)
        
        except asyncio.TimeoutError:
            print(f"⏱️ API timeout (attempt {retry_count + 1})")
            
            if retry_count < 2:
                await asyncio.sleep((retry_count + 1) * 2)
                return await self.get_answer(question, uid, mode, retry_count + 1)
            
            # Fallback to mock
            return await mock_api.get_mock_answer(question, uid, mode)
        
        except Exception as e:
            print(f"❌ API Exception: {str(e)}")
            
            if retry_count < 2:
                await asyncio.sleep((retry_count + 1) * 2)
                return await self.get_answer(question, uid, mode, retry_count + 1)
            
            # Fallback to mock
            return await mock_api.get_mock_answer(question, uid, mode)
    
    async def get_image_answer(self, file_path: str, uid: int) -> Dict[str, Any]:
        """
        Get answer for image-based question
        
        Args:
            file_path: Path to downloaded image
            uid: User ID
        
        Returns:
            Dict with answer data
        """
        # Use mock for images if no API
        if self.use_mock:
            return await mock_api.get_mock_image_answer(file_path, uid)
        
        # If real API exists, implement multipart upload here
        # For now, fallback to mock
        return await mock_api.get_mock_image_answer(file_path, uid)

# Global API client instance
api_client = APIClient()
