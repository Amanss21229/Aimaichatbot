"""
Mock API module for testing when real website API is unavailable
यह मॉड्यूल वास्तविक वेबसाइट API न होने पर टेस्टिंग के लिए उपयोग होता है
"""

import random
from typing import Dict, Any

# Sample NEET/JEE questions and answers for mock responses
MOCK_RESPONSES = [
    {
        "question": "What is the SI unit of electric current?",
        "short_answer": "Ampere (A) is the SI unit of electric current. It is named after André-Marie Ampère.",
        "detailed_url": "https://example.com/solution/electric-current-si-unit",
        "solution_id": "phys_001"
    },
    {
        "question": "Define photosynthesis",
        "short_answer": "Photosynthesis is the process where plants convert light energy into chemical energy, producing glucose and oxygen from CO2 and water.",
        "detailed_url": "https://example.com/solution/photosynthesis-definition",
        "solution_id": "bio_001"
    },
    {
        "question": "What is Newton's second law of motion?",
        "short_answer": "F = ma (Force equals mass times acceleration). It states that the force acting on an object is equal to the mass of that object times its acceleration.",
        "detailed_url": "https://example.com/solution/newtons-second-law",
        "solution_id": "phys_002"
    },
    {
        "question": "What is the molecular formula of glucose?",
        "short_answer": "C₆H₁₂O₆ is the molecular formula of glucose. It's a simple sugar and the primary energy source for cells.",
        "detailed_url": "https://example.com/solution/glucose-formula",
        "solution_id": "chem_001"
    },
    {
        "question": "Define osmosis",
        "short_answer": "Osmosis is the movement of water molecules through a semi-permeable membrane from a region of higher concentration to lower concentration.",
        "detailed_url": "https://example.com/solution/osmosis-definition",
        "solution_id": "bio_002"
    }
]

async def get_mock_answer(question: str, uid: int, mode: str = "short") -> Dict[str, Any]:
    """
    Generate mock answer for testing
    Returns realistic response mimicking actual API
    
    Args:
        question: The question text
        uid: User ID (for logging purposes)
        mode: "short" or "detailed"
    
    Returns:
        Dict with short_answer, detailed_url, solution_id
    """
    # Pick a random mock response
    response = random.choice(MOCK_RESPONSES)
    
    return {
        "success": True,
        "question": question[:100] + "..." if len(question) > 100 else question,
        "short_answer": response["short_answer"],
        "detailed_url": response["detailed_url"],
        "solution_id": response["solution_id"],
        "mode": mode,
        "uid": uid
    }

async def get_mock_image_answer(file_path: str, uid: int) -> Dict[str, Any]:
    """
    Mock response for image-based questions
    
    Args:
        file_path: Path to image file
        uid: User ID
    
    Returns:
        Dict with answer details
    """
    return {
        "success": True,
        "question": "Image question received",
        "short_answer": "यह एक गणित का सवाल है। समीकरण को हल करने के लिए quadratic formula का उपयोग करें: x = (-b ± √(b²-4ac)) / 2a",
        "detailed_url": "https://example.com/solution/quadratic-equation-image",
        "solution_id": "math_img_001",
        "mode": "short",
        "uid": uid
    }
