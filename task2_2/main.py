from fastapi import FastAPI
from task2_2.models import Feedback
from task2_2.feedback_storage import feedbacks

app = FastAPI()

@app.post("/feedback")
async def create_feedback(feedback: Feedback):
    feedbacks.append(feedback.dict())
    return {"message": f"Спасибо, {feedback.name}! Ваш отзыв сохранён."}

@app.get("/feedbacks")
async def get_all_feedbacks():
    return feedbacks

@app.get("/")
async def root():
    return {"message": "POST /feedback - отправить отзыв"}