from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.core.paginator import Paginator

from .models import Corporate, Director, Wallet, Transaction, Customer
from .forms import CorporateForm, DirectorForm, WalletGenerationForm, TransferForm, CreditDebitForm, CustomerForm
from core.services import npsb_service, NPSBAPIError
from core.verification import verification_service, VerificationError


@login_required
def dashboard(request):
    """Dashboard view"""
    corporates_count = Corporate.objects.count()
    customers_count = Customer.objects.count()
    wallets_count = Wallet.objects.count()
    active_wallets = Wallet.objects.filter(status='ACTIVE').count()
    recent_corporates = Corporate.objects.all()[:5]
    recent_customers = Customer.objects.all()[:5]
    
    context = {
        'corporates_count': corporates_count,
        'customers_count': customers_count,
        'wallets_count': wallets_count,
        'active_wallets': active_wallets,
        'recent_corporates': recent_corporates,
        'recent_customers': recent_customers,
    }
    return render(request, 'corporates/dashboard.html', context)


# ==================== CORPORATE VIEWS ====================

@login_required
def corporate_list(request):
    """List all corporates"""
    corporates = Corporate.objects.all()
    
    # Search
    search = request.GET.get('search', '')
    if search:
        corporates = corporates.filter(business_name__icontains=search)
    
    # Status filter
    status = request.GET.get('status', '')
    if status:
        corporates = corporates.filter(status=status)
    
    paginator = Paginator(corporates, 20)
    page = request.GET.get('page')
    corporates = paginator.get_page(page)
    
    context = {
        'corporates': corporates,
        'search': search,
        'status': status,
    }
    return render(request, 'corporates/corporate_list.html', context)


@login_required
def corporate_create(request):
    """Create new corporate"""
    if request.method == 'POST':
        form = CorporateForm(request.POST, request.FILES)
        if form.is_valid():
            corporate = form.save(commit=False)
            corporate.created_by = request.user
            corporate.save()
            messages.success(request, f'Corporate "{corporate.business_name}" created successfully.')
            return redirect('corporate_detail', pk=corporate.pk)
    else:
        form = CorporateForm()
    
    return render(request, 'corporates/corporate_form.html', {'form': form, 'title': 'Create Corporate'})


@login_required
def corporate_detail(request, pk):
    """View corporate details"""
    corporate = get_object_or_404(Corporate, pk=pk)
    directors = corporate.directors.all()
    wallets = corporate.wallets.all()
    
    context = {
        'corporate': corporate,
        'directors': directors,
        'wallets': wallets,
    }
    return render(request, 'corporates/corporate_detail.html', context)


@login_required
def corporate_edit(request, pk):
    """Edit corporate"""
    corporate = get_object_or_404(Corporate, pk=pk)
    
    if request.method == 'POST':
        form = CorporateForm(request.POST, request.FILES, instance=corporate)
        if form.is_valid():
            form.save()
            messages.success(request, 'Corporate updated successfully.')
            return redirect('corporate_detail', pk=corporate.pk)
    else:
        form = CorporateForm(instance=corporate)
    
    return render(request, 'corporates/corporate_form.html', {
        'form': form,
        'corporate': corporate,
        'title': 'Edit Corporate'
    })


@login_required
def corporate_delete(request, pk):
    """Delete corporate"""
    corporate = get_object_or_404(Corporate, pk=pk)
    
    if request.method == 'POST':
        business_name = corporate.business_name
        corporate.delete()
        messages.success(request, f'Corporate "{business_name}" deleted successfully.')
        return redirect('corporate_list')
    
    return render(request, 'corporates/corporate_confirm_delete.html', {'corporate': corporate})


# ==================== DIRECTOR VIEWS ====================

@login_required
def director_add(request, corporate_pk):
    """Add director to corporate"""
    corporate = get_object_or_404(Corporate, pk=corporate_pk)
    
    if request.method == 'POST':
        form = DirectorForm(request.POST, request.FILES)
        if form.is_valid():
            director = form.save(commit=False)
            director.corporate = corporate
            director.save()
            messages.success(request, f'Director "{director.full_name}" added successfully.')
            return redirect('corporate_detail', pk=corporate.pk)
    else:
        form = DirectorForm()
    
    return render(request, 'corporates/director_form.html', {
        'form': form,
        'corporate': corporate,
        'title': 'Add Director'
    })


