import google.generativeai as genai
import os
from dotenv import load_dotenv
from typing import List, Dict, Any
import json
from google.genai import types


load_dotenv()
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")


response_schema = {
    "type": "object",
    "properties": {
        "planets": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the planet themed around the financial goal",
                    },
                    "image": {
                        "type": "string",
                        "description": "Image filename for the planet (e.g., 'savings-planet.png')",
                    },
                    "achievements": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Name of the achievement",
                                },
                                "description": {
                                    "type": "string",
                                    "description": "Detailed description of what the achievement entails and why it matters",
                                },
                                "type": {
                                    "type": "string",
                                    "enum": ["progress", "streak", "game"],
                                    "description": "Type of achievement",
                                },
                                "data": {
                                    "type": "object",
                                    "properties": {
                                        "startDate": {
                                            "type": "string",
                                            "description": "Start date in YYYY-MM-DD format (required for all types)",
                                        },
                                        "endDate": {
                                            "type": "string",
                                            "description": "End date in YYYY-MM-DD format (required for all types)",
                                        },
                                        "moneyToSave": {
                                            "type": "number",
                                            "description": "Target amount to save (for progress type)",
                                        },
                                        "numConsecutiveDays": {
                                            "type": "integer",
                                            "description": "Number of consecutive days (for streak type)",
                                        },
                                        "minimumStreakAmount": {
                                            "type": "number",
                                            "description": "Minimum amount per streak period (for streak type)",
                                        },
                                        "frequency": {
                                            "type": "string",
                                            "enum": ["daily", "weekly", "monthly"],
                                            "description": "Frequency of streak (for streak type)",
                                        },
                                    },
                                    "required": ["startDate", "endDate"],
                                    "description": "Achievement data - all types require startDate and endDate, additional fields depend on achievement type",
                                },
                            },
                            "required": ["name", "description", "type", "data"],
                        },
                    },
                },
                "required": ["name", "image", "achievements"],
            },
        }
    },
    "required": ["planets"],
}

