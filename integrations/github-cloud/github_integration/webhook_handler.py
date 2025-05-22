import logging

from fastapi import FastAPI, HTTPException, Request

app = FastAPI()
logger = logging.getLogger(__name__)


@app.post("/webhook")
async def handle_webhook(request: Request):
    payload = await request.json()
    event = request.headers.get("X-GitHub-Event")

    logger.info(f"Received webhook event: {event}")

    if event == "push":
        # Handle push event
        logger.info(f"Push event payload: {payload}")
    elif event == "pull_request":
        # Handle pull request event
        logger.info(f"Pull request event payload: {payload}")
    elif event == "issues":
        # Handle issues event
        logger.info(f"Issues event payload: {payload}")
    else:
        logger.error(f"Unsupported event type: {event}")
        raise HTTPException(status_code=400, detail="Unsupported event type")

    return {"status": "success"}
