"""
Management command to run APScheduler for background tasks.
Polls 9PSB every 3 minutes for pending corporate account statuses.

Usage:
    python manage.py runapscheduler
"""
import logging
from django.conf import settings
from django.core.management.base import BaseCommand

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util

from corporates.tasks import poll_pending_corporate_statuses

logger = logging.getLogger(__name__)


@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """Delete APScheduler job execution entries older than max_age (default 7 days)."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = 'Runs APScheduler for background tasks (corporate status polling)'

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), 'default')

        interval = getattr(settings, 'CORPORATE_STATUS_POLL_INTERVAL', 180)

        scheduler.add_job(
            poll_pending_corporate_statuses,
            trigger=IntervalTrigger(seconds=interval),
            id='poll_corporate_statuses',
            max_instances=1,
            replace_existing=True,
        )
        self.stdout.write(self.style.SUCCESS(
            f'Added job: poll_corporate_statuses (every {interval} seconds)'
        ))

        scheduler.add_job(
            delete_old_job_executions,
            trigger=IntervalTrigger(days=1),
            id='delete_old_job_executions',
            max_instances=1,
            replace_existing=True,
        )
        self.stdout.write('Added job: delete_old_job_executions (daily)')

        try:
            self.stdout.write(self.style.SUCCESS('Starting scheduler...'))
            scheduler.start()
        except KeyboardInterrupt:
            self.stdout.write('Stopping scheduler...')
            scheduler.shutdown()
            self.stdout.write(self.style.SUCCESS('Scheduler shut down successfully!'))
