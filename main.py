from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from openai import OpenAI
import logging

# Hardcoded Gemini key (development/testing)
gemini_key = "AIzaSyAdfD6yDtOF6vbmoxVvtHcuG4SVPTMx_fg"

client = OpenAI(api_key=gemini_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")

app = FastAPI()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("itinerary_api")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class Generate(BaseModel):
    Destination: str
    Start_date: str
    Days: str
    Travel_style: str
    Budget: str
    Interests: str
@app.get("/generate")
@app.post("/generate")
async def generate(data: Generate):
    user_topic = f"""
Destination: {data.Destination}
Start Date: {data.Start_date}
Days: {data.Days}
Travel Style: {data.Travel_style}
Budget: {data.Budget}
Interests: {data.Interests}
"""
    try:
        response = client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert AI travel planner. Return the itinerary as a clean, day-wise formatted plan. "
                        "No markdown, no JSON, no extra explanations. "
                        "Format with --- Day X --- separators."
                    )
                },
                {"role": "user", "content": f"Plan a detailed travel itinerary:\n{user_topic}"}
            ],
            temperature=0.7
        )

        formatted_plan = response.choices[0].message.content
        logger.info(formatted_plan)
        return JSONResponse(content={"itinerary": formatted_plan})

    except Exception as e:
        logger.error(f"Error generating itinerary: {e}")
        return JSONResponse(
            content={"error": "Failed to generate itinerary", "details": str(e)},
            status_code=500
        )