@login_required
def director_edit(request, pk):
    """Edit director"""
    director = get_object_or_404(Director, pk=pk)
    
    if request.method == 'POST':
        form = DirectorForm(request.POST, request.FILES, instance=director)
        if form.is_valid():
            form.save()
            messages.success(request, 'Director updated successfully.')
            return redirect('corporate_detail', pk=director.corporate.pk)
    else:
        form = DirectorForm(instance=director)
    
    return render(request, 'corporates/director_form.html', {
        'form': form,
        'director': director,
        'corporate': director.corporate,
        'title': 'Edit Director'
    })


@login_required
def director_delete(request, pk):
    """Delete director"""
    director = get_object_or_404(Director, pk=pk)
    corporate = director.corporate
    
    if request.method == 'POST':
        name = director.full_name
        director.delete()
        messages.success(request, f'Director "{name}" deleted successfully.')
        return redirect('corporate_detail', pk=corporate.pk)
    
    return render(request, 'corporates/director_confirm_delete.html', {
        'director': director,
        'corporate': corporate
    })


# ==================== WALLET VIEWS ====================

@login_required
def wallet_generate(request, corporate_pk):
    """Submit corporate account to 9PSB for verification and wallet creation"""
    corporate = get_object_or_404(Corporate, pk=corporate_pk)
    directors = corporate.directors.all()
    form = WalletGenerationForm(corporate, request.POST or None)
    
    if request.method == 'POST':
        wallet_option = request.POST.get('wallet_option', 'new')
        
        try:
            if wallet_option == 'existing':
                # Link existing wallet
                account_number = request.POST.get('existing_account_number', '')
                account_name = request.POST.get('existing_account_name', '')
                
                if not account_number:
                    messages.error(request, 'Account number is required.')
                elif Wallet.objects.filter(account_number=account_number).exists():
                    messages.error(request, f'Wallet with account number {account_number} already exists in the system.')
                else:
                    wallet = Wallet.objects.create(
                        wallet_type='CORPORATE',
                        corporate=corporate,
                        account_number=account_number,
                        account_name=account_name or corporate.business_name,
                        status='ACTIVE'
                    )
                    
                    corporate.status = 'ACTIVE'
                    corporate.save()
                    
                    messages.success(request, f'Existing wallet linked successfully. Account Number: {wallet.account_number}')
                    return redirect('wallet_detail', pk=wallet.pk)
            
            elif wallet_option == 'check_status':
                # Check status of existing submission
                if not corporate.tax_identification_number:
                    messages.error(request, 'Tax Identification Number (TIN) is required to check status.')
                else:
                    response = npsb_service.get_corporate_status(corporate.tax_identification_number)
                    
                    if response.get('status') == 'SUCCESS':
                        data = response.get('data', {})
                        final_status = data.get('finalStatus')
                        org_data = data.get('organization', {})
                        
                        corporate.npsb_submission_status = final_status
                        if org_data.get('accountNumber'):
                            corporate.npsb_account_number = org_data.get('accountNumber')
                            corporate.npsb_account_name = org_data.get('accountName')
                        
                        if final_status == 'APPROVED':
                            corporate.status = 'ACTIVE'
                            corporate.save()
                            
                            # Create wallet
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
                                messages.success(request, f'Corporate approved! Wallet Account: {wallet.account_number}')
                                return redirect('wallet_detail', pk=wallet.pk)
                        elif final_status == 'DECLINED':
                            corporate.save()
                            messages.warning(request, f'Corporate verification was declined. Please update documents and resubmit.')
                        else:
                            corporate.save()
                            messages.info(request, f'Corporate verification status: {final_status}. Account: {org_data.get("accountNumber", "Pending")}')
                    else:
                        messages.error(request, f'Failed to check status: {response.get("message", "Unknown error")}')
            
            else:
                # Submit new corporate account to 9PSB
                # Validate required fields and documents
                missing_items = []
                
                # Corporate required fields
                if not directors.exists():
                    missing_items.append('At least one director')
                if not corporate.tax_identification_number:
                    missing_items.append('Tax Identification Number (TIN)')
                if not corporate.registration_number:
                    missing_items.append('Registration Number (RC/BN)')
                
                # Corporate required documents
                if not corporate.cac_certificate:
                    missing_items.append('CAC Certificate')
                if not corporate.scuml_certificate:
                    missing_items.append('SCUML Certificate')
                if not corporate.memart:
                    missing_items.append('Memart Document')
                if not corporate.tin_certificate:
                    missing_items.append('TIN Certificate')
                if not corporate.cac_status_report:
                    missing_items.append('CAC Status Report')
                if not corporate.board_resolution:
                    missing_items.append('Board Resolution Letter')
                if not corporate.utility_bill:
                    missing_items.append('Utility Bill')
                if not corporate.proof_of_address:
                    missing_items.append('Proof of Address')
                
                # Director required documents
                for director in directors:
                    if not director.bvn:
                        missing_items.append(f'Director {director.full_name}: BVN')
                    if not director.nin:
                        missing_items.append(f'Director {director.full_name}: NIN')
                    if not director.passport_photo:
                        missing_items.append(f'Director {director.full_name}: Passport Photo')
                    if not director.id_card_front:
                        missing_items.append(f'Director {director.full_name}: ID Card Front')
                    if not director.proof_of_address:
                        missing_items.append(f'Director {director.full_name}: Proof of Address')
                
                if missing_items:
                    messages.error(request, f'Missing required items: {", ".join(missing_items)}')
                else:
                    # Set contact person from primary director if not set
                    primary_director = directors.filter(is_primary=True).first() or directors.first()
                    if not corporate.contact_person_first_name:
                        corporate.contact_person_first_name = primary_director.first_name
                        corporate.contact_person_last_name = primary_director.last_name
                        corporate.save()
                    
                    response = npsb_service.submit_corporate_data(
                        corporate=corporate,
                        directors=list(directors)
                    )
                    
                    if response.get('status') == 'SUCCESS':
                        corporate.npsb_submission_status = 'PENDING'
                        corporate.save()
                        
                        messages.success(request, 'Corporate account submitted for verification. You will be notified when approved.')
                        return redirect('corporate_detail', pk=corporate.pk)
                    else:
                        messages.error(request, f'Failed to submit: {response.get("message", "Unknown error")}')
                
        except NPSBAPIError as e:
            messages.error(request, f'API Error: {e.message}')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    # Check missing documents for display
    missing_corporate_docs = []
    missing_director_docs = []
    
    if not corporate.tax_identification_number:
        missing_corporate_docs.append('Tax Identification Number (TIN)')
    if not corporate.registration_number:
        missing_corporate_docs.append('Registration Number (RC/BN)')
    if not corporate.cac_certificate:
        missing_corporate_docs.append('CAC Certificate')
    if not corporate.scuml_certificate:
        missing_corporate_docs.append('SCUML Certificate')
    if not corporate.memart:
        missing_corporate_docs.append('Memart Document')
    if not corporate.tin_certificate:
        missing_corporate_docs.append('TIN Certificate')
    if not corporate.cac_status_report:
        missing_corporate_docs.append('CAC Status Report')
    if not corporate.board_resolution:
        missing_corporate_docs.append('Board Resolution Letter')
    if not corporate.utility_bill:
        missing_corporate_docs.append('Utility Bill')
    if not corporate.proof_of_address:
        missing_corporate_docs.append('Proof of Address')
    
    for director in directors:
        director_missing = []
        if not director.bvn:
            director_missing.append('BVN')
        if not director.nin:
            director_missing.append('NIN')
        if not director.passport_photo:
            director_missing.append('Passport Photo')
        if not director.id_card_front:
            director_missing.append('ID Card Front')
        if not director.proof_of_address:
            director_missing.append('Proof of Address')
        if director_missing:
            missing_director_docs.append({'name': director.full_name, 'missing': director_missing})
    
    return render(request, 'corporates/wallet_generate.html', {
        'corporate': corporate,
        'directors': directors,
        'form': form,
        'has_required_docs': not missing_corporate_docs and not missing_director_docs,
        'missing_corporate_docs': missing_corporate_docs,
        'missing_director_docs': missing_director_docs,
    })


