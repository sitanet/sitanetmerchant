from django.db import models
from django.contrib.auth.models import User
import uuid


class Customer(models.Model):
    """Individual customer model"""
    
    GENDER_CHOICES = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACTIVE', 'Active'),
        ('SUSPENDED', 'Suspended'),
        ('CLOSED', 'Closed'),
    ]
    
    IDENTIFICATION_TYPE_CHOICES = [
        ('NATIONAL_ID', 'National ID'),
        ('DRIVERS_LICENSE', 'Driver\'s License'),
        ('INTERNATIONAL_PASSPORT', 'International Passport'),
        ('VOTERS_CARD', 'Voter\'s Card'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    other_names = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    place_of_birth = models.CharField(max_length=100)
    nationality = models.CharField(max_length=50, default='NIGERIAN')
    
    # Contact
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    
    # Identification
    bvn = models.CharField(max_length=11, unique=True, verbose_name='BVN')
    nin = models.CharField(max_length=11, blank=True, null=True, verbose_name='NIN')
    identification_type = models.CharField(max_length=30, choices=IDENTIFICATION_TYPE_CHOICES)
    
    # Next of Kin
    next_of_kin_name = models.CharField(max_length=200)
    next_of_kin_phone = models.CharField(max_length=20)
    
    # Documents
    passport_photo = models.ImageField(upload_to='customers/photos/', blank=True, null=True)
    id_card_front = models.FileField(upload_to='customers/id_front/', blank=True, null=True)
    id_card_back = models.FileField(upload_to='customers/id_back/', blank=True, null=True)
    signature = models.ImageField(upload_to='customers/signatures/', blank=True, null=True)
    proof_of_address = models.FileField(upload_to='customers/address/', blank=True, null=True)
    
    # Verification
    bvn_verified = models.BooleanField(default=False)
    nin_verified = models.BooleanField(default=False)
    
    # Status and Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_customers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        names = [self.first_name, self.other_names, self.last_name]
        return ' '.join(filter(None, names))


class Corporate(models.Model):
    """Corporate entity model"""
    
    BUSINESS_TYPE_CHOICES = [
        ('SOLE_PROPRIETORSHIP', 'Sole Proprietorship'),
        ('PARTNERSHIP', 'Partnership'),
        ('LIMITED_LIABILITY_COMPANY', 'Limited Liability Company'),
        ('CORPORATIONS', 'Corporation'),
        ('NGO', 'NGO'),
        ('COOPERATIVE', 'Cooperative'),
        ('SOCIAL_ENTERPRISE', 'Social Enterprise'),
        ('FRANCHISE', 'Franchise'),
        ('OTHERS', 'Others'),
    ]
    
    INDUSTRIAL_SECTOR_CHOICES = [
        ('TECHNOLOGY', 'Technology'),
        ('FINANCE', 'Finance'),
        ('HEALTHCARE', 'Healthcare'),
        ('EDUCATION', 'Education'),
        ('RETAIL', 'Retail'),
        ('MANUFACTURING', 'Manufacturing'),
        ('AGRICULTURE', 'Agriculture'),
        ('REAL_ESTATE', 'Real Estate'),
        ('TRANSPORTATION', 'Transportation'),
        ('OTHERS', 'Others'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACTIVE', 'Active'),
        ('SUSPENDED', 'Suspended'),
        ('CLOSED', 'Closed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business_name = models.CharField(max_length=255)
    trading_name = models.CharField(max_length=255, blank=True, null=True)
    business_type = models.CharField(max_length=50, choices=BUSINESS_TYPE_CHOICES)
    registration_number = models.CharField(max_length=50, unique=True)
    tax_identification_number = models.CharField(max_length=50, blank=True, null=True)
    
    # Contact Information
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    website = models.URLField(blank=True, null=True)
    
    # Address
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='Nigeria')
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    
    # Business Details
    industrial_sector = models.CharField(max_length=50, choices=INDUSTRIAL_SECTOR_CHOICES, default='OTHERS')
    nature_of_business = models.CharField(max_length=255)
    date_incorporated = models.DateField()
    business_commencement_date = models.DateField(blank=True, null=True)
    company_reg_date = models.DateField(blank=True, null=True)
    
    # Contact Person
    contact_person_first_name = models.CharField(max_length=100, blank=True, null=True)
    contact_person_last_name = models.CharField(max_length=100, blank=True, null=True)
    
    # Documents (file paths)
    cac_certificate = models.FileField(upload_to='documents/cac/', blank=True, null=True)
    scuml_certificate = models.FileField(upload_to='documents/scuml/', blank=True, null=True)
    tin_certificate = models.FileField(upload_to='documents/tin/', blank=True, null=True)
    utility_bill = models.FileField(upload_to='documents/utility/', blank=True, null=True)
    memart = models.FileField(upload_to='documents/memart/', blank=True, null=True)
    board_resolution = models.FileField(upload_to='documents/board/', blank=True, null=True)
    cac_status_report = models.FileField(upload_to='documents/cac_status/', blank=True, null=True)
    proof_of_address = models.FileField(upload_to='documents/address/', blank=True, null=True)
    regulatory_license_fintech = models.FileField(upload_to='documents/fintech_license/', blank=True, null=True)
    
    # 9PSB Integration
    npsb_business_id = models.CharField(max_length=50, blank=True, null=True)
    npsb_account_number = models.CharField(max_length=20, blank=True, null=True)
    npsb_account_name = models.CharField(max_length=255, blank=True, null=True)
    npsb_submission_status = models.CharField(max_length=20, blank=True, null=True)  # PENDING, APPROVED, DECLINED
    
    # Status and Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_corporates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Corporate'
        verbose_name_plural = 'Corporates'

    def __str__(self):
        return self.business_name


class Director(models.Model):
    """Director/Signatory for Corporate entity"""
    
    GENDER_CHOICES = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
    ]
    
    CUSTOMER_TYPE_CHOICES = [
        ('DIRECTOR', 'Director'),
        ('SIGNATORY', 'Signatory'),
        ('SHAREHOLDER', 'Shareholder'),
    ]
    
    IDENTIFICATION_TYPE_CHOICES = [
        ('NATIONAL_ID', 'National ID'),
        ('DRIVERS_LICENSE', 'Driver\'s License'),
        ('INTERNATIONAL_PASSPORT', 'International Passport'),
        ('VOTERS_CARD', 'Voter\'s Card'),
    ]
    
    NATIONALITY_CHOICES = [
        ('NIGERIAN', 'Nigerian'),
        ('OTHER', 'Other'),
    ]
    
    NPSB_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('DECLINED', 'Declined'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    corporate = models.ForeignKey(Corporate, on_delete=models.CASCADE, related_name='directors')
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    other_names = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    place_of_birth = models.CharField(max_length=100, blank=True, null=True)
    nationality = models.CharField(max_length=50, choices=NATIONALITY_CHOICES, default='NIGERIAN')
    other_nationality_type = models.CharField(max_length=100, blank=True, null=True)
    
    # Contact
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    
    # Identification
    bvn = models.CharField(max_length=11, verbose_name='BVN')
    nin = models.CharField(max_length=11, blank=True, null=True, verbose_name='NIN')
    identification_type = models.CharField(max_length=30, choices=IDENTIFICATION_TYPE_CHOICES)
    
    # Next of Kin
    next_of_kin_name = models.CharField(max_length=200)
    next_of_kin_phone = models.CharField(max_length=20)
    
    # Role
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPE_CHOICES, default='DIRECTOR')
    is_primary = models.BooleanField(default=False)
    pep = models.BooleanField(default=False, verbose_name='Politically Exposed Person')
    
    # Documents
    passport_photo = models.ImageField(upload_to='directors/photos/', blank=True, null=True)
    id_card_front = models.FileField(upload_to='directors/id_front/', blank=True, null=True)
    id_card_back = models.FileField(upload_to='directors/id_back/', blank=True, null=True)
    signature = models.ImageField(upload_to='directors/signatures/', blank=True, null=True)
    proof_of_address = models.FileField(upload_to='directors/address/', blank=True, null=True)
    
    # 9PSB Verification Status
    npsb_status = models.CharField(max_length=20, choices=NPSB_STATUS_CHOICES, blank=True, null=True)
    npsb_declined_items = models.JSONField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_primary', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        names = [self.first_name, self.other_names, self.last_name]
        return ' '.join(filter(None, names))


class Wallet(models.Model):
    """Wallet for Corporate or Individual Customer"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACTIVE', 'Active'),
        ('FROZEN', 'Frozen'),
        ('CLOSED', 'Closed'),
    ]
    
    WALLET_TYPE_CHOICES = [
        ('CORPORATE', 'Corporate'),
        ('INDIVIDUAL', 'Individual'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet_type = models.CharField(max_length=20, choices=WALLET_TYPE_CHOICES, default='CORPORATE')
    corporate = models.ForeignKey(Corporate, on_delete=models.CASCADE, related_name='wallets', blank=True, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='wallets', blank=True, null=True)
    
    # Account Details
    account_number = models.CharField(max_length=20, unique=True)
    account_name = models.CharField(max_length=255)
    npsb_customer_id = models.CharField(max_length=50, blank=True, null=True)
    
    # Balance
    ledger_balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    available_balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    
    # Limits
    tier = models.CharField(max_length=20, blank=True, null=True)
    maximum_balance = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    maximum_deposit = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    freeze_status = models.CharField(max_length=20, blank=True, null=True)
    lien_status = models.CharField(max_length=20, blank=True, null=True)
    pnd_status = models.CharField(max_length=20, blank=True, null=True)
    
    # 9PSB Integration
    npsb_order_ref = models.CharField(max_length=50, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        if self.corporate:
            return f"{self.account_number} - {self.corporate.business_name}"
        elif self.customer:
            return f"{self.account_number} - {self.customer.full_name}"
        return self.account_number
    
    @property
    def owner_name(self):
        if self.corporate:
            return self.corporate.business_name
        elif self.customer:
            return self.customer.full_name
        return "Unknown"


class Transaction(models.Model):
    """Wallet Transaction"""
    
    TYPE_CHOICES = [
        ('CREDIT', 'Credit'),
        ('DEBIT', 'Debit'),
        ('TRANSFER', 'Transfer'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    narration = models.CharField(max_length=255)
    
    # Reference
    transaction_reference = models.CharField(max_length=100, unique=True)
    session_id = models.CharField(max_length=100, blank=True, null=True)
    
    # For transfers
    beneficiary_account = models.CharField(max_length=20, blank=True, null=True)
    beneficiary_bank = models.CharField(max_length=10, blank=True, null=True)
    beneficiary_name = models.CharField(max_length=255, blank=True, null=True)
    
    # Fees
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    response_code = models.CharField(max_length=10, blank=True, null=True)
    response_message = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} - {self.transaction_reference}"
