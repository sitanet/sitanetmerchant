"""
9PSB Wallet As A Service API Integration
"""
import requests
import logging
from datetime import datetime
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class NPSBAPIError(Exception):
    """Custom exception for 9PSB API errors"""
    def __init__(self, message, response_code=None, data=None):
        self.message = message
        self.response_code = response_code
        self.data = data
        super().__init__(self.message)


class NPSBService:
    """9PSB Wallet As A Service API Client"""
    
    # Request timeout in seconds (connect timeout, read timeout)
    DEFAULT_TIMEOUT = (10, 30)
    
    def __init__(self):
        self.base_url = settings.NPSB_BASE_URL
        self.username = settings.NPSB_USERNAME
        self.password = settings.NPSB_PASSWORD
        self.client_id = settings.NPSB_CLIENT_ID
        self.client_secret = settings.NPSB_CLIENT_SECRET
        self._token = None
    
    @property
    def token(self):
        """Get cached token or authenticate"""
        cached_token = cache.get('npsb_access_token')
        if cached_token:
            return cached_token
        return self.authenticate()
    
    def _get_headers(self, include_auth=True):
        """Get request headers"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        if include_auth:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers
    
    def _handle_response(self, response):
        """Handle API response"""
        try:
            data = response.json()
        except ValueError:
            raise NPSBAPIError("Invalid JSON response from API")
        
        if data.get('status') == 'FAILED':
            raise NPSBAPIError(
                message=data.get('message', 'API request failed'),
                response_code=data.get('responseCode'),
                data=data
            )
        
        return data
    
    def authenticate(self):
        """Authenticate and get access token"""
        url = f"{self.base_url}/api/v1/authenticate"
        payload = {
            "username": self.username,
            "password": self.password,
            "clientId": self.client_id,
            "clientSecret": self.client_secret
        }
        
        logger.info(f"Authenticating with 9PSB API at {url}")
        logger.debug(f"Auth payload (username: {self.username}, clientId: {self.client_id})")
        
        try:
            response = requests.post(url, json=payload, headers=self._get_headers(include_auth=False), timeout=self.DEFAULT_TIMEOUT)
            
            logger.info(f"Auth response status code: {response.status_code}")
            logger.info(f"Auth response body: {response.text}")
            
            data = self._handle_response(response)
            
            if data.get('message') == 'successful':
                token = data.get('accessToken')
                expires_in = int(data.get('expiresIn', 3600))
                cache.set('npsb_access_token', token, timeout=expires_in - 60)
                logger.info("Authentication successful, token cached")
                return token
            else:
                logger.error(f"Authentication failed. Response: {data}")
                raise NPSBAPIError("Authentication failed", data=data)
                
        except requests.RequestException as e:
            logger.error(f"Authentication connection error: {str(e)}")
            raise NPSBAPIError(f"Connection error: {str(e)}")
    
    def generate_reference(self, prefix='TXN'):
        """Generate unique transaction reference"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')[:17]
        return f"{prefix}{timestamp}"
    
    # ==================== WALLET OPERATIONS ====================
    
    def open_wallet(self, data):
        """
        Open a new individual wallet
        
        Args:
            data: dict with bvn, dateOfBirth, gender, lastName, otherNames, 
                  phoneNo, transactionTrackingRef, placeOfBirth, address,
                  nationalIdentityNo, nextOfKinPhoneNo, nextOfKinName, email
        """
        url = f"{self.base_url}/api/v1/open_wallet"
        
        try:
            response = requests.post(url, json=data, headers=self._get_headers())
            return self._handle_response(response)
        except requests.RequestException as e:
            logger.error(f"Open wallet error: {str(e)}")
            raise NPSBAPIError(f"Connection error: {str(e)}")
    
    def submit_corporate_data(self, corporate, directors):
        """
        Submit corporate account data with documents (multipart form-data)
        
        Args:
            corporate: Corporate model instance
            directors: list of Director model instances
        """
        url = f"{self.base_url}/api/v1/corporates/submit"
        
        files = {}
        data = {}
        
        # Corporate data
        data['taxIDNo'] = corporate.tax_identification_number or ''
        data['businessName'] = corporate.business_name
        data['email'] = corporate.email
        data['phoneNo'] = corporate.phone_number
        data['address'] = corporate.address
        data['industrialSector'] = corporate.industrial_sector or 'OTHERS'
        data['businessType'] = corporate.business_type
        data['companyRegDate'] = corporate.company_reg_date.strftime('%Y-%m-%d') if corporate.company_reg_date else corporate.date_incorporated.strftime('%Y-%m-%d')
        data['contactPersonFirstName'] = corporate.contact_person_first_name or ''
        data['contactPersonLastName'] = corporate.contact_person_last_name or ''
        data['webAddress'] = corporate.website or ''
        data['dateIncorporated'] = corporate.date_incorporated.strftime('%Y-%m-%d')
        data['businessCommencementDate'] = corporate.business_commencement_date.strftime('%Y-%m-%d') if corporate.business_commencement_date else corporate.date_incorporated.strftime('%Y-%m-%d')
        data['registrationNumber'] = corporate.registration_number
        data['postalAddress'] = corporate.postal_code or corporate.address
        
        # Corporate documents
        if corporate.cac_certificate:
            files['cacCertificate'] = (corporate.cac_certificate.name, corporate.cac_certificate.file, 'application/pdf')
        if corporate.scuml_certificate:
            files['scumlCertificate'] = (corporate.scuml_certificate.name, corporate.scuml_certificate.file, 'application/pdf')
        if corporate.regulatory_license_fintech:
            files['regulatoryLicenseFintech'] = (corporate.regulatory_license_fintech.name, corporate.regulatory_license_fintech.file, 'application/pdf')
        if corporate.utility_bill:
            files['utilityBill'] = (corporate.utility_bill.name, corporate.utility_bill.file, 'application/pdf')
        if corporate.proof_of_address:
            files['proofOfAddressVerification'] = (corporate.proof_of_address.name, corporate.proof_of_address.file, 'application/pdf')
        if corporate.memart:
            files['memart'] = (corporate.memart.name, corporate.memart.file, 'application/pdf')
        if corporate.tin_certificate:
            files['tinCertificate'] = (corporate.tin_certificate.name, corporate.tin_certificate.file, 'application/pdf')
        if corporate.cac_status_report:
            files['cacOrStatusReport'] = (corporate.cac_status_report.name, corporate.cac_status_report.file, 'application/pdf')
        if corporate.board_resolution:
            files['letterOfBoardResolution'] = (corporate.board_resolution.name, corporate.board_resolution.file, 'application/pdf')
        
        # Directors data
        for i, director in enumerate(directors):
            data[f'directors[{i}].firstName'] = director.first_name
            data[f'directors[{i}].lastName'] = director.last_name
            data[f'directors[{i}].otherNames'] = director.other_names or ''
            data[f'directors[{i}].address'] = director.address
            data[f'directors[{i}].gender'] = director.gender
            data[f'directors[{i}].dateOfBirth'] = director.date_of_birth.strftime('%Y-%m-%d')
            data[f'directors[{i}].email'] = director.email
            data[f'directors[{i}].phoneNo'] = director.phone_number
            data[f'directors[{i}].bankVerificationNumber'] = director.bvn
            data[f'directors[{i}].nationalIdentityNo'] = director.nin or ''
            data[f'directors[{i}].identificationType'] = director.identification_type
            data[f'directors[{i}].nationality'] = director.nationality
            data[f'directors[{i}].otherNationalityType'] = director.other_nationality_type or ''
            data[f'directors[{i}].nextOfKinName'] = director.next_of_kin_name
            data[f'directors[{i}].nextOfKinPhoneNumber'] = director.next_of_kin_phone
            data[f'directors[{i}].pep'] = 'YES' if director.pep else 'NO'
            
            # Director documents
            if director.passport_photo:
                files[f'directors[{i}].passportPhoto'] = (director.passport_photo.name, director.passport_photo.file, 'image/jpeg')
            if director.proof_of_address:
                files[f'directors[{i}].proofOfAddressVerification'] = (director.proof_of_address.name, director.proof_of_address.file, 'application/pdf')
            if director.id_card_front:
                files[f'directors[{i}].idCardFront'] = (director.id_card_front.name, director.id_card_front.file, 'application/pdf')
            if director.id_card_back:
                files[f'directors[{i}].idCardBack'] = (director.id_card_back.name, director.id_card_back.file, 'application/pdf')
        
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.post(url, data=data, files=files, headers=headers)
            return self._handle_response(response)
        except requests.RequestException as e:
            logger.error(f"Submit corporate data error: {str(e)}")
            raise NPSBAPIError(f"Connection error: {str(e)}")
    
    def update_corporate_data(self, corporate, directors):
        """
        Update corporate account data with documents (multipart form-data)
        """
        url = f"{self.base_url}/api/v1/corporates/update"
        
        files = {}
        data = {}
        
        # TIN is required for update
        data['taxIDNo'] = corporate.tax_identification_number or ''
        
        # Add other fields same as submit...
        data['businessName'] = corporate.business_name
        data['email'] = corporate.email
        data['phoneNo'] = corporate.phone_number
        data['address'] = corporate.address
        data['industrialSector'] = corporate.industrial_sector or 'OTHERS'
        data['businessType'] = corporate.business_type
        data['companyRegDate'] = corporate.company_reg_date.strftime('%Y-%m-%d') if corporate.company_reg_date else corporate.date_incorporated.strftime('%Y-%m-%d')
        data['contactPersonFirstName'] = corporate.contact_person_first_name or ''
        data['contactPersonLastName'] = corporate.contact_person_last_name or ''
        data['webAddress'] = corporate.website or ''
        data['dateIncorporated'] = corporate.date_incorporated.strftime('%Y-%m-%d')
        data['businessCommencementDate'] = corporate.business_commencement_date.strftime('%Y-%m-%d') if corporate.business_commencement_date else corporate.date_incorporated.strftime('%Y-%m-%d')
        data['registrationNumber'] = corporate.registration_number
        
        # Corporate documents
        if corporate.cac_certificate:
            files['cacCertificate'] = (corporate.cac_certificate.name, corporate.cac_certificate.file, 'application/pdf')
        if corporate.scuml_certificate:
            files['scumlCertificate'] = (corporate.scuml_certificate.name, corporate.scuml_certificate.file, 'application/pdf')
        if corporate.regulatory_license_fintech:
            files['regulatoryLicenseFintech'] = (corporate.regulatory_license_fintech.name, corporate.regulatory_license_fintech.file, 'application/pdf')
        if corporate.utility_bill:
            files['utilityBill'] = (corporate.utility_bill.name, corporate.utility_bill.file, 'application/pdf')
        if corporate.proof_of_address:
            files['proofOfAddressVerification'] = (corporate.proof_of_address.name, corporate.proof_of_address.file, 'application/pdf')
        if corporate.memart:
            files['memart'] = (corporate.memart.name, corporate.memart.file, 'application/pdf')
        if corporate.tin_certificate:
            files['tinCertificate'] = (corporate.tin_certificate.name, corporate.tin_certificate.file, 'application/pdf')
        if corporate.cac_status_report:
            files['cacOrStatusReport'] = (corporate.cac_status_report.name, corporate.cac_status_report.file, 'application/pdf')
        if corporate.board_resolution:
            files['letterOfBoardResolution'] = (corporate.board_resolution.name, corporate.board_resolution.file, 'application/pdf')
        
        # Directors data
        for i, director in enumerate(directors):
            data[f'directors[{i}].firstName'] = director.first_name
            data[f'directors[{i}].lastName'] = director.last_name
            data[f'directors[{i}].otherNames'] = director.other_names or ''
            data[f'directors[{i}].address'] = director.address
            data[f'directors[{i}].gender'] = director.gender
            data[f'directors[{i}].dateOfBirth'] = director.date_of_birth.strftime('%Y-%m-%d')
            data[f'directors[{i}].email'] = director.email
            data[f'directors[{i}].phoneNo'] = director.phone_number
            data[f'directors[{i}].bankVerificationNumber'] = director.bvn
            data[f'directors[{i}].nationalIdentityNo'] = director.nin or ''
            data[f'directors[{i}].identificationType'] = director.identification_type
            data[f'directors[{i}].nationality'] = director.nationality
            data[f'directors[{i}].otherNationalityType'] = director.other_nationality_type or ''
            data[f'directors[{i}].nextOfKinName'] = director.next_of_kin_name
            data[f'directors[{i}].nextOfKinPhoneNumber'] = director.next_of_kin_phone
            data[f'directors[{i}].pep'] = 'YES' if director.pep else 'NO'
            
            # Director documents
            if director.passport_photo:
                files[f'directors[{i}].passportPhoto'] = (director.passport_photo.name, director.passport_photo.file, 'image/jpeg')
            if director.proof_of_address:
                files[f'directors[{i}].proofOfAddressVerification'] = (director.proof_of_address.name, director.proof_of_address.file, 'application/pdf')
            if director.id_card_front:
                files[f'directors[{i}].idCardFront'] = (director.id_card_front.name, director.id_card_front.file, 'application/pdf')
            if director.id_card_back:
                files[f'directors[{i}].idCardBack'] = (director.id_card_back.name, director.id_card_back.file, 'application/pdf')
        
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.post(url, data=data, files=files, headers=headers)
            return self._handle_response(response)
        except requests.RequestException as e:
            logger.error(f"Update corporate data error: {str(e)}")
            raise NPSBAPIError(f"Connection error: {str(e)}")
    
    def get_corporate_status(self, tin):
        """
        Get corporate account verification status by TIN
        """
        url = f"{self.base_url}/api/v1/corporates/status"
        params = {'tin': tin}
        
        try:
            response = requests.get(url, params=params, headers=self._get_headers(), timeout=self.DEFAULT_TIMEOUT)
            return self._handle_response(response)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            logger.error(f"Get corporate status connection error: {str(e)}")
            raise  # Re-raise to allow retry at caller level
        except requests.RequestException as e:
            logger.error(f"Get corporate status error: {str(e)}")
            raise NPSBAPIError(f"Connection error: {str(e)}")
    
    def get_wallet_by_bvn(self, bvn):
        """Get wallet details by BVN"""
        url = f"{self.base_url}/api/v1/get_wallet"
        payload = {"bvn": bvn}
        
        try:
            response = requests.post(url, json=payload, headers=self._get_headers())
            return self._handle_response(response)
        except requests.RequestException as e:
            logger.error(f"Get wallet error: {str(e)}")
            raise NPSBAPIError(f"Connection error: {str(e)}")
    
    def wallet_enquiry(self, account_no):
        """Get wallet details and balance"""
        url = f"{self.base_url}/api/v1/wallet_enquiry"
        payload = {"accountNo": account_no}
        
        try:
            response = requests.post(url, json=payload, headers=self._get_headers())
            return self._handle_response(response)
        except requests.RequestException as e:
            logger.error(f"Wallet enquiry error: {str(e)}")
            raise NPSBAPIError(f"Connection error: {str(e)}")
    
    def wallet_status(self, account_no):
        """Check wallet status"""
        url = f"{self.base_url}/api/v1/wallet_status"
        payload = {"accountNo": account_no}
        
        try:
            response = requests.post(url, json=payload, headers=self._get_headers())
            return self._handle_response(response)
        except requests.RequestException as e:
            logger.error(f"Wallet status error: {str(e)}")
            raise NPSBAPIError(f"Connection error: {str(e)}")
    
    # ==================== TRANSFER OPERATIONS ====================
    
    def credit_wallet(self, account_no, amount, narration, transaction_id=None, merchant_fee=None):
        """Credit a wallet"""
        url = f"{self.base_url}/api/v1/credit/transfer"
        
        payload = {
            "accountNo": account_no,
            "narration": narration,
            "totalAmount": float(amount),
            "transactionId": transaction_id or self.generate_reference('CR'),
            "merchant": {
                "isFee": bool(merchant_fee),
                "merchantFeeAccount": merchant_fee.get('account', '') if merchant_fee else '',
                "merchantFeeAmount": str(merchant_fee.get('amount', '')) if merchant_fee else ''
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=self._get_headers())
            return self._handle_response(response)
        except requests.RequestException as e:
            logger.error(f"Credit wallet error: {str(e)}")
            raise NPSBAPIError(f"Connection error: {str(e)}")
    
    def debit_wallet(self, account_no, amount, narration, transaction_id=None, merchant_fee=None):
        """Debit a wallet"""
        url = f"{self.base_url}/api/v1/debit/transfer"
        
        payload = {
            "accountNo": account_no,
            "narration": narration,
            "totalAmount": float(amount),
            "transactionId": transaction_id or self.generate_reference('DR'),
            "merchant": {
                "isFee": bool(merchant_fee),
                "merchantFeeAccount": merchant_fee.get('account', '') if merchant_fee else '',
                "merchantFeeAmount": str(merchant_fee.get('amount', '')) if merchant_fee else ''
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=self._get_headers())
            return self._handle_response(response)
        except requests.RequestException as e:
            logger.error(f"Debit wallet error: {str(e)}")
            raise NPSBAPIError(f"Connection error: {str(e)}")
    
    def other_banks_enquiry(self, bank_code, account_number):
        """Name enquiry for other banks"""
        url = f"{self.base_url}/api/v1/other_banks_enquiry"
        
        payload = {
            "customer": {
                "account": {
                    "bank": bank_code,
                    "number": account_number
                }
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=self._get_headers())
            return self._handle_response(response)
        except requests.RequestException as e:
            logger.error(f"Other banks enquiry error: {str(e)}")
            raise NPSBAPIError(f"Connection error: {str(e)}")
    
    def transfer_to_other_bank(self, sender_account, sender_name, beneficiary_account, 
                                beneficiary_bank, beneficiary_name, amount, narration,
                                reference=None, merchant_fee=None):
        """Transfer to other banks"""
        url = f"{self.base_url}/api/v1/wallet_other_banks"
        
        payload = {
            "customer": {
                "account": {
                    "bank": beneficiary_bank,
                    "name": beneficiary_name,
                    "number": beneficiary_account,
                    "senderaccountnumber": sender_account,
                    "sendername": sender_name
                }
            },
            "narration": narration,
            "order": {
                "amount": str(amount),
                "country": "NGA",
                "currency": "NGN",
                "description": narration
            },
            "transaction": {
                "reference": reference or self.generate_reference('TRF')
            },
            "merchant": {
                "isFee": bool(merchant_fee),
                "merchantFeeAccount": merchant_fee.get('account', '') if merchant_fee else '',
                "merchantFeeAmount": str(merchant_fee.get('amount', '')) if merchant_fee else ''
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=self._get_headers())
            return self._handle_response(response)
        except requests.RequestException as e:
            logger.error(f"Transfer error: {str(e)}")
            raise NPSBAPIError(f"Connection error: {str(e)}")
    
    def requery_transaction(self, transaction_id, amount=None, transaction_type=None, 
                           transaction_date=None, account_no=None):
        """Requery transaction status"""
        url = f"{self.base_url}/api/v1/wallet_requery"
        
        payload = {"transactionId": transaction_id}
        if amount:
            payload["amount"] = float(amount)
        if transaction_type:
            payload["transactionType"] = transaction_type
        if transaction_date:
            payload["transactionDate"] = transaction_date
        if account_no:
            payload["accountNo"] = account_no
        
        try:
            response = requests.post(url, json=payload, headers=self._get_headers())
            return self._handle_response(response)
        except requests.RequestException as e:
            logger.error(f"Requery error: {str(e)}")
            raise NPSBAPIError(f"Connection error: {str(e)}")


# Singleton instance
npsb_service = NPSBService()
