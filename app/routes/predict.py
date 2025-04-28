import os
from groq import Groq
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.auth import get_current_user
from app.main import API_KEY

# Initialize Groq client
client = Groq(api_key=API_KEY)

router = APIRouter()

class Prompt(BaseModel):
    prompt: str

@router.get("/models")
async def list_models(user=Depends(get_current_user)):
    """
    List available models accessible with your API key.
    """
    try:
        models = await client.models.list()
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing models: {e}")

@router.post("/predict")
async def predict(body: Prompt, user=Depends(get_current_user)):
    """
    Groq-powered predict endpoint using a LLaMA model.
    """
    try:
        chat_resp = client.chat.completions.create(
            model="gemma2-9b-it",  # choose an accessible LLaMA model
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user",   "content": body.prompt}
            ],
            max_tokens=512,
            temperature=0.7,
        )
        assistant_msg = chat_resp.choices[0].message.content
        return {"output": assistant_msg}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {e}")
