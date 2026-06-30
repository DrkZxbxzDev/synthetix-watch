from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from app.database.connection import AsyncSessionLocal
from app.database.models import MonitorTarget, MonitorResult
from app.services.monitor import QAWebMonitor

scheduler = AsyncIOScheduler()


async def run_all_checks():
    """Ejecuta checks sobre todos los targets activos."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(MonitorTarget).where(MonitorTarget.is_active == True)
        )
        targets = result.scalars().all()

        for target in targets:
            data = await QAWebMonitor.run_check(target.url, target.expected_selector)
            session.add(MonitorResult(
                target_id=target.id,
                status_code=data["status_code"],
                response_time=data["response_time"],
                is_up=data["is_up"],
                error_message=data["error_message"],
                screenshot_path=data["screenshot_path"],
            ))

        await session.commit()
        print(f"Checks completados para {len(targets)} target(s)")


def start_scheduler(interval_minutes: int = 5):
    scheduler.add_job(
        run_all_checks,
        trigger="interval",
        minutes=interval_minutes,
        id="monitor_job",
        replace_existing=True,
    )
    scheduler.start()
    print(f"Scheduler iniciado — checks cada {interval_minutes} minutos")


def stop_scheduler():
    scheduler.shutdown()
    print("Scheduler detenido")