# Corporate Wallet API Endpoints

This document contains both the **Local Django Project API** endpoints and the **9PSB External API** endpoints.

---

# PART 1: Local Django Project API

Base URL: `/api/`

## Corporate Endpoints

### 1. Create Corporate
**POST** `/api/corporates/`

Creates a new corporate entity.

**Request Body:**
```json
{
    "business_name": "ABC Company Ltd",
    "trading_name": "ABC Trading",
    "business_type": "LIMITED_LIABILITY",
    "registration_number": "RC123456",
    "tax_identification_number": "12345678901",
    "email": "info@abccompany.com",
    "phone_number": "+2348012345678",
    "website": "https://abccompany.com",
    "address": "123 Main Street",
    "city": "Lagos",
    "state": "Lagos",
    "country": "Nigeria",
    "postal_code": "100001",
    "nature_of_business": "Import and Export",
    "date_incorporated": "2020-01-15",
    "business_commencement_date": "2020-02-01"
}
```

**Business Types:**
- `SOLE_PROPRIETORSHIP`
- `PARTNERSHIP`
- `LIMITED_LIABILITY`
- `PUBLIC_LIMITED`

---

### 2. List Corporates
**GET** `/api/corporates/`

Returns list of all corporates.

---

### 3. Get Corporate Details
**GET** `/api/corporates/{corporate_id}/`

Returns full corporate details including directors and wallets.

---

### 4. Update Corporate
**PUT** `/api/corporates/{corporate_id}/`

---

### 5. Delete Corporate
**DELETE** `/api/corporates/{corporate_id}/`

---

## Director Endpoints

### 6. Add Director to Corporate
**POST** `/api/corporates/{corporate_id}/directors/`

**Request Body:**
```json
{
    "first_name": "John",
    "last_name": "Doe",
    "other_names": "Smith",
    "gender": "MALE",
    "date_of_birth": "1985-06-15",
    "place_of_birth": "Lagos",
    "nationality": "NIGERIAN",
    "email": "john.doe@email.com",
    "phone_number": "+2348012345678",
    "address": "456 Business Avenue",
    "city": "Lagos",
    "bvn": "12345678901",
    "nin": "12345678901",
    "identification_type": "NATIONAL_ID",
    "next_of_kin_name": "Jane Doe",
    "next_of_kin_phone": "+2348098765432",
    "customer_type": "DIRECTOR",
    "is_primary": true,
    "pep": false
}
```

**Customer Types:** `DIRECTOR`, `SIGNATORY`, `SHAREHOLDER`

**Identification Types:** `NATIONAL_ID`, `DRIVERS_LICENSE`, `INTERNATIONAL_PASSPORT`, `VOTERS_CARD`

---

### 7. List Directors
**GET** `/api/corporates/{corporate_id}/directors/`

---

### 8. Get/Update/Delete Director
- **GET** `/api/corporates/{corporate_id}/directors/{director_id}/`
- **PUT** `/api/corporates/{corporate_id}/directors/{director_id}/`
- **DELETE** `/api/corporates/{corporate_id}/directors/{director_id}/`

---

## Wallet Endpoints (Local)

### 9. Submit Corporate Account
**POST** `/api/corporates/{corporate_id}/submit_corporate/`

Submits corporate data and documents to 9PSB for verification. The account will be created in PENDING status and activated via webhook after 9PSB approval.

**Prerequisites:**
- Corporate must have at least one director
- Tax Identification Number (TIN) is required
- CAC Certificate is required
- All required documents should be uploaded

**No request body required** - Data is pulled from the corporate and directors records.

**Response (Success):**
```json
{
    "status": "success",
    "message": "Corporate Account Request Submitted For Processing",
    "data": {}
}
```

---

### 10. Update Corporate Account
**POST** `/api/corporates/{corporate_id}/update_corporate/`

Updates corporate data and documents on 9PSB (for re-submission after decline).

**Prerequisites:**
- Tax Identification Number (TIN) is required
- Corporate must have at least one director

**Response:**
```json
{
    "status": "success",
    "message": "Corporate Data Update Submitted For Processing"
}
```

---

### 11. Check Corporate Status
**GET** `/api/corporates/{corporate_id}/corporate_status/`

Checks the verification status of a corporate account from 9PSB.

