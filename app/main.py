import os
from dotenv import load_dotenv

# look for a “.env” in the cwd and load its vars into os.environ
load_dotenv()

# now you can
API_KEY = os.getenv("GROQ_API_KEY")

from fastapi import FastAPI
from app.routes.predict import router as predict_router

app = FastAPI()
app.include_router(predict_router)