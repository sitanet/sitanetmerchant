from django import forms
from .models import Corporate, Director, Wallet, Customer


class CustomerForm(forms.ModelForm):
    """Form for creating/editing Individual Customers"""
    
    class Meta:
        model = Customer
        exclude = ['created_by', 'status', 'bvn_verified', 'nin_verified', 'created_at', 'updated_at']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'other_names': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'place_of_birth': forms.TextInput(attrs={'class': 'form-control'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'bvn': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 11}),
            'nin': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 11}),
            'identification_type': forms.Select(attrs={'class': 'form-select'}),
            'next_of_kin_name': forms.TextInput(attrs={'class': 'form-control'}),
            'next_of_kin_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'passport_photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'id_card_front': forms.FileInput(attrs={'class': 'form-control'}),
            'id_card_back': forms.FileInput(attrs={'class': 'form-control'}),
            'signature': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'proof_of_address': forms.FileInput(attrs={'class': 'form-control'}),
        }


class CorporateForm(forms.ModelForm):
    """Form for creating/editing Corporate entities"""
    
    class Meta:
        model = Corporate
        fields = [
            'business_name', 'trading_name', 'business_type', 'registration_number',
            'tax_identification_number', 'email', 'phone_number', 'website',
            'address', 'city', 'state', 'country', 'postal_code',
            'nature_of_business', 'date_incorporated', 'business_commencement_date',
            'cac_certificate', 'scuml_certificate', 'tin_certificate',
            'utility_bill', 'memart', 'board_resolution'
        ]
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Business Name'}),
            'trading_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Trading Name (Optional)'}),
            'business_type': forms.Select(attrs={'class': 'form-select'}),
            'registration_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'RC Number'}),
            'tax_identification_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'TIN'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'nature_of_business': forms.TextInput(attrs={'class': 'form-control'}),
            'date_incorporated': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'business_commencement_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cac_certificate': forms.FileInput(attrs={'class': 'form-control'}),
            'scuml_certificate': forms.FileInput(attrs={'class': 'form-control'}),
            'tin_certificate': forms.FileInput(attrs={'class': 'form-control'}),
            'utility_bill': forms.FileInput(attrs={'class': 'form-control'}),
            'memart': forms.FileInput(attrs={'class': 'form-control'}),
            'board_resolution': forms.FileInput(attrs={'class': 'form-control'}),
        }


class DirectorForm(forms.ModelForm):
    """Form for creating/editing Directors"""
    
    class Meta:
        model = Director
        exclude = ['corporate', 'created_at', 'updated_at']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'other_names': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'place_of_birth': forms.TextInput(attrs={'class': 'form-control'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'bvn': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 11}),
            'nin': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 11}),
            'identification_type': forms.Select(attrs={'class': 'form-select'}),
            'next_of_kin_name': forms.TextInput(attrs={'class': 'form-control'}),
            'next_of_kin_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_type': forms.Select(attrs={'class': 'form-select'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pep': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'passport_photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'id_card_front': forms.FileInput(attrs={'class': 'form-control'}),
            'id_card_back': forms.FileInput(attrs={'class': 'form-control'}),
            'signature': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'proof_of_address': forms.FileInput(attrs={'class': 'form-control'}),
        }


class WalletGenerationForm(forms.Form):
    """Form for generating wallet for a corporate"""
    
    WALLET_OPTION_CHOICES = [
        ('generate', 'Generate New Wallet'),
        ('existing', 'Link Existing Wallet'),
    ]
    
    wallet_option = forms.ChoiceField(
        choices=WALLET_OPTION_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='generate'
    )
    
    director = forms.ModelChoiceField(
        queryset=Director.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text='Select the primary director/signatory for this wallet'
    )
    
    existing_account_number = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter 10-digit account number'})
    )
    
    existing_account_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account holder name'})
    )
    
    def __init__(self, corporate, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['director'].queryset = Director.objects.filter(corporate=corporate)
    
    def clean(self):
        cleaned_data = super().clean()
        wallet_option = cleaned_data.get('wallet_option')
        
        if wallet_option == 'existing':
            account_number = cleaned_data.get('existing_account_number')
            account_name = cleaned_data.get('existing_account_name')
            
            if not account_number:
                self.add_error('existing_account_number', 'Account number is required for existing wallet')
            elif len(account_number) != 10:
                self.add_error('existing_account_number', 'Account number must be 10 digits')
            
            if not account_name:
                self.add_error('existing_account_name', 'Account name is required for existing wallet')
        
        return cleaned_data


class TransferForm(forms.Form):
    """Form for wallet transfers"""
    
    TRANSFER_TYPE_CHOICES = [
        ('internal', 'Internal Transfer (9PSB)'),
        ('external', 'External Transfer (Other Banks)'),
    ]
    
    NIGERIAN_BANKS = [
        ('', '-- Select Bank --'),
        ('000001', 'Sterling Bank'),
        ('000002', 'Keystone Bank'),
        ('000003', 'FCMB'),
        ('000004', 'United Bank for Africa'),
        ('000005', 'Diamond Bank'),
        ('000006', 'JAIZ Bank'),
        ('000007', 'Fidelity Bank'),
        ('000008', 'Polaris Bank'),
        ('000009', 'Citi Bank'),
        ('000010', 'Ecobank'),
        ('000011', 'Unity Bank'),
        ('000012', 'StanbicIBTC Bank'),
        ('000013', 'GTBank'),
        ('000014', 'Access Bank'),
        ('000015', 'Zenith Bank'),
        ('000016', 'First Bank of Nigeria'),
        ('000017', 'Wema Bank'),
        ('000018', 'Union Bank'),
        ('000019', 'Enterprise Bank'),
        ('000020', 'Heritage Bank'),
        ('000021', 'Standard Chartered Bank'),
        ('000022', 'Suntrust Bank'),
        ('000023', 'Providus Bank'),
        ('000024', 'Rand Merchant Bank'),
        ('000025', 'Titan Trust Bank'),
        ('000026', 'Taj Bank'),
        ('000027', 'Globus Bank'),
        ('000028', 'Central Bank of Nigeria'),
        ('000029', 'Lotus Bank'),
        ('000030', 'Parallex Bank'),
        ('000031', 'Premium Trust Bank'),
        ('000032', 'Optimus Bank'),
        ('000033', 'Signature Bank'),
        ('100001', 'FET'),
        ('100002', 'PAGA'),
        ('100003', 'Parkway-ReadyCash'),
        ('100004', 'Cellulant'),
        ('100005', 'eTranzact'),
        ('100006', 'Payattitude'),
        ('100007', 'EcoMobile'),
        ('100008', 'Teasy Mobile'),
        ('100009', 'GT Mobile'),
        ('100010', 'Mkudi'),
        ('100011', 'VTNetwork'),
        ('100012', 'Intellifin'),
        ('100013', 'AccessMobile'),
        ('100014', 'FBNMobile'),
        ('100015', 'Kegow'),
        ('100016', 'FortisMobile'),
        ('100017', 'Hedonmark'),
        ('100018', 'ZenithMobile'),
        ('100019', 'Fidelity Mobile'),
        ('100020', 'Eartholeum'),
        ('100021', 'StanbicMobile'),
        ('100022', 'GoMoney'),
        ('100023', 'TagPay'),
        ('100024', 'Imperial Homes Mortgage Bank'),
        ('100025', 'Kuda Bank'),
        ('100026', 'Carbon'),
        ('100027', 'OPay'),
        ('100028', 'PalmPay'),
        ('100029', 'Moniepoint MFB'),
        ('100030', 'Rubies Bank'),
        ('100031', 'ALAT by Wema'),
        ('100032', 'Sparkle'),
        ('100033', 'Eyowo'),
        ('100034', 'VFD MFB'),
        ('100035', 'LAPO MFB'),
        ('120001', '9PSB'),
    ]
    
    transfer_type = forms.ChoiceField(
        choices=TRANSFER_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    beneficiary_bank = forms.ChoiceField(
        choices=NIGERIAN_BANKS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    beneficiary_account = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account Number'})
    )
    beneficiary_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': True})
    )
    amount = forms.DecimalField(
        max_digits=18,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'})
    )
    narration = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Transaction narration'})
    )


class CreditDebitForm(forms.Form):
    """Form for credit/debit operations"""
    
    amount = forms.DecimalField(
        max_digits=18,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'})
    )
    narration = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Transaction narration'})
    )
