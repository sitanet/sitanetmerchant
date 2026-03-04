"""
CheckMyNINBVN API Integration for NIN/BVN Verification
https://checkmyninbvn.com.ng/documentation
"""
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

BASE_URL = "https://checkmyninbvn.com.ng/api"


class VerificationError(Exception):
    """Custom exception for verification errors"""
    def __init__(self, message, code=None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class CheckMyNINBVNService:
    """CheckMyNINBVN API Client for NIN/BVN verification"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'CHECKMYNINBVN_API_KEY', '')
    
    def _get_headers(self):
        return {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key
        }
    
    def _make_request(self, endpoint, payload):
        """Make API request"""
        if not self.api_key:
            raise VerificationError("CheckMyNINBVN API key not configured")
        
        url = f"{BASE_URL}/{endpoint}"
        
        try:
            response = requests.post(url, json=payload, headers=self._get_headers(), timeout=30)
            data = response.json()
            
            print(f"===== API Response from {endpoint} =====")
            print(f"Full response: {data}")
            print(f"Data field: {data.get('data')}")
            print("=========================================")
            
            if data.get('status') == 'success':
                return data
            else:
                raise VerificationError(
                    message=data.get('message', 'Verification failed'),
                    code=data.get('code', response.status_code)
                )
                
        except requests.RequestException as e:
            logger.error(f"Verification API error: {str(e)}")
            raise VerificationError(f"Connection error: {str(e)}")
    
    def verify_bvn(self, bvn):
        """
        Verify BVN and return personal details
        
        Returns:
            dict with firstname, middlename, lastname, phone, email, dob, gender, 
            state_of_origin, state_of_residence, photo (base64)
        """
        payload = {
            "bvn": bvn,
            "consent": True
        }
        
        response = self._make_request("bvn-verification", payload)
        data = response.get('data', {})
        # API returns nested data.data structure
        if isinstance(data, dict) and 'data' in data:
            data = data.get('data', {})
        return data
    
    def verify_nin(self, nin):
        """
        Verify NIN and return personal details
        
        Returns:
            dict with firstname, middlename, surname, telephoneno, gender,
            birthdate, birthstate, residence_address, photo (base64)
        """
        payload = {
            "nin": nin,
            "consent": True
        }
        
        response = self._make_request("nin-verification", payload)
        data = response.get('data', {})
        # API may return nested data.data structure
        if isinstance(data, dict) and 'data' in data:
            data = data.get('data', {})
        return data
    
    def get_balance(self):
        """Check API wallet balance"""
        if not self.api_key:
            raise VerificationError("CheckMyNINBVN API key not configured")
        
        url = f"{BASE_URL}/balance"
        
        try:
            response = requests.get(url, headers=self._get_headers(), timeout=30)
            data = response.json()
            
            if data.get('status') == 'success':
                return data.get('data', {})
            else:
                raise VerificationError(data.get('message', 'Failed to get balance'))
                
        except requests.RequestException as e:
            raise VerificationError(f"Connection error: {str(e)}")


# Singleton instance
verification_service = CheckMyNINBVNService()
