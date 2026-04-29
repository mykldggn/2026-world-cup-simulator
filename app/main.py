from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from .data import tournament_metadata
from .simulator import WorldCupSimulator


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="2026 World Cup Simulator", version="0.1.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

simulator = WorldCupSimulator()


class SimulationRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    iterations: int = Field(default=400, ge=50, le=3000)
    scenario: str = Field(default="balanced")
    host_advantage: bool = Field(default=True, alias="hostAdvantage")
    featured_team: Optional[str] = Field(default=None, alias="featuredTeam")
    seed: Optional[int] = Field(default=None, ge=1, le=999_999_999)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/metadata")
def metadata() -> dict:
    return tournament_metadata()


@app.post("/api/simulate")
def simulate(payload: SimulationRequest) -> dict:
    return simulator.simulate(
        iterations=payload.iterations,
        scenario=payload.scenario,
        host_advantage=payload.host_advantage,
        featured_team=payload.featured_team,
        seed=payload.seed,
    )


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")