@login_required
def wallet_list(request):
    """List all wallets"""
    wallets = Wallet.objects.select_related('corporate').all()
    
    # Search
    search = request.GET.get('search', '')
    if search:
        wallets = wallets.filter(
            account_number__icontains=search
        ) | wallets.filter(
            corporate__business_name__icontains=search
        )
    
    paginator = Paginator(wallets, 20)
    page = request.GET.get('page')
    wallets = paginator.get_page(page)
    
    return render(request, 'corporates/wallet_list.html', {'wallets': wallets, 'search': search})


@login_required
def wallet_detail(request, pk):
    """View wallet details"""
    wallet = get_object_or_404(Wallet, pk=pk)
    transactions = wallet.transactions.all()[:20]
    
    # Try to fetch latest balance from API
    try:
        response = npsb_service.wallet_enquiry(wallet.account_number)
        if response.get('status') == 'SUCCESS':
            data = response.get('data', {})
            wallet.available_balance = data.get('availableBalance', wallet.available_balance)
            wallet.ledger_balance = data.get('ledgerBalance', wallet.ledger_balance)
            wallet.tier = data.get('tier', wallet.tier)
            wallet.save()
    except Exception:
        pass
    
    context = {
        'wallet': wallet,
        'transactions': transactions,
    }
    return render(request, 'corporates/wallet_detail.html', context)


@login_required
def wallet_refresh_balance(request, pk):
    """Refresh wallet balance from API"""
    wallet = get_object_or_404(Wallet, pk=pk)
    
    try:
        response = npsb_service.wallet_enquiry(wallet.account_number)
        if response.get('status') == 'SUCCESS':
            data = response.get('data', {})
            wallet.available_balance = data.get('availableBalance', 0)
            wallet.ledger_balance = data.get('ledgerBalance', 0)
            wallet.tier = data.get('tier')
            wallet.freeze_status = data.get('freezeStatus')
            wallet.lien_status = data.get('lienStatus')
            wallet.pnd_status = data.get('pndstatus')
            wallet.save()
            
            return JsonResponse({
                'success': True,
                'available_balance': str(wallet.available_balance),
                'ledger_balance': str(wallet.ledger_balance),
            })
    except NPSBAPIError as e:
        return JsonResponse({'success': False, 'error': e.message})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Failed to fetch balance'})


@login_required
def wallet_credit(request, pk):
    """Credit wallet"""
    wallet = get_object_or_404(Wallet, pk=pk)
    
    if request.method == 'POST':
        form = CreditDebitForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            narration = form.cleaned_data['narration']
            
            try:
                reference = npsb_service.generate_reference('CR')
                response = npsb_service.credit_wallet(
                    account_no=wallet.account_number,
                    amount=amount,
                    narration=narration,
                    transaction_id=reference
                )
                
                # Create transaction record
                Transaction.objects.create(
                    wallet=wallet,
                    transaction_type='CREDIT',
                    amount=amount,
                    narration=narration,
                    transaction_reference=reference,
                    status='SUCCESS' if response.get('status') == 'SUCCESS' else 'FAILED',
                    response_code=response.get('responseCode'),
                    response_message=response.get('message')
                )
                
                if response.get('status') == 'SUCCESS':
                    messages.success(request, f'Successfully credited {amount} to wallet')
                else:
                    messages.warning(request, f'Credit request submitted: {response.get("message")}')
                    
                return redirect('wallet_detail', pk=wallet.pk)
                
            except NPSBAPIError as e:
                messages.error(request, f'API Error: {e.message}')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
    else:
        form = CreditDebitForm()
    
    return render(request, 'corporates/wallet_credit.html', {'form': form, 'wallet': wallet})


