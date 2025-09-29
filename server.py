import os
from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()

# Главная (для проверки)
@app.get("/")
def home():
    return {"status": "ok", "message": "Bot is running"}

# Отдаём оферту
@app.get("/offer")
def get_offer():
    return FileResponse("static/offer.pdf", media_type="application/pdf")
