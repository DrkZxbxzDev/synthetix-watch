from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional

from app.database.connection import get_db
from app.database.models import MonitorTarget, MonitorResult
from app.services.monitor import QAWebMonitor
from app.core.scheduler import scheduler, run_all_checks

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────────────

class TargetCreate(BaseModel):
    name: str
    url: str
    expected_selector: Optional[str] = None

class TargetUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    expected_selector: Optional[str] = None
    is_active: Optional[bool] = None


# ── Targets ───────────────────────────────────────────────────────────────────

@router.get("/targets", tags=["Targets"])
async def list_targets(db: AsyncSession = Depends(get_db)):
    """Lista todos los targets registrados."""
    result = await db.execute(select(MonitorTarget))
    return result.scalars().all()


@router.post("/targets", status_code=201, tags=["Targets"])
async def create_target(body: TargetCreate, db: AsyncSession = Depends(get_db)):
    """Registra un nuevo target para monitorear."""
    target = MonitorTarget(**body.model_dump())
    db.add(target)
    await db.flush()
    await db.refresh(target)
    return target


@router.patch("/targets/{target_id}", tags=["Targets"])
async def update_target(
    target_id: int,
    body: TargetUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Actualiza nombre, URL, selector o estado activo de un target."""
    result = await db.execute(
        select(MonitorTarget).where(MonitorTarget.id == target_id)
    )
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="Target no encontrado")

    for field, value in body.model_dump(exclude_none=True).items():
        setattr(target, field, value)

    await db.flush()
    await db.refresh(target)
    return target


@router.delete("/targets/{target_id}", status_code=204, tags=["Targets"])
async def delete_target(target_id: int, db: AsyncSession = Depends(get_db)):
    """Elimina un target y todo su historial."""
    result = await db.execute(
        select(MonitorTarget).where(MonitorTarget.id == target_id)
    )
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="Target no encontrado")
    await db.delete(target)


# ── Checks ────────────────────────────────────────────────────────────────────

@router.post("/targets/{target_id}/check", tags=["Checks"])
async def run_check(target_id: int, db: AsyncSession = Depends(get_db)):
    """Ejecuta un check manual e inmediato sobre un target."""
    result = await db.execute(
        select(MonitorTarget).where(MonitorTarget.id == target_id)
    )
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="Target no encontrado")

    data = await QAWebMonitor.run_check(target.url, target.expected_selector)
    monitor_result = MonitorResult(
        target_id=target.id,
        status_code=data["status_code"],
        response_time=data["response_time"],
        is_up=data["is_up"],
        error_message=data["error_message"],
        screenshot_path=data["screenshot_path"],
    )
    db.add(monitor_result)
    await db.flush()
    await db.refresh(monitor_result)
    return monitor_result


@router.get("/targets/{target_id}/results", tags=["Checks"])
async def get_results(
    target_id: int,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """Historial de resultados de un target (más reciente primero)."""
    exists = await db.execute(
        select(MonitorTarget).where(MonitorTarget.id == target_id)
    )
    if not exists.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Target no encontrado")

    results = await db.execute(
        select(MonitorResult)
        .where(MonitorResult.target_id == target_id)
        .order_by(MonitorResult.checked_at.desc())
        .limit(limit)
    )
    return results.scalars().all()


# ── Dashboard ─────────────────────────────────────────────────────────────────

@router.get("/dashboard", tags=["Dashboard"])
async def dashboard(db: AsyncSession = Depends(get_db)):
    """Resumen general: totales, uptime % y estado actual de cada target."""
    total_targets = await db.scalar(select(func.count(MonitorTarget.id)))
    active_targets = await db.scalar(
        select(func.count(MonitorTarget.id)).where(MonitorTarget.is_active == True)
    )
    total_checks = await db.scalar(select(func.count(MonitorResult.id)))

    targets_result = await db.execute(select(MonitorTarget))
    targets = targets_result.scalars().all()

    summary = []
    for target in targets:
        last = await db.execute(
            select(MonitorResult)
            .where(MonitorResult.target_id == target.id)
            .order_by(MonitorResult.checked_at.desc())
            .limit(1)
        )
        last_result = last.scalar_one_or_none()

        up_count = await db.scalar(
            select(func.count(MonitorResult.id)).where(
                MonitorResult.target_id == target.id,
                MonitorResult.is_up == True,
            )
        )
        total_count = await db.scalar(
            select(func.count(MonitorResult.id)).where(
                MonitorResult.target_id == target.id
            )
        )
        uptime_pct = round(up_count / total_count * 100, 1) if total_count else None

        summary.append({
            "id": target.id,
            "name": target.name,
            "url": target.url,
            "is_active": target.is_active,
            "uptime_pct": uptime_pct,
            "last_check": {
                "is_up": last_result.is_up,
                "status_code": last_result.status_code,
                "response_time": round(last_result.response_time, 3),
                "checked_at": last_result.checked_at,
            } if last_result else None,
        })

    return {
        "total_targets": total_targets,
        "active_targets": active_targets,
        "total_checks": total_checks,
        "targets": summary,
    }


# ── Scheduler ─────────────────────────────────────────────────────────────────

@router.get("/scheduler/status", tags=["Scheduler"])
async def scheduler_status():
    """Estado actual del scheduler y próxima ejecución."""
    job = scheduler.get_job("monitor_job")
    return {
        "running": scheduler.running,
        "next_run": job.next_run_time if job else None,
    }


@router.post("/scheduler/run-now", tags=["Scheduler"])
async def run_now():
    """Dispara todos los checks inmediatamente sin esperar el intervalo."""
    await run_all_checks()
    return {"message": "Checks ejecutados correctamente"}