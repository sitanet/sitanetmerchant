"""
Background tasks for corporate account management.
"""
import logging
from corporates.models import Corporate, Wallet
from core.services import npsb_service, NPSBAPIError

logger = logging.getLogger(__name__)


def poll_pending_corporate_statuses():
    """
    Poll 9PSB for all pending corporate account statuses.
    This is called by APScheduler every 3 minutes.
    """
    pending_corporates = Corporate.objects.filter(
        npsb_submission_status='PENDING',
        tax_identification_number__isnull=False
    ).exclude(tax_identification_number='')

    if not pending_corporates.exists():
        logger.debug('No pending corporate accounts to check')
        return

    logger.info(f'Polling {pending_corporates.count()} pending corporate account(s)...')

    for corporate in pending_corporates:
        try:
            check_and_update_corporate_status(corporate)
        except Exception as e:
            logger.error(f'Error checking {corporate.business_name}: {e}')


def check_and_update_corporate_status(corporate):
    """Check and update status for a single corporate account from 9PSB"""
    logger.info(f'Checking status for: {corporate.business_name}')

    try:
        response = npsb_service.get_corporate_status(corporate.tax_identification_number)

        if response.get('status') != 'SUCCESS':
            logger.warning(f'API returned non-success for {corporate.business_name}: {response.get("message")}')
            return False

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
                        logger.info(f'Created wallet {wallet.account_number} for {corporate.business_name}')

                logger.info(f'{corporate.business_name} APPROVED! Account: {corporate.npsb_account_number}')
            
            elif final_status == 'DECLINED':
                logger.warning(f'{corporate.business_name} DECLINED - {org_data.get("declinedItems", {})}')
            else:
                logger.info(f'{corporate.business_name} status changed to: {final_status}')

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
            
            return True
        else:
            logger.debug(f'{corporate.business_name} still {final_status or "PENDING"} - no change')
            return False

    except NPSBAPIError as e:
        logger.error(f'9PSB API error for {corporate.business_name}: {e.message}')
        return False
