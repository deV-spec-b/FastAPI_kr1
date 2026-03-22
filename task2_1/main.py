from fastapi import FastAPI
from task2_1.models import Feedback
from task2_1.feedback_storage import feedbacks

app = FastAPI()

@app.post("/feedback")
async def create_feedback(feedback: Feedback):
    feedbacks.append(feedback.dict())
    return {"message": f"Feedback received. Thank you, {feedback.name}."}

@app.get("/feedbacks")
async def get_all_feedbacks():
    return feedbacks

@app.get("/")
async def root():
    return {"message": "запрос POST для просмотра фидбеков /feedback"}