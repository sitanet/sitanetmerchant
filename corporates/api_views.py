from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

from .models import Corporate, Director, Wallet, Transaction
from .serializers import (
    CorporateListSerializer, CorporateDetailSerializer, CorporateCreateSerializer,
    CorporateSubmitSerializer, DirectorSubmitSerializer, CorporateStatusSerializer,
    DirectorSerializer, WalletSerializer, TransactionSerializer,
    WalletGenerateSerializer, CreditDebitSerializer, TransferSerializer,
    NameEnquirySerializer
)
from core.services import npsb_service, NPSBAPIError


class CorporateViewSet(viewsets.ModelViewSet):
    queryset = Corporate.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CorporateListSerializer
        elif self.action == 'create':
            return CorporateCreateSerializer
        return CorporateDetailSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def submit_corporate(self, request, pk=None):
        """Submit corporate account data to 9PSB for verification"""
        corporate = self.get_object()
        
        directors = corporate.directors.all()
        if not directors.exists():
            return Response({
                'status': 'error',
                'message': 'Corporate must have at least one director'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate required documents
        if not corporate.tax_identification_number:
            return Response({
                'status': 'error',
                'message': 'Tax Identification Number (TIN) is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not corporate.cac_certificate:
            return Response({
                'status': 'error',
                'message': 'CAC Certificate is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Set contact person from primary director if not set
        primary_director = directors.filter(is_primary=True).first() or directors.first()
        if not corporate.contact_person_first_name:
            corporate.contact_person_first_name = primary_director.first_name
            corporate.contact_person_last_name = primary_director.last_name
            corporate.save()
        
        try:
            response = npsb_service.submit_corporate_data(
                corporate=corporate,
                directors=list(directors)
            )
            
            if response.get('status') == 'SUCCESS':
                corporate.npsb_submission_status = 'PENDING'
                corporate.save()
                
                return Response({
                    'status': 'success',
                    'message': response.get('message', 'Corporate Account Request Submitted For Processing'),
                    'data': response.get('data', {})
                })
            else:
                return Response({
                    'status': 'failed',
                    'message': response.get('message', 'Failed to submit corporate data')
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except NPSBAPIError as e:
            return Response({
                'status': 'error',
                'message': e.message
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def update_corporate(self, request, pk=None):
        """Update corporate account data on 9PSB"""
        corporate = self.get_object()
        
        directors = corporate.directors.all()
        if not directors.exists():
            return Response({
                'status': 'error',
                'message': 'Corporate must have at least one director'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not corporate.tax_identification_number:
            return Response({
                'status': 'error',
                'message': 'Tax Identification Number (TIN) is required for update'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            response = npsb_service.update_corporate_data(
                corporate=corporate,
                directors=list(directors)
            )
            
            if response.get('status') == 'SUCCESS':
                return Response({
                    'status': 'success',
                    'message': response.get('message', 'Corporate Data Update Submitted For Processing')
                })
            else:
                return Response({
                    'status': 'failed',
                    'message': response.get('message', 'Failed to update corporate data')
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except NPSBAPIError as e:
            return Response({
                'status': 'error',
                'message': e.message
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def corporate_status(self, request, pk=None):
        """Check corporate account verification status from 9PSB"""
        corporate = self.get_object()
        
        if not corporate.tax_identification_number:
            return Response({
                'status': 'error',
                'message': 'Tax Identification Number (TIN) is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            response = npsb_service.get_corporate_status(corporate.tax_identification_number)
            
            if response.get('status') == 'SUCCESS':
                data = response.get('data', {})
                
                # Update local corporate status
                final_status = data.get('finalStatus')
                if final_status:
                    corporate.npsb_submission_status = final_status
                
                org_data = data.get('organization', {})
                if org_data:
                    corporate.npsb_account_number = org_data.get('accountNumber')
                    corporate.npsb_account_name = org_data.get('accountName')
                    if org_data.get('status') == 'APPROVED':
                        corporate.status = 'ACTIVE'
                
                corporate.save()
                
                # Update director statuses
                members = data.get('members', [])
                for member in members:
                    bvn = member.get('bvn')
                    director = directors.filter(bvn=bvn).first() if bvn else None
                    if director:
                        director.npsb_status = member.get('status')
                        director.npsb_declined_items = member.get('declinedItems')
                        director.save()
                
                # Create wallet if approved and no wallet exists
                if final_status == 'APPROVED' and org_data.get('accountNumber'):
                    wallet, created = Wallet.objects.get_or_create(
                        account_number=org_data.get('accountNumber'),
                        defaults={
                            'wallet_type': 'CORPORATE',
                            'corporate': corporate,
                            'account_name': org_data.get('accountName', corporate.business_name),
                            'status': 'ACTIVE'
                        }
                    )
                
                return Response({
                    'status': 'success',
                    'message': response.get('message'),
                    'data': data
                })
            else:
                return Response({
                    'status': 'failed',
                    'message': response.get('message', 'Failed to get corporate status')
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except NPSBAPIError as e:
            return Response({
                'status': 'error',
                'message': e.message
            }, status=status.HTTP_400_BAD_REQUEST)


class DirectorViewSet(viewsets.ModelViewSet):
    serializer_class = DirectorSerializer
    
    def get_queryset(self):
        corporate_id = self.kwargs.get('corporate_pk')
        if corporate_id:
            return Director.objects.filter(corporate_id=corporate_id)
        return Director.objects.all()
    
    def perform_create(self, serializer):
        corporate_id = self.kwargs.get('corporate_pk')
        corporate = get_object_or_404(Corporate, pk=corporate_id)
        serializer.save(corporate=corporate)


class WalletViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Wallet.objects.select_related('corporate').all()
    serializer_class = WalletSerializer
    
    @action(detail=True, methods=['get'])
    def balance(self, request, pk=None):
        """Get wallet balance from API"""
        wallet = self.get_object()
        
        try:
            response = npsb_service.wallet_enquiry(wallet.account_number)
            
            if response.get('status') == 'SUCCESS':
                data = response.get('data', {})
                wallet.available_balance = data.get('availableBalance', 0)
                wallet.ledger_balance = data.get('ledgerBalance', 0)
                wallet.save()
                
                return Response({
                    'status': 'success',
                    'available_balance': str(wallet.available_balance),
                    'ledger_balance': str(wallet.ledger_balance),
                    'data': data
                })
        except NPSBAPIError as e:
            return Response({
                'status': 'error',
                'message': e.message
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'status': 'error',
            'message': 'Failed to fetch balance'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def credit(self, request, pk=None):
        """Credit wallet"""
        wallet = self.get_object()
        serializer = CreditDebitSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            reference = npsb_service.generate_reference('CR')
            response = npsb_service.credit_wallet(
                account_no=wallet.account_number,
                amount=serializer.validated_data['amount'],
                narration=serializer.validated_data['narration'],
                transaction_id=reference
            )
            
            Transaction.objects.create(
                wallet=wallet,
                transaction_type='CREDIT',
                amount=serializer.validated_data['amount'],
                narration=serializer.validated_data['narration'],
                transaction_reference=reference,
                status='SUCCESS' if response.get('status') == 'SUCCESS' else 'FAILED',
                response_code=response.get('responseCode'),
                response_message=response.get('message')
            )
            
            return Response({
                'status': response.get('status', 'PENDING'),
                'message': response.get('message'),
                'reference': reference
            })
            
        except NPSBAPIError as e:
            return Response({
                'status': 'error',
                'message': e.message
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def debit(self, request, pk=None):
        """Debit wallet"""
        wallet = self.get_object()
        serializer = CreditDebitSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            reference = npsb_service.generate_reference('DR')
            response = npsb_service.debit_wallet(
                account_no=wallet.account_number,
                amount=serializer.validated_data['amount'],
                narration=serializer.validated_data['narration'],
                transaction_id=reference
            )
            
            Transaction.objects.create(
                wallet=wallet,
                transaction_type='DEBIT',
                amount=serializer.validated_data['amount'],
                narration=serializer.validated_data['narration'],
                transaction_reference=reference,
                status='SUCCESS' if response.get('status') == 'SUCCESS' else 'FAILED',
                response_code=response.get('responseCode'),
                response_message=response.get('message')
            )
            
            return Response({
                'status': response.get('status', 'PENDING'),
                'message': response.get('message'),
                'reference': reference
            })
            
        except NPSBAPIError as e:
            return Response({
                'status': 'error',
                'message': e.message
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def transfer(self, request, pk=None):
        """Transfer from wallet"""
        wallet = self.get_object()
        serializer = TransferSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            reference = npsb_service.generate_reference('TRF')
            
            if data['transfer_type'] == 'external':
                response = npsb_service.transfer_to_other_bank(
                    sender_account=wallet.account_number,
                    sender_name=wallet.account_name,
                    beneficiary_account=data['beneficiary_account'],
                    beneficiary_bank=data.get('beneficiary_bank', ''),
                    beneficiary_name=data.get('beneficiary_name', ''),
                    amount=data['amount'],
                    narration=data['narration'],
                    reference=reference
                )
            else:
                response = npsb_service.debit_wallet(
                    account_no=wallet.account_number,
                    amount=data['amount'],
                    narration=f"Transfer to {data['beneficiary_account']}: {data['narration']}",
                    transaction_id=reference
                )
            
            Transaction.objects.create(
                wallet=wallet,
                transaction_type='TRANSFER',
                amount=data['amount'],
                narration=data['narration'],
                transaction_reference=reference,
                beneficiary_account=data['beneficiary_account'],
                beneficiary_bank=data.get('beneficiary_bank'),
                beneficiary_name=data.get('beneficiary_name'),
                status='SUCCESS' if response.get('status') == 'SUCCESS' else 'PENDING',
                response_code=response.get('responseCode'),
                response_message=response.get('message')
            )
            
            return Response({
                'status': response.get('status', 'PENDING'),
                'message': response.get('message'),
                'reference': reference
            })
            
        except NPSBAPIError as e:
            return Response({
                'status': 'error',
                'message': e.message
            }, status=status.HTTP_400_BAD_REQUEST)


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Transaction.objects.select_related('wallet', 'wallet__corporate').all()
    serializer_class = TransactionSerializer
    
    @action(detail=True, methods=['post'])
    def requery(self, request, pk=None):
        """Requery transaction status"""
        txn = self.get_object()
        
        try:
            response = npsb_service.requery_transaction(
                transaction_id=txn.transaction_reference,
                amount=float(txn.amount),
                account_no=txn.wallet.account_number
            )
            
            if response.get('status') == 'SUCCESS':
                data = response.get('data', {})
                txn.status = data.get('status', txn.status)
                txn.response_code = data.get('responseCode')
                txn.response_message = data.get('responseMessage')
                txn.save()
            
            return Response({
                'status': 'success',
                'transaction_status': txn.status,
                'data': response.get('data')
            })
            
        except NPSBAPIError as e:
            return Response({
                'status': 'error',
                'message': e.message
            }, status=status.HTTP_400_BAD_REQUEST)


class NameEnquiryView(APIView):
    """Name enquiry for other banks"""
    
    def post(self, request):
        serializer = NameEnquirySerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            response = npsb_service.other_banks_enquiry(
                bank_code=serializer.validated_data['bank_code'],
                account_number=serializer.validated_data['account_number']
            )
            
            if response.get('status') == 'SUCCESS':
                data = response.get('data', {})
                return Response({
                    'status': 'success',
                    'account_name': data.get('accountName', data.get('name', '')),
                    'data': data
                })
                
        except NPSBAPIError as e:
            return Response({
                'status': 'error',
                'message': e.message
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'status': 'error',
            'message': 'Account not found'
        }, status=status.HTTP_404_NOT_FOUND)


@method_decorator(csrf_exempt, name='dispatch')
class CorporateVerificationWebhookView(APIView):
    """
    Webhook handler for 9PSB corporate verification notifications.
    This endpoint receives approval/decline notifications from 9PSB.
    
    Configure in settings.py:
        WEBHOOK_USERNAME = 'your-webhook-username'
        WEBHOOK_PASSWORD = 'your-webhook-password'
    """
    authentication_classes = []  # Disable DRF authentication for webhook
    permission_classes = []  # Disable permission checks for webhook
    
    def verify_basic_auth(self, request):
        """Verify Basic Authentication from 9PSB webhook"""
        from django.conf import settings
        import base64
        
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Basic '):
            return False
        
        try:
            encoded_credentials = auth_header.split(' ')[1]
            decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
            username, password = decoded_credentials.split(':')
            
            expected_username = getattr(settings, 'WEBHOOK_USERNAME', '')
            expected_password = getattr(settings, 'WEBHOOK_PASSWORD', '')
            
            # If no credentials configured, skip verification (development mode)
            if not expected_username and not expected_password:
                return True
            
            return username == expected_username and password == expected_password
        except Exception:
            return False
    
    def post(self, request):
        """
        Handle corporate verification webhook from 9PSB.
        
        Expected payload:
        {
            "finalStatus": "APPROVED" or "DECLINED",
            "channel": "YOUR_CHANNEL",
            "organization": {
                "status": "APPROVED" or "DECLINED",
                "tin": "12345678-0001",
                "accountNumber": "1100076507",
                "accountName": "CHANNEL/Company Name",
                "declinedItems": {}
            },
            "members": [
                {
                    "bvn": "22222222222",
                    "name": "Director Name",
                    "type": "DIRECTOR",
                    "status": "APPROVED" or "DECLINED",
                    "declinedItems": {}
                }
            ]
        }
        """
        # Verify Basic Auth
        if not self.verify_basic_auth(request):
            return Response({
                'status': 'error',
                'message': 'Unauthorized'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            data = request.data
            event_type = request.query_params.get('event')
            
            if event_type != 'corporate-verification':
                return Response({'status': 'ignored', 'message': 'Unknown event type'})
            
            final_status = data.get('finalStatus')
            org_data = data.get('organization', {})
            members = data.get('members', [])
            
            tin = org_data.get('tin')
            if not tin:
                return Response({
                    'status': 'error',
                    'message': 'TIN not provided'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Find corporate by TIN
            corporate = Corporate.objects.filter(tax_identification_number=tin).first()
            if not corporate:
                return Response({
                    'status': 'error',
                    'message': 'Corporate not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Update corporate status
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
            elif final_status == 'DECLINED':
                corporate.status = 'PENDING'
            
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
            
            return Response({
                'status': 'success',
                'message': 'Webhook processed successfully'
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
