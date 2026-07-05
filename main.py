import time
import uuid

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# ---- 1. YOUR SETTINGS -------------------------------------------------
ALLOWED_ORIGIN = "https://dash-0ge2nw.example.com"
YOUR_EMAIL = "24f2006358@ds.study.iitm.ac.in "  # <-- CHANGE THIS!
# ------------------------------------------------------------------------

app = FastAPI()

# The "bouncer": only this one origin gets let in the door.
# No wildcards ("*") anywhere.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)


# The "stopwatch + ID stamper": runs on every single response.
@app.middleware("http")
async def add_custom_headers(request: Request, call_next):
    start = time.perf_counter()
    request_id = str(uuid.uuid4())
    response = await call_next(request)
    duration = time.perf_counter() - start
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{duration:.6f}"
    return response


@app.get("/stats")
async def stats(values: str = Query(..., description="Comma-separated integers")):
    try:
        nums = [int(v.strip()) for v in values.split(",") if v.strip() != ""]
    except ValueError:
        raise HTTPException(status_code=400, detail="values must be comma-separated integers")

    if not nums:
        raise HTTPException(status_code=400, detail="values cannot be empty")

    total = sum(nums)
    count = len(nums)

    result = {
        "email": YOUR_EMAIL,
        "count": count,
        "sum": total,
        "min": min(nums),
        "max": max(nums),
        "mean": total / count,
    }
    return JSONResponse(content=result)


@app.get("/")
async def root():
    return {"status": "ok", "docs": "/docs"}