**Response (Pending):**
```json
{
    "status": "success",
    "message": "Corporate Review Retrieved",
    "data": {
        "finalStatus": "PENDING",
        "channel": "YOUR_CHANNEL",
        "organization": {
            "status": "PENDING",
            "tin": "87365677-0000",
            "accountNumber": "1100077243",
            "accountName": "CHANNEL/Company Name"
        },
        "members": [
            {
                "bvn": "22123356789",
                "name": "Michael Johnson",
                "type": "DIRECTOR",
                "status": "PENDING",
                "declinedItems": {}
            }
        ]
    }
}
```

**Response (Approved):**
```json
{
    "status": "success",
    "message": "Corporate Review Retrieved",
    "data": {
        "finalStatus": "APPROVED",
        "organization": {
            "status": "APPROVED",
            "tin": "87365677-0000",
            "accountNumber": "1100077243",
            "accountName": "CHANNEL/Company Name"
        },
        "members": [...]
    }
}
```

**Note:** When status is APPROVED, a Wallet is automatically created locally.

---

### 12. Corporate Verification Webhook
**POST** `/api/webhooks/corporate-verification/?event=corporate-verification`

Webhook endpoint for 9PSB to send verification results.

**Webhook Payload (Approval):**
```json
{
    "finalStatus": "APPROVED",
    "channel": "YOUR_CHANNEL",
    "organization": {
        "status": "APPROVED",
        "tin": "92365677-0011",
        "accountNumber": "1100076507",
        "accountName": "CHANNEL/Company Name",
        "declinedItems": {}
    },
    "members": [
        {
            "bvn": "22222222222",
            "name": "Michael Johnson",
            "type": "DIRECTOR",
            "status": "APPROVED",
            "declinedItems": {}
        }
    ]
}
```

**Webhook Payload (Decline):**
```json
{
    "finalStatus": "DECLINED",
    "organization": {
        "status": "DECLINED",
        "tin": "92365677-0011",
        "accountNumber": "1100076507",
        "accountName": "CHANNEL/Company Name",
        "declinedItems": {
            "memart": "unclear image",
            "cacCertificate": "Document is outdated"
        }
    },
    "members": [
        {
            "bvn": "22222222222",
            "name": "Michael Johnson",
            "type": "DIRECTOR",
            "status": "DECLINED",
            "declinedItems": {
                "proofOfAddressVerification": "document is not valid",
                "idCardFront": "Uploaded image is not clear enough"
            }
        }
    ]
}
```

---

### 10. List Wallets
**GET** `/api/wallets/`

---

### 11. Get Wallet Details
**GET** `/api/wallets/{wallet_id}/`

---

### 12. Get Wallet Balance
**GET** `/api/wallets/{wallet_id}/balance/`

---

### 13. Credit Wallet
**POST** `/api/wallets/{wallet_id}/credit/`

```json
{
    "amount": "10000.00",
    "narration": "Initial deposit"
}
```

---

### 14. Debit Wallet
**POST** `/api/wallets/{wallet_id}/debit/`

```json
{
    "amount": "5000.00",
    "narration": "Payment for services"
}
```

---

### 15. Transfer from Wallet
**POST** `/api/wallets/{wallet_id}/transfer/`

**Internal Transfer:**
```json
{
    "beneficiary_account": "9000654321",
    "amount": "25000.00",
    "narration": "Payment to supplier",
    "transfer_type": "internal"
}
```

**External Transfer:**
```json
{
    "beneficiary_account": "0123456789",
    "beneficiary_bank": "058",
    "beneficiary_name": "Beneficiary Name",
    "amount": "25000.00",
    "narration": "Payment to vendor",
    "transfer_type": "external"
}
```

---

## Transaction Endpoints

### 16. List Transactions
**GET** `/api/transactions/`

---

### 17. Get Transaction Details
**GET** `/api/transactions/{transaction_id}/`

---

### 18. Requery Transaction
**POST** `/api/transactions/{transaction_id}/requery/`

---

## Utility Endpoints

### 19. Name Enquiry
**POST** `/api/name-enquiry/`

```json
{
    "bank_code": "058",
    "account_number": "0123456789"
}
```

---
---

# PART 2: 9PSB Wallet As A Service - External API

Base URL: `{{baseUrl}}/api/v1`

**Contact Support:** 9PSB - itaccounts@9psb.com.ng

---

## Authentication

### 1. Authenticate
**POST** `/api/v1/authenticate`

Authenticates and returns access token for subsequent requests.

**Headers:**
```
Content-Type: application/json
Accept: */*
```

**Request Body:**
```json
{
    "username": "{{username}}",
    "password": "{{password}}",
    "clientId": "{{clientId}}",
    "clientSecret": "{{clientSecret}}"
}
```

**Success Response (200):**
```json
{
    "message": "successful",
    "accessToken": "<string>",
    "expiresIn": "<string>",
    "refreshToken": "<string>",
    "refreshExpiresIn": "<string>",
    "jwt": "<string>",
    "tokenType": "<string>"
}
```

---

## Wallet Operations

### 2. Open Wallet
**POST** `/api/v1/open_wallet`

Creates a new wallet account.

**Headers:**
```
Content-Type: application/json
Accept: application/json
Authorization: Bearer {{bearerToken}}
```

**Request Body:**
```json
{
    "bvn": "22416208831",
    "dateOfBirth": "29/04/1995",
    "gender": 1,
    "lastName": "Matthew",
    "otherNames": "Oluwole",
    "phoneNo": "07034478568",
    "transactionTrackingRef": "DGN2025121912010000",
    "placeOfBirth": "Lagos",
    "address": "7, Ikate Elegushi",
    "nationalIdentityNo": "65241199803",
    "ninUserId": "ABCDEF-1238",
    "nextOfKinPhoneNo": "09134567894",
    "nextOfKinName": "Mark Oluwole",
    "email": "matthew.oluwole@yopmail.com"
}
```

**Field Notes:**
- `gender`: 1 = Male, 0 = Female
- `dateOfBirth`: Format DD/MM/YYYY
- `transactionTrackingRef`: Unique reference for the transaction
- `ninUserId`: NIN User ID (uppercase alphanumeric with hyphen)

---

## Corporate Account Operations

### Submit Corporate Data
**POST** `/api/v1/corporates/submit`

Submits corporate account application with documents (multipart/form-data).

**Content-Type:** `multipart/form-data`

**Form Fields (Corporate):**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| taxIDNo | text | Yes | Tax Identification Number (TIN) |
| businessName | text | Yes | Business Name |
| email | text | Yes | Business Email |
| phoneNo | text | Yes | Business Phone Number |
| address | text | Yes | Business Address |
| industrialSector | text | No | Business Sector (TECHNOLOGY, FINANCE, etc.) |
| businessType | text | Yes | SOLE_PROPRIETORSHIP, PARTNERSHIP, LIMITED_LIABILITY_COMPANY, etc. |
| companyRegDate | text | Yes | Company Registration Date (yyyy-MM-dd) |
| contactPersonFirstName | text | Yes | Contact Person First Name |
| contactPersonLastName | text | Yes | Contact Person Last Name |
| webAddress | text | No | Corporate Website URL |
| dateIncorporated | text | No | Date of Incorporation (yyyy-MM-dd) |
| businessCommencementDate | text | No | Business Start Date (yyyy-MM-dd) |
| registrationNumber | text | Yes | RC or BN Number |
| postalAddress | text | No | Postal Address |

**Form Fields (Documents):**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| cacCertificate | file | Yes | Certificate of Incorporation (PDF) |
| scumlCertificate | file | Yes | SCUML Certificate (PDF) |
| regulatoryLicenseFintech | file | No | Fintech Regulatory License (PDF) |
| utilityBill | file | Yes | Utility Bill (JPEG, PNG, PDF) |
| proofOfAddressVerification | file | Yes | Proof of Address (JPEG, PNG, PDF) |
| memart | file | Yes | Memorandum and Articles (PDF) |
| tinCertificate | file | Yes | Tax ID Certificate (JPG, PNG, PDF) |
| cacOrStatusReport | file | Yes | CAC Status Report (PDF) |
| letterOfBoardResolution | file | Yes | Board Resolution Letter (PDF) |

**Form Fields (Directors - array):**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| directors[0].firstName | text | Yes | Director's First Name |
| directors[0].lastName | text | Yes | Director's Last Name |
| directors[0].otherNames | text | No | Director's Other Names |
| directors[0].address | text | Yes | Director's Address |
| directors[0].gender | text | Yes | MALE or FEMALE |
| directors[0].dateOfBirth | text | Yes | Date of Birth (yyyy-MM-dd) |
| directors[0].email | text | Yes | Email Address |
| directors[0].phoneNo | text | Yes | Phone Number |
| directors[0].bankVerificationNumber | text | Yes | BVN |
| directors[0].nationalIdentityNo | text | Yes | NIN |
| directors[0].identificationType | text | Yes | NATIONAL_ID, DRIVERS_LICENSE, etc. |
| directors[0].nationality | text | Yes | NIGERIAN or OTHER |
| directors[0].otherNationalityType | text | No | If OTHER, specify nationality |
| directors[0].nextOfKinName | text | Yes | Next of Kin Name |
| directors[0].nextOfKinPhoneNumber | text | Yes | Next of Kin Phone |
| directors[0].pep | text | Yes | YES or NO (Politically Exposed Person) |
| directors[0].passportPhoto | file | Yes | Passport Photo (JPG, PNG) |
| directors[0].proofOfAddressVerification | file | Yes | Proof of Address (JPG, PNG, PDF) |
| directors[0].idCardFront | file | Yes | ID Card Front (JPG, PNG, PDF) |
| directors[0].idCardBack | file | No | ID Card Back (JPG, PNG, PDF) |

**Success Response (200):**
```json
{
    "status": "SUCCESS",
    "responseCode": "00",
    "message": "Corporate Account Request Submitted For Processing"
}
```

---

### Update Corporate Data
**POST** `/api/v1/corporates/update`

Updates corporate account data (same format as submit).

---

### Check Corporate Status
**GET** `/api/v1/corporates/status?tin={tin}`

Checks corporate verification status by TIN.

**Success Response (200):**
```json
{
    "status": "SUCCESS",
    "responseCode": "00",
    "message": "Corporate Review Retrieved",
    "data": {
        "finalStatus": "PENDING",
        "channel": "YOUR_CHANNEL",
        "organization": {
            "status": "PENDING",
            "tin": "87365677-0000",
            "accountNumber": "1100077243",
            "accountName": "CHANNEL/EweduTech Ltd"
        },
        "members": [
            {
                "bvn": "22123356789",
                "name": "Michael Johnson",
                "type": "DIRECTOR",
                "status": "PENDING",
                "declinedItems": {}
            }
        ]
    }
}
```

---

### Corporate Verification Webhook
**POST** `{clientWebhookUrl}?event=corporate-verification`

9PSB sends verification results to your webhook URL.

**Approval Payload:**
```json
{
    "finalStatus": "APPROVED",
    "channel": "YOUR_CHANNEL",
    "organization": {
        "status": "APPROVED",
        "tin": "92365677-0011",
        "accountNumber": "1100076507",
        "accountName": "CHANNEL/Company Name",
        "declinedItems": {}
    },
    "members": [
        {
            "bvn": "22222222222",
            "name": "Michael Johnson",
            "type": "DIRECTOR",
            "status": "APPROVED",
            "declinedItems": {}
        }
    ]
}
```

**Decline Payload:**
```json
{
    "finalStatus": "DECLINED",
    "organization": {
        "status": "DECLINED",
        "tin": "92365677-0011",
        "declinedItems": {
            "memart": "unclear image",
            "cacCertificate": "Document is outdated"
        }
    },
    "members": [
        {
            "bvn": "22222222222",
            "name": "Michael Johnson",
            "type": "DIRECTOR",
            "status": "DECLINED",
            "declinedItems": {
                "proofOfAddressVerification": "document is not valid"
            }
        }
    ]
}
```

**Success Response (200):**
```json
{
    "status": "SUCCESS",
    "message": "Account Opening successful",
    "data": {
        "orderRef": "1100032893",
        "customerID": "003289",
        "fullName": "9PSBQA1/Mike Deen",
        "accountNumber": "1100032893"
    }
}
```

---

### 3. Credit Wallet
**POST** `/api/v1/credit/transfer`

Credits funds to a wallet.

**Headers:**
```
Content-Type: application/json
Accept: application/json
Authorization: Bearer {{bearerToken}}
```

**Request Body:**
```json
{
    "accountNo": "1100075438",
    "narration": "TEST CREDIT",
    "totalAmount": 50000.00,
    "transactionId": "B202602112540001",
    "merchant": {
        "isFee": false,
        "merchantFeeAccount": "",
        "merchantFeeAmount": ""
    }
}
```

---

### 4. Debit Wallet
**POST** `/api/v1/debit/transfer`

Debits funds from a wallet.

**Headers:**
```
Content-Type: application/json
Accept: application/json
Authorization: Bearer {{bearerToken}}
```

**Request Body:**
```json
{
    "accountNo": "1100043017",
    "narration": "TEST DEBIT",
    "totalAmount": 100.00,
    "transactionId": "QA2024121616550000",
    "merchant": {
        "isFee": false,
        "merchantFeeAccount": "",
        "merchantFeeAmount": ""
    }
}
```

---

### 5. Wallet Enquiry
**POST** `/api/v1/wallet_enquiry`

Gets wallet details and balance information.

**Headers:**
```
Content-Type: application/json
Accept: application/json
Authorization: Bearer {{bearerToken}}
```

