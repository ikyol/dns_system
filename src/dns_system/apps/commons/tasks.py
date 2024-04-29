from apscheduler.schedulers.background import BackgroundScheduler

from dns_system.apps.typer.views.api import domain_sync

scheduler = BackgroundScheduler()

scheduler.add_job(domain_sync, "interval", minutes=30)
