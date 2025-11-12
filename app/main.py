import io
from pathlib import Path
from typing import Dict

from fastapi import (
    BackgroundTasks,
    FastAPI,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .services.clustering import (
    generate_task_id,
    run_clustering_pipeline,
    serialize_clusters_to_json,
)

app = FastAPI(title="AVOCADO")

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


class TaskManager:
    """A minimal in-memory task registry for clustering jobs."""

    def __init__(self) -> None:
        self._tasks: Dict[str, Dict[str, object]] = {}

    def create_task(self, task_id: str) -> None:
        self._tasks[task_id] = {"status": "processing", "result": None, "error": None}

    def set_result(self, task_id: str, result: Dict[str, object]) -> None:
        self._tasks[task_id] = {"status": "completed", "result": result, "error": None}

    def set_error(self, task_id: str, error: str) -> None:
        self._tasks[task_id] = {"status": "failed", "result": None, "error": error}

    def get(self, task_id: str) -> Dict[str, object]:
        if task_id not in self._tasks:
            raise KeyError(task_id)
        return self._tasks[task_id]


tasks = TaskManager()


def process_file_task(task_id: str, file_bytes: bytes) -> None:
    """Background task that runs the clustering pipeline."""
    try:
        result = run_clustering_pipeline(io.BytesIO(file_bytes))
    except Exception as exc:  # pylint: disable=broad-except
        tasks.set_error(task_id, str(exc))
    else:
        tasks.set_result(task_id, result)


@app.get("/", response_class=HTMLResponse)
async def upload_form(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("upload.html", {"request": request})


@app.post("/upload")
async def upload_file(
    request: Request, file: UploadFile, background_tasks: BackgroundTasks
) -> RedirectResponse:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No file selected."
        )

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported.",
        )

    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    task_id = generate_task_id()
    tasks.create_task(task_id)
    background_tasks.add_task(process_file_task, task_id, file_bytes)
    return RedirectResponse(
        url=request.url_for("processing_view", task_id=task_id),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@app.get("/processing/{task_id}", response_class=HTMLResponse)
async def processing_view(request: Request, task_id: str) -> HTMLResponse:
    try:
        tasks.get(task_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Task not found.") from None

    return templates.TemplateResponse(
        "processing.html", {"request": request, "task_id": task_id}
    )


@app.get("/status/{task_id}")
async def task_status(task_id: str) -> JSONResponse:
    try:
        task = tasks.get(task_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Task not found.") from None

    payload: Dict[str, object] = {"status": task["status"]}

    if task["status"] == "completed":
        payload["redirect_url"] = f"/results/{task_id}"
    elif task["status"] == "failed":
        payload["error"] = task["error"]

    return JSONResponse(payload)


@app.get("/results/{task_id}", response_class=HTMLResponse)
async def results_view(request: Request, task_id: str) -> HTMLResponse:
    try:
        task = tasks.get(task_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Task not found.") from None

    if task["status"] == "processing":
        return RedirectResponse(
            url=request.url_for("processing_view", task_id=task_id),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    if task["status"] == "failed":
        return templates.TemplateResponse(
            "results.html",
            {
                "request": request,
                "task_id": task_id,
                "result": None,
                "error": task["error"],
            },
        )

    result = task["result"]
    return templates.TemplateResponse(
        "results.html",
        {"request": request, "task_id": task_id, "result": result, "error": None},
    )


@app.get("/download/{task_id}")
async def download_result(task_id: str) -> Response:
    try:
        task = tasks.get(task_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Task not found.") from None

    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Result not available.")

    result_json = serialize_clusters_to_json(task["result"]).encode("utf-8")

    headers = {
        "Content-Disposition": f'attachment; filename="clusters_{task_id}.json"',
        "Cache-Control": "no-store",
    }
    return Response(
        content=result_json,
        media_type="application/json",
        headers=headers,
    )