response_sample = {
    "planets": [
        {
            "name": "Mercury Momentum",
            "image": "mercury-planet.png",
            "achievements": [
                {
                    "name": "First Gear Saver",
                    "description": "Save your first $500 toward your new car in just 3 weeks. Every journey starts with a single step - let's get rolling!",
                    "type": "progress",
                    "data": {
                        "startDate": "2025-10-18",
                        "endDate": "2025-11-08",
                        "moneyToSave": 500,
                    },
                },
                {
                    "name": "Daily Drive Discipline",
                    "description": "Save at least $15 every day for 5 consecutive days. Small daily habits lead to big wins!",
                    "type": "streak",
                    "data": {
                        "startDate": "2025-10-18",
                        "endDate": "2025-10-22",
                        "numConsecutiveDays": 5,
                        "minimumStreakAmount": 15,
                        "frequency": "daily",
                    },
                },
            ],
        },
        {
            "name": "Venus Value",
            "image": "venus-planet.png",
            "achievements": [
                {
                    "name": "Budget Roadmap",
                    "description": "Learn to track your expenses like a pro with this interactive budgeting game. Knowledge is power when saving for big goals!",
                    "type": "game",
                    "data": {
                        "startDate": "2025-11-08",
                        "endDate": "2025-12-01",
                    },
                },
                {
                    "name": "Car Fund Kickstart",
                    "description": "Reach $1,000 in your car savings fund within 6 weeks. You're 10% of the way to your dream car!",
                    "type": "progress",
                    "data": {
                        "startDate": "2025-11-08",
                        "endDate": "2025-12-20",
                        "moneyToSave": 1000,
                    },
                },
            ],
        },
        {
            "name": "Earth Economy",
            "image": "earth-planet.png",
            "achievements": [
                {
                    "name": "Foundation Builder",
                    "description": "Save $2,000 over 8 weeks while managing your student loan payments. Balance is the key to financial success!",
                    "type": "progress",
                    "data": {
                        "startDate": "2025-12-20",
                        "endDate": "2026-02-14",
                        "moneyToSave": 2000,
                    },
                },
                {
                    "name": "Weekly Warrior",
                    "description": "Maintain a 7-day streak saving $25 daily. Consistency builds the foundation for reaching big goals!",
                    "type": "streak",
                    "data": {
                        "startDate": "2025-12-20",
                        "endDate": "2025-12-26",
                        "numConsecutiveDays": 7,
                        "minimumStreakAmount": 25,
                        "frequency": "daily",
                    },
                },
            ],
        },
        {
            "name": "Mars Momentum",
            "image": "mars-planet.png",
            "achievements": [
                {
                    "name": "Mid-Journey Milestone",
                    "description": "Hit the $4,000 mark in your car savings - you're almost halfway there! The finish line is in sight!",
                    "type": "progress",
                    "data": {
                        "startDate": "2026-02-14",
                        "endDate": "2026-04-25",
                        "moneyToSave": 4000,
                    },
                },
                {
                    "name": "Two-Week Turbo",
                    "description": "Save $35 per day for 14 consecutive days. You're accelerating toward your goal faster than ever!",
                    "type": "streak",
                    "data": {
                        "startDate": "2026-02-14",
                        "endDate": "2026-02-27",
                        "numConsecutiveDays": 14,
                        "minimumStreakAmount": 35,
                        "frequency": "daily",
                    },
                },
            ],
        },
        {
            "name": "Jupiter Journey",
            "image": "jupiter-planet.png",
            "achievements": [
                {
                    "name": "Investment Explorer",
                    "description": "Learn about low-risk investment options through this simulation. Make your car fund work harder while staying safe!",
                    "type": "game",
                    "data": {
                        "startDate": "2026-04-25",
                        "endDate": "2026-06-15",
                    },
                },
                {
                    "name": "Halfway Hero",
                    "description": "Reach the major milestone of $6,500 saved for your car. You're over halfway to driving off the lot!",
                    "type": "progress",
                    "data": {
                        "startDate": "2026-04-25",
                        "endDate": "2026-07-11",
                        "moneyToSave": 6500,
                    },
                },
                {
                    "name": "Three-Week Champion",
                    "description": "Achieve a 21-day streak saving $50 daily. Your commitment to your car goal is unstoppable!",
                    "type": "streak",
                    "data": {
                        "startDate": "2026-04-25",
                        "endDate": "2026-05-15",
                        "numConsecutiveDays": 21,
                        "minimumStreakAmount": 50,
                        "frequency": "daily",
                    },
                },
            ],
        },
        {
            "name": "Saturn Stability",
            "image": "saturn-planet.png",
            "achievements": [
                {
                    "name": "Final Stretch Sprint",
                    "description": "Push to $9,000 in your car fund over 10 weeks. The keys to your new car are almost in hand!",
                    "type": "progress",
                    "data": {
                        "startDate": "2026-07-11",
                        "endDate": "2026-09-19",
                        "moneyToSave": 9000,
                    },
                },
                {
                    "name": "Monthly Master",
                    "description": "Complete a full 30-day streak saving $60 daily. Your discipline is what separates dreamers from achievers!",
                    "type": "streak",
                    "data": {
                        "startDate": "2026-07-11",
                        "endDate": "2026-08-09",
                        "numConsecutiveDays": 30,
                        "minimumStreakAmount": 60,
                        "frequency": "daily",
                    },
                },
            ],
        },
        {
            "name": "Uranus Upgrade",
            "image": "uranus-planet.png",
            "achievements": [
                {
                    "name": "Down Payment Ready",
                    "description": "Reach $11,500 saved - enough for a solid down payment on your new car! Financial independence feels incredible!",
                    "type": "progress",
                    "data": {
                        "startDate": "2026-09-19",
                        "endDate": "2026-11-28",
                        "moneyToSave": 11500,
                    },
                },
                {
                    "name": "Financial Planning Pro",
                    "description": "Master advanced budgeting and car financing strategies through this challenge. Make the smartest purchase decision!",
                    "type": "game",
                    "data": {
                        "startDate": "2026-09-19",
                        "endDate": "2026-10-31",
                    },
                },
                {
                    "name": "Six-Week Elite",
                    "description": "Maintain a 45-day streak saving $70 daily. You're in the top tier of committed savers!",
                    "type": "streak",
                    "data": {
                        "startDate": "2026-09-19",
                        "endDate": "2026-11-02",
                        "numConsecutiveDays": 45,
                        "minimumStreakAmount": 70,
                        "frequency": "daily",
                    },
                },
            ],
        },
        {
            "name": "Neptune Nirvana",
            "image": "neptune-planet.png",
            "achievements": [
                {
                    "name": "New Car Champion",
                    "description": "Achieve your ultimate goal of $14,000 saved for your new car in 12 months! You did it - financial security and independence are yours!",
                    "type": "progress",
                    "data": {
                        "startDate": "2026-11-28",
                        "endDate": "2027-02-06",
                        "moneyToSave": 14000,
                    },
                },
                {
                    "name": "Two-Month Legend",
                    "description": "Complete an epic 60-day streak saving $80 daily. You've proven that commitment plus consistency equals success!",
                    "type": "streak",
                    "data": {
                        "startDate": "2026-11-28",
                        "endDate": "2027-01-26",
                        "numConsecutiveDays": 60,
                        "minimumStreakAmount": 80,
                        "frequency": "daily",
                    },
                },
                {
                    "name": "Wealth Builder Mastery",
                    "description": "Complete the comprehensive financial independence course. You now have all the tools to achieve any financial goal!",
                    "type": "game",
                    "data": {
                        "startDate": "2026-11-28",
                        "endDate": "2027-01-31",
                    },
                },
            ],
        },
    ]
}


def generate_gamified_structure(questionnaire: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Generates gamified planet and achievement structure from user questionnaire responses.

    Args:
        questionnaire: List of dictionaries with 'question' and 'answer' keys

    Returns:
        Dictionary containing structured planet/achievement data
    """
    # Create a formatted string of the questionnaire
    questionnaire_text = "\n\n".join(
        [
            f"{idx + 1}. Q: {qa['question']}\n   A: {qa['answer']}"
            for idx, qa in enumerate(questionnaire)
        ]
    )

    system_instruction = f"""You are a financial gamification expert. Your job is to analyze user responses about their financial goals and spending habits, then create an engaging gamified structure with planets and achievements.


IMPORTANT GUIDELINES:
1. Create EXACTLY 8 planets based on the user's financial goals, modeled after the solar system (Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune)
2. Each planet should represent a major financial theme with creative names inspired by finance and the solar system (e.g., "Mercury Savings", "Venus Budget", "Earth Balance", "Mars Momentum", "Jupiter Growth", "Saturn Stability", "Uranus Innovation", "Neptune Mastery")
3. **CRITICAL: Planets MUST be in sequential, progressive order.** Each planet should be harder than the previous one:
   - Planet 1 (Mercury): Beginner level achievements (e.g., save $200, 3-day streak)
   - Planet 2 (Venus): Early starter (e.g., save $500, 5-day streak)
   - Planet 3 (Earth): Foundation level (e.g., save $1000, 7-day streak)
   - Planet 4 (Mars): Intermediate level (e.g., save $1500, 14-day streak)
   - Planet 5 (Jupiter): Advanced level (e.g., save $2000, 21-day streak)
   - Planet 6 (Saturn): Expert level (e.g., save $2500, 30-day streak)
   - Planet 7 (Uranus): Master level (e.g., save $3000, 45-day streak)
   - Planet 8 (Neptune): Elite/mastery level (e.g., save $3500+, 60-day streak)
4. Achievements within each planet should build on the previous planet's achievements:
   - If Planet 1 has "Save $200", Planet 2 should have "Save $500", Planet 3 "Save $1000", etc.
   - If Planet 1 has a 3-day streak, Planet 2 should have 5-day, Planet 3 7-day, etc.
   - Games should progress from simple to increasingly complex
5. Each planet should have 1-3 achievements that are specific, measurable, and relevant to the user's responses
6. Achievement types:
   - "progress": Goal with a specific money target and timeframe
   - "streak": Repeated behavior over consecutive periods
   - "game": Interactive challenge or educational game
7. Use realistic dates with appropriate durations for each difficulty level
8. Base money amounts on the user's stated goals and current spending patterns, scaling them progressively
9. Make achievement names engaging and motivational, reflecting increasing difficulty
10. Image names should reflect the solar system progression (e.g., "mercury-planet.png", "venus-planet.png", "earth-planet.png", "mars-planet.png", "jupiter-planet.png", "saturn-planet.png", "uranus-planet.png", "neptune-planet.png")
11. Try to change up the names of the planets to be more financially themed while still reflecting their solar system counterparts
12. For each achievement, have a description on what specificially needs to be done to complete it.
DATA FIELD RULES (only include relevant fields for each type):
- progress type: requires startDate, endDate, moneyToSave
- streak type: requires startDate, endDate, numConsecutiveDays, minimumStreakAmount, frequency
- game type: requires startDate, endDate


You must respond with valid JSON matching the specified schema. Do not include any markdown formatting or code blocks. Follow the format of {response_schema}.
\n Here is an example of the expected response format:
{response_sample}"""

    user_prompt = f"""Based on the following user questionnaire responses, create a gamified planet and achievement structure:


{questionnaire_text}


Generate planets and achievements that are:
- Directly related to their stated goals and spending habits
- Achievable but challenging
- Varied in type (mix of progress, streak, and game achievements)
- Motivating and fun


Respond with a valid JSON object matching this structure:
{json.dumps(response_schema, indent=2)}"""

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        "gemini-2.5-pro", system_instruction=system_instruction
    )
    response = model.generate_content(
        user_prompt,
        generation_config=genai.types.GenerationConfig(
            response_mime_type="application/json",
            response_schema=response_schema,
        ),
    )
    try:
        data = json.loads(response.text)
        # print("RESPONSE DATA: " + str(data))
        # print(response.text)
        return data
    except Exception as e:
        print(f"Error processing response: {e}")
        return response_sample