@login_required
def wallet_debit(request, pk):
    """Debit wallet"""
    wallet = get_object_or_404(Wallet, pk=pk)
    
    if request.method == 'POST':
        form = CreditDebitForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            narration = form.cleaned_data['narration']
            
            try:
                reference = npsb_service.generate_reference('DR')
                response = npsb_service.debit_wallet(
                    account_no=wallet.account_number,
                    amount=amount,
                    narration=narration,
                    transaction_id=reference
                )
                
                # Create transaction record
                Transaction.objects.create(
                    wallet=wallet,
                    transaction_type='DEBIT',
                    amount=amount,
                    narration=narration,
                    transaction_reference=reference,
                    status='SUCCESS' if response.get('status') == 'SUCCESS' else 'FAILED',
                    response_code=response.get('responseCode'),
                    response_message=response.get('message')
                )
                
                if response.get('status') == 'SUCCESS':
                    messages.success(request, f'Successfully debited {amount} from wallet')
                else:
                    messages.warning(request, f'Debit request submitted: {response.get("message")}')
                    
                return redirect('wallet_detail', pk=wallet.pk)
                
            except NPSBAPIError as e:
                messages.error(request, f'API Error: {e.message}')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
    else:
        form = CreditDebitForm()
    
    return render(request, 'corporates/wallet_debit.html', {'form': form, 'wallet': wallet})


@login_required  
def wallet_transfer(request, pk):
    """Transfer from wallet"""
    wallet = get_object_or_404(Wallet, pk=pk)
    
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            transfer_type = form.cleaned_data['transfer_type']
            beneficiary_account = form.cleaned_data['beneficiary_account']
            beneficiary_bank = form.cleaned_data.get('beneficiary_bank', '')
            beneficiary_name = form.cleaned_data.get('beneficiary_name', '')
            amount = form.cleaned_data['amount']
            narration = form.cleaned_data['narration']
            
            try:
                reference = npsb_service.generate_reference('TRF')
                
                if transfer_type == 'external':
                    response = npsb_service.transfer_to_other_bank(
                        sender_account=wallet.account_number,
                        sender_name=wallet.account_name,
                        beneficiary_account=beneficiary_account,
                        beneficiary_bank=beneficiary_bank,
                        beneficiary_name=beneficiary_name,
                        amount=amount,
                        narration=narration,
                        reference=reference
                    )
                else:
                    # Internal transfer (credit beneficiary's 9PSB wallet)
                    response = npsb_service.debit_wallet(
                        account_no=wallet.account_number,
                        amount=amount,
                        narration=f"Transfer to {beneficiary_account}: {narration}",
                        transaction_id=reference
                    )
                
                # Create transaction record
                Transaction.objects.create(
                    wallet=wallet,
                    transaction_type='TRANSFER',
                    amount=amount,
                    narration=narration,
                    transaction_reference=reference,
                    beneficiary_account=beneficiary_account,
                    beneficiary_bank=beneficiary_bank,
                    beneficiary_name=beneficiary_name,
                    status='SUCCESS' if response.get('status') == 'SUCCESS' else 'PENDING',
                    response_code=response.get('responseCode'),
                    response_message=response.get('message')
                )
                
                if response.get('status') == 'SUCCESS':
                    messages.success(request, f'Transfer of {amount} initiated successfully')
                else:
                    messages.warning(request, f'Transfer submitted: {response.get("message")}')
                    
                return redirect('wallet_detail', pk=wallet.pk)
                
            except NPSBAPIError as e:
                messages.error(request, f'API Error: {e.message}')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
    else:
        form = TransferForm()
    
    return render(request, 'corporates/wallet_transfer.html', {'form': form, 'wallet': wallet})


@login_required
def name_enquiry(request):
    """AJAX endpoint for name enquiry"""
    bank_code = request.GET.get('bank_code')
    account_number = request.GET.get('account_number')
    transfer_type = request.GET.get('transfer_type', 'external')
    
    if not account_number:
        return JsonResponse({'success': False, 'error': 'Missing account number'})
    
    try:
        if transfer_type == 'internal':
            response = npsb_service.wallet_enquiry(account_number)
            if response.get('status') == 'SUCCESS':
                data = response.get('data', {})
                return JsonResponse({
                    'success': True,
                    'account_name': data.get('accountName', data.get('name', ''))
                })
        else:
            if not bank_code:
                return JsonResponse({'success': False, 'error': 'Missing bank code'})
            response = npsb_service.other_banks_enquiry(bank_code, account_number)
            if response.get('status') == 'SUCCESS':
                data = response.get('data', {})
                return JsonResponse({
                    'success': True,
                    'account_name': data.get('accountName', data.get('name', ''))
                })
    except NPSBAPIError as e:
        return JsonResponse({'success': False, 'error': e.message})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Account not found'})


# ==================== TRANSACTION VIEWS ====================

@login_required
def transaction_list(request):
    """List all transactions"""
    transactions = Transaction.objects.select_related('wallet', 'wallet__corporate').all()
    
    # Filters
    status = request.GET.get('status', '')
    if status:
        transactions = transactions.filter(status=status)
    
    txn_type = request.GET.get('type', '')
    if txn_type:
        transactions = transactions.filter(transaction_type=txn_type)
    
    paginator = Paginator(transactions, 50)
    page = request.GET.get('page')
    transactions = paginator.get_page(page)
    
    return render(request, 'corporates/transaction_list.html', {
        'transactions': transactions,
        'status': status,
        'txn_type': txn_type,
    })


@login_required
def transaction_requery(request, pk):
    """Requery transaction status"""
    txn = get_object_or_404(Transaction, pk=pk)
    
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
            
            messages.success(request, f'Transaction status: {txn.status}')
        else:
            messages.warning(request, f'Requery response: {response.get("message")}')
            
    except NPSBAPIError as e:
        messages.error(request, f'API Error: {e.message}')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    
    return redirect('wallet_detail', pk=txn.wallet.pk)


# ==================== VERIFICATION VIEWS ====================

@login_required
def verify_bvn(request):
    """AJAX endpoint for BVN verification"""
    bvn = request.GET.get('bvn', '').strip()
    
    if not bvn or len(bvn) != 11:
        return JsonResponse({'success': False, 'error': 'BVN must be 11 digits'})
    
    try:
        data = verification_service.verify_bvn(bvn)
        
        return JsonResponse({
            'success': True,
            'data': {
                'first_name': data.get('firstName', ''),
                'last_name': data.get('lastName', ''),
                'other_names': data.get('middleName', ''),
                'phone_number': data.get('phoneNumber1', '') or data.get('phoneNumber2', ''),
                'email': data.get('email', ''),
                'gender': (data.get('gender', '') or '').upper(),
                'date_of_birth': data.get('dateOfBirth', ''),
                'state_of_origin': data.get('stateOfOrigin', ''),
                'place_of_birth': data.get('stateOfOrigin', ''),
                'address': data.get('residentialAddress', ''),
                'city': data.get('lgaOfResidence', ''),
                'photo': data.get('base64Image', ''),
            }
        })
    except VerificationError as e:
        return JsonResponse({'success': False, 'error': e.message})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def verify_nin(request):
    """AJAX endpoint for NIN verification"""
    nin = request.GET.get('nin', '').strip()
    
    if not nin or len(nin) != 11:
        return JsonResponse({'success': False, 'error': 'NIN must be 11 digits'})
    
    try:
        data = verification_service.verify_nin(nin)
        
        return JsonResponse({
            'success': True,
            'data': {
                'first_name': data.get('firstName', '') or data.get('firstname', ''),
                'last_name': data.get('lastName', '') or data.get('surname', ''),
                'other_names': data.get('middleName', '') or data.get('middlename', ''),
                'phone_number': data.get('phoneNumber1', '') or data.get('telephoneno', '') or data.get('phoneNumber', ''),
                'gender': (data.get('gender', '') or '').upper(),
                'date_of_birth': data.get('dateOfBirth', '') or data.get('birthdate', ''),
                'place_of_birth': data.get('stateOfOrigin', '') or data.get('birthstate', ''),
                'address': data.get('residentialAddress', '') or data.get('residence_address', ''),
                'city': data.get('lgaOfResidence', '') or data.get('residence_town', ''),
                'photo': data.get('base64Image', '') or data.get('photo', ''),
            }
        })
    except VerificationError as e:
        return JsonResponse({'success': False, 'error': e.message})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ==================== CUSTOMER VIEWS ====================

@login_required
def customer_list(request):
    """List all customers"""
    customers = Customer.objects.all()
    
    search = request.GET.get('search', '')
    if search:
        customers = customers.filter(first_name__icontains=search) | customers.filter(last_name__icontains=search) | customers.filter(bvn__icontains=search)
    
    status = request.GET.get('status', '')
    if status:
        customers = customers.filter(status=status)
    
    paginator = Paginator(customers, 20)
    page = request.GET.get('page')
    customers = paginator.get_page(page)
    
    return render(request, 'corporates/customer_list.html', {
        'customers': customers,
        'search': search,
        'status': status,
    })


@login_required
def customer_create(request):
    """Create new customer"""
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.created_by = request.user
            customer.save()
            messages.success(request, f'Customer "{customer.full_name}" created successfully.')
            return redirect('customer_detail', pk=customer.pk)
    else:
        form = CustomerForm()
    
    return render(request, 'corporates/customer_form.html', {'form': form, 'title': 'Add Customer'})


@login_required
def customer_detail(request, pk):
    """View customer details"""
    customer = get_object_or_404(Customer, pk=pk)
    wallets = customer.wallets.all()
    
    return render(request, 'corporates/customer_detail.html', {
        'customer': customer,
        'wallets': wallets,
    })


@login_required
def customer_edit(request, pk):
    """Edit customer"""
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated successfully.')
            return redirect('customer_detail', pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)
    
    return render(request, 'corporates/customer_form.html', {
        'form': form,
        'customer': customer,
        'title': 'Edit Customer'
    })


@login_required
def customer_delete(request, pk):
    """Delete customer"""
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        name = customer.full_name
        customer.delete()
        messages.success(request, f'Customer "{name}" deleted successfully.')
        return redirect('customer_list')
    
    return render(request, 'corporates/customer_confirm_delete.html', {'customer': customer})


@login_required
def customer_wallet_generate(request, pk):
    """Generate wallet for customer"""
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        try:
            wallet_data = {
                "bvn": customer.bvn,
                "dateOfBirth": customer.date_of_birth.strftime('%d/%m/%Y'),
                "gender": 1 if customer.gender == 'MALE' else 0,
                "lastName": customer.last_name,
                "otherNames": f"{customer.first_name} {customer.other_names or ''}".strip(),
                "phoneNo": customer.phone_number,
                "transactionTrackingRef": npsb_service.generate_reference('CWT'),
                "placeOfBirth": customer.place_of_birth,
                "address": customer.address,
                "nationalIdentityNo": customer.nin or "",
                "nextOfKinPhoneNo": customer.next_of_kin_phone,
                "nextOfKinName": customer.next_of_kin_name,
                "email": customer.email,
            }
            
            response = npsb_service.open_wallet(wallet_data)
            
            if response.get('status') == 'SUCCESS':
                data = response.get('data', {})
                
                wallet = Wallet.objects.create(
                    wallet_type='INDIVIDUAL',
                    customer=customer,
                    account_number=data.get('accountNumber'),
                    account_name=data.get('fullName', customer.full_name),
                    npsb_customer_id=data.get('customerID'),
                    npsb_order_ref=data.get('orderRef'),
                    status='ACTIVE'
                )
                
                customer.status = 'ACTIVE'
                customer.save()
                
                messages.success(request, f'Wallet created successfully. Account Number: {wallet.account_number}')
                return redirect('wallet_detail', pk=wallet.pk)
            else:
                messages.error(request, f'Failed to create wallet: {response.get("message", "Unknown error")}')
                
        except NPSBAPIError as e:
            messages.error(request, f'API Error: {e.message}')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'corporates/customer_wallet_generate.html', {'customer': customer})
