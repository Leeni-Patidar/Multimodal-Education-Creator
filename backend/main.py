from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from routes.generate import router

app = FastAPI()

# CORS middleware - must be added early
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
async def root():
    return JSONResponse({"message": "API is running. Frontend is on http://localhost:5174"})

@app.get("/favicon.ico")
async def favicon():
    return JSONResponse({"error": "Not found"}, status_code=204)