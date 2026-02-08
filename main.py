from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from playwright.sync_api import sync_playwright
from starlette.concurrency import run_in_threadpool
import time
import traceback

app = FastAPI()


# --------------------------------------------------
# Request model
# --------------------------------------------------
class CaptureRequest(BaseModel):
    goto_url: str
    capture_url_contains: str | None = None
    method: str = "GET"
    timeout_ms: int = 15000


# --------------------------------------------------
# Core Playwright Runner
# --------------------------------------------------
def run_playwright(req: CaptureRequest, mode: str):
    """
    mode:
      - target : capture one matching API
      - all    : capture all requests/responses (basic)
      - full   : capture full request/response details
    """

    events = []
    target_response = None

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,
                args=["--no-sandbox", "--disable-dev-shm-usage"],
            )

            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1920, "height": 1080},
            )

            page = context.new_page()

            # ---------------- REQUEST HANDLER ----------------
            def on_request(request):
                try:
                    entry = {
                        "type": "request",
                        "url": request.url,
                        "method": request.method,
                        "headers": request.headers,
                        "post_data": request.post_data,
                        "resource_type": request.resource_type,
                        "timestamp": time.time(),
                    }

                    if mode == "full":
                        events.append(entry)
                    elif mode == "all":
                        events.append({
                            "type": "request",
                            "method": request.method,
                            "url": request.url,
                        })
                except Exception:
                    # NEVER allow listener to throw
                    traceback.print_exc()

            # ---------------- RESPONSE HANDLER ----------------
            def on_response(response):
                nonlocal target_response
                try:
                    entry = {
                        "type": "response",
                        "url": response.url,
                        "status": response.status,
                        "status_text": response.status_text,
                        "headers": response.headers,
                        "from_service_worker": response.from_service_worker,
                        "timestamp": time.time(),
                    }

                    if mode == "full":
                        try:
                            entry["body"] = response.text()
                        except Exception:
                            entry["body"] = None
                        events.append(entry)

                    elif mode == "all":
                        events.append({
                            "type": "response",
                            "status": response.status,
                            "url": response.url,
                        })

                    if (
                        mode == "target"
                        and req.capture_url_contains
                        and req.capture_url_contains in response.url
                        and response.request.method.upper() == req.method.upper()
                    ):
                        target_response = response

                except Exception:
                    traceback.print_exc()

            page.on("request", on_request)
            page.on("response", on_response)

            page.goto(req.goto_url, wait_until="domcontentloaded")

            # ---------------- WAIT LOOP ----------------
            start = time.time()
            while time.time() - start < req.timeout_ms / 1000:
                if mode == "target" and target_response:
                    break
                page.wait_for_timeout(200)

            # ---------------- RESULTS ----------------
            if mode in ("all", "full"):
                browser.close()
                return {
                    "status": "success",
                    "events": events,
                }

            if not target_response:
                browser.close()
                raise Exception("Target API not captured")

            response = target_response
            result = {
                "status": "success",
                "url": response.url,
                "status_code": response.status,
                "headers": response.headers,
            }

            try:
                result["data"] = response.json()
            except Exception:
                result["data"] = response.text()

            browser.close()
            return result

    except Exception as e:
        traceback.print_exc()
        raise Exception(str(e))


# --------------------------------------------------
# ENDPOINTS
# --------------------------------------------------

@app.post("/capture/target")
async def capture_target(req: CaptureRequest):
    if not req.capture_url_contains:
        raise HTTPException(
            status_code=400,
            detail="capture_url_contains is required for /capture/target",
        )
    try:
        return await run_in_threadpool(run_playwright, req, "target")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/capture/all")
async def capture_all(req: CaptureRequest):
    try:
        return await run_in_threadpool(run_playwright, req, "all")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/capture/full")
async def capture_full(req: CaptureRequest):
    try:
        return await run_in_threadpool(run_playwright, req, "full")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
