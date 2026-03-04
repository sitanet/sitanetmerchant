from rest_framework import serializers
from .models import Corporate, Director, Wallet, Transaction


class DirectorSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Director
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class WalletSerializer(serializers.ModelSerializer):
    corporate_name = serializers.CharField(source='corporate.business_name', read_only=True)
    
    class Meta:
        model = Wallet
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class TransactionSerializer(serializers.ModelSerializer):
    wallet_account = serializers.CharField(source='wallet.account_number', read_only=True)
    
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class CorporateListSerializer(serializers.ModelSerializer):
    wallets_count = serializers.SerializerMethodField()
    directors_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Corporate
        fields = [
            'id', 'business_name', 'trading_name', 'business_type',
            'registration_number', 'email', 'phone_number', 'status',
            'wallets_count', 'directors_count', 'created_at'
        ]
    
    def get_wallets_count(self, obj):
        return obj.wallets.count()
    
    def get_directors_count(self, obj):
        return obj.directors.count()


class CorporateDetailSerializer(serializers.ModelSerializer):
    directors = DirectorSerializer(many=True, read_only=True)
    wallets = WalletSerializer(many=True, read_only=True)
    
    class Meta:
        model = Corporate
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']


class CorporateCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Corporate
        exclude = ['created_by', 'npsb_business_id', 'npsb_account_number', 'npsb_account_name', 'npsb_submission_status']


class CorporateSubmitSerializer(serializers.ModelSerializer):
    """Serializer for corporate account submission with documents"""
    
    class Meta:
        model = Corporate
        fields = [
            'tax_identification_number', 'business_name', 'email', 'phone_number',
            'address', 'industrial_sector', 'business_type', 'company_reg_date',
            'contact_person_first_name', 'contact_person_last_name', 'website',
            'date_incorporated', 'business_commencement_date', 'registration_number',
            'postal_code', 'cac_certificate', 'scuml_certificate', 'regulatory_license_fintech',
            'utility_bill', 'proof_of_address', 'memart', 'tin_certificate',
            'cac_status_report', 'board_resolution'
        ]


class DirectorSubmitSerializer(serializers.ModelSerializer):
    """Serializer for director submission with documents"""
    
    class Meta:
        model = Director
        fields = [
            'first_name', 'last_name', 'other_names', 'address', 'gender',
            'date_of_birth', 'email', 'phone_number', 'bvn', 'nin',
            'identification_type', 'nationality', 'other_nationality_type',
            'next_of_kin_name', 'next_of_kin_phone', 'pep', 'customer_type',
            'passport_photo', 'proof_of_address', 'id_card_front', 'id_card_back'
        ]


class CorporateStatusSerializer(serializers.Serializer):
    """Serializer for corporate status check"""
    tin = serializers.CharField(max_length=50)


class WalletGenerateSerializer(serializers.Serializer):
    director_id = serializers.UUIDField(required=False)


class CreditDebitSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    narration = serializers.CharField(max_length=255)


class TransferSerializer(serializers.Serializer):
    beneficiary_account = serializers.CharField(max_length=20)
    beneficiary_bank = serializers.CharField(max_length=10, required=False, allow_blank=True)
    beneficiary_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    narration = serializers.CharField(max_length=255)
    transfer_type = serializers.ChoiceField(choices=['internal', 'external'])


class NameEnquirySerializer(serializers.Serializer):
    bank_code = serializers.CharField(max_length=10)
    account_number = serializers.CharField(max_length=20)
