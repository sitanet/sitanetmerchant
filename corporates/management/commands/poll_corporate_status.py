"""
Management command to poll 9PSB for pending corporate account statuses.
Runs every 3 minutes to check if any pending corporate accounts have been approved/declined.

Usage:
    python manage.py poll_corporate_status          # Run once
    python manage.py poll_corporate_status --daemon # Run continuously every 3 minutes
"""
import time
import logging
import requests
from django.core.management.base import BaseCommand
from corporates.models import Corporate, Wallet
from core.services import npsb_service, NPSBAPIError

logger = logging.getLogger(__name__)

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 10  # seconds


class Command(BaseCommand):
    help = 'Poll 9PSB for pending corporate account statuses'

    def add_arguments(self, parser):
        parser.add_argument(
            '--daemon',
            action='store_true',
            help='Run continuously every 3 minutes',
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=180,
            help='Polling interval in seconds (default: 180 = 3 minutes)',
        )

    def handle(self, *args, **options):
        daemon = options['daemon']
        interval = options['interval']

        if daemon:
            self.stdout.write(self.style.SUCCESS(
                f'Starting corporate status polling daemon (interval: {interval}s)...'
            ))
            while True:
                try:
                    self.poll_pending_corporates()
                except Exception as e:
                    logger.error(f'Polling error: {e}')
                    self.stdout.write(self.style.ERROR(f'Polling error: {e}'))
                time.sleep(interval)
        else:
            self.poll_pending_corporates()

    def poll_pending_corporates(self):
        """Check status of all pending corporate accounts from 9PSB"""
        pending_corporates = Corporate.objects.filter(
            npsb_submission_status='PENDING',
            tax_identification_number__isnull=False
        ).exclude(tax_identification_number='')

        if not pending_corporates.exists():
            self.stdout.write('No pending corporate accounts to check.')
            return

        self.stdout.write(f'Checking {pending_corporates.count()} pending corporate account(s)...')

        for corporate in pending_corporates:
            try:
                self.check_corporate_status(corporate)
            except Exception as e:
                logger.error(f'Error checking {corporate.business_name}: {e}')
                self.stdout.write(self.style.WARNING(
                    f'Error checking {corporate.business_name}: {e}'
                ))

    def check_corporate_status(self, corporate):
        """Check and update status for a single corporate account with retry logic"""
        self.stdout.write(f'Checking: {corporate.business_name} (TIN: {corporate.tax_identification_number})')

        response = None
        for attempt in range(MAX_RETRIES):
            try:
                response = npsb_service.get_corporate_status(corporate.tax_identification_number)
                break  # Success, exit retry loop
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                if attempt < MAX_RETRIES - 1:
                    self.stdout.write(self.style.WARNING(
                        f'  Connection error (attempt {attempt + 1}/{MAX_RETRIES}): {e}'
                    ))
                    self.stdout.write(f'  Retrying in {RETRY_DELAY} seconds...')
                    time.sleep(RETRY_DELAY)
                else:
                    self.stdout.write(self.style.ERROR(
                        f'  Failed after {MAX_RETRIES} attempts. Network issue with 9PSB API.'
                    ))
                    return
            except NPSBAPIError as e:
                self.stdout.write(self.style.WARNING(f'  API Error: {e.message}'))
                return

        if response is None:
            return

        try:
            if response.get('status') != 'SUCCESS':
                self.stdout.write(self.style.WARNING(
                    f'  API returned: {response.get("message", "Unknown error")}'
                ))
                return

            data = response.get('data', {})
            final_status = data.get('finalStatus')
            org_data = data.get('organization', {})
            members = data.get('members', [])

            if final_status and final_status != corporate.npsb_submission_status:
                corporate.npsb_submission_status = final_status
                corporate.npsb_account_number = org_data.get('accountNumber')
                corporate.npsb_account_name = org_data.get('accountName')

                if final_status == 'APPROVED':
                    corporate.status = 'ACTIVE'
                    
                    # Create wallet if account number provided
                    if org_data.get('accountNumber'):
                        wallet, created = Wallet.objects.get_or_create(
                            account_number=org_data.get('accountNumber'),
                            defaults={
                                'wallet_type': 'CORPORATE',
                                'corporate': corporate,
                                'account_name': org_data.get('accountName', corporate.business_name),
                                'status': 'ACTIVE'
                            }
                        )
                        if created:
                            self.stdout.write(self.style.SUCCESS(
                                f'  Created wallet: {wallet.account_number}'
                            ))

                    self.stdout.write(self.style.SUCCESS(
                        f'  APPROVED! Account: {corporate.npsb_account_number}'
                    ))
                elif final_status == 'DECLINED':
                    self.stdout.write(self.style.ERROR(
                        f'  DECLINED - {org_data.get("declinedItems", {})}'
                    ))
                else:
                    self.stdout.write(f'  Status changed to: {final_status}')

                corporate.save()

                # Update director statuses
                for member in members:
                    bvn = member.get('bvn')
                    if bvn:
                        director = corporate.directors.filter(bvn=bvn).first()
                        if director:
                            director.npsb_status = member.get('status')
                            director.npsb_declined_items = member.get('declinedItems')
                            director.save()
            else:
                self.stdout.write(f'  Still {final_status or "PENDING"} - no change')

        except NPSBAPIError as e:
            logger.error(f'9PSB API error for {corporate.business_name}: {e.message}')
            self.stdout.write(self.style.WARNING(f'  API Error: {e.message}'))