**Request Body:**
```json
{
    "accountNo": "1100035911"
}
```

**Success Response (200):**
```json
{
    "status": "SUCCESS",
    "message": "<string>",
    "data": {
        "name": "<string>",
        "number": "<string>",
        "email": "<string>",
        "status": "<string>",
        "phoneNo": "<string>",
        "lastName": "<string>",
        "firstName": "<string>",
        "tier": "<string>",
        "bvn": "<string>",
        "nuban": "<string>",
        "ledgerBalance": "<double>",
        "availableBalance": "<double>",
        "maximumBalance": "<double>",
        "maximumDeposit": "<string>",
        "freezeStatus": "<string>",
        "lienStatus": "<string>",
        "pndstatus": "<string>"
    }
}
```

---

### 6. Wallet Status
**POST** `/api/v1/wallet_status`

Gets the status of a wallet.

**Headers:**
```
Content-Type: application/json
Accept: application/json
Authorization: Bearer {{bearerToken}}
```

**Request Body:**
```json
{
    "accountNo": "1100035911"
}
```

**Success Response (200):**
```json
{
    "status": "SUCCESS",
    "message": "<string>",
    "data": {
        "walletStatus": "<string>",
        "responseCode": "<string>"
    }
}
```

---

### 7. Wallet Requery
**POST** `/api/v1/wallet_requery`

Requeries a transaction status.

**Headers:**
```
Content-Type: application/json
Accept: application/json
Authorization: Bearer {{bearerToken}}
```

**Request Body (Simple):**
```json
{
    "transactionId": "20240825124530001"
}
```

**Request Body (Detailed - for Credit/Debit):**
```json
{
    "transactionId": "QA2024072216470000",
    "amount": 1000,
    "transactionType": "CREDIT_WALLET",
    "transactionDate": "",
    "accountNo": "1100030727"
}
```

**Success Response (200):**
```json
{
    "status": "SUCCESS",
    "message": "Approved by Financial Institution",
    "data": {
        "isSuccessful": true,
        "responseMessage": "Approved by Financial Institution",
        "responseCode": "00",
        "reference": "QA2024072216470000",
        "status": "SUCCESS"
    }
}
```

---

## Bank Transfer Operations

### 8. Other Banks Enquiry (Name Enquiry)
**POST** `/api/v1/other_banks_enquiry`

Performs name enquiry for accounts at other banks.

**Headers:**
```
Content-Type: application/json
Accept: application/json
Authorization: Bearer {{bearerToken}}
```

**Request Body:**
```json
{
    "customer": {
        "account": {
            "bank": "120001",
            "number": "1100072516"
        }
    }
}
```

---

### 9. Transfer to Other Banks
**POST** `/api/v1/wallet_other_banks`

Transfers funds from wallet to accounts at other banks.

**Headers:**
```
Content-Type: application/json
Accept: application/json
Authorization: Bearer {{bearerToken}}
```

**Request Body:**
```json
{
    "customer": {
        "account": {
            "bank": "120001",
            "name": "John Doe",
            "number": "1100033670",
            "senderaccountnumber": "1100035911",
            "sendername": "John Doe"
        }
    },
    "narration": "Test Transfer",
    "order": {
        "amount": "1000",
        "country": "NGA",
        "currency": "NGN",
        "description": "TEST TRANSFER"
    },
    "transaction": {
        "reference": "202412170543900000"
    },
    "merchant": {
        "isFee": true,
        "merchantFeeAccount": "1100015137",
        "merchantFeeAmount": "16.13"
    }
}
```

---

## Common Response Formats

### Success Response
```json
{
    "status": "SUCCESS",
    "responseCode": "<string>",
    "message": "<string>",
    "data": { ... }
}
```

### Failed Response
```json
{
    "status": "FAILED",
    "responseCode": "<string>",
    "message": "<string>",
    "data": {},
    "error": "<string>",
    "fieldErrors": { ... }
}
```

### Pending Response
```json
{
    "status": "PENDING",
    "responseCode": "<string>",
    "message": "<string>",
    "data": { ... }
}
```

---

## HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | OK - Request successful |
| 202 | Accepted - Request accepted but processing |
| 400 | Bad Request - Invalid parameters |
| 403 | Forbidden - Authentication failed |
| 500 | Internal Server Error |

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `{{baseUrl}}` | API base URL |
| `{{username}}` | API username |
| `{{password}}` | API password |
| `{{clientId}}` | Client ID |
| `{{clientSecret}}` | Client secret |
| `{{bearerToken}}` | Bearer token from authenticate endpoint |
