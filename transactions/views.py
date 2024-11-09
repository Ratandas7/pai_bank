from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.generic import CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from transactions.models import Transaction
from django.urls import reverse_lazy
from transactions.forms import DepositForm, WithdrawForm, LoanRequestForm, TransferForm
from transactions.constants import DEPOSIT, WITHDRAW, LOAN, LOAN_PAID, TRANSFER
from django.contrib import messages
from datetime import datetime
from django.db.models import Sum
from django.views import View
from accounts.models import UserBankAccount
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
# Create your views here.

def send_transaction_email(user, amount, subject, template):
    message = render_to_string(template, {
        'user' : user,
        'amount' : amount,
    })
    send_email = EmailMultiAlternatives(subject, '', to=[user.email])
    send_email.attach_alternative(message, "text/html")
    send_email.send()


class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = 'transactions/transaction_form.html'
    model = Transaction
    title = ''
    success_url = reverse_lazy('transaction_report')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account' : self.request.user.account
        })
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title' : self.title
        })
        return context



class DepositMoneyView(TransactionCreateMixin):
    form_class = DepositForm
    title = 'Deposit'

    def get_initial(self):
        initial = {'transaction_type' : DEPOSIT}
        return initial
    
    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        account.balance += amount
        account.save(
            update_fields = ['balance']
        )

        messages.success(
            self.request, f'{"{:,.2f}".format(float(amount))}$ was deposited to your account successfully'
        )

        # mail_subject = 'Deposit Message'
        # message = render_to_string('transactions/deposit_email.html', {
        #     'user' : self.request.user,
        #     'amount' : amount,
        # })
        # to_email = self.request.user.email
        # send_email = EmailMultiAlternatives(mail_subject, '', to=[to_email])
        # send_email.attach_alternative(message, "text/html")
        # send_email.send()

        send_transaction_email(self.request.user, amount, "Deposit Message", "transactions/deposit_email.html")

        return super().form_valid(form)


class WithdrawMoneyView(TransactionCreateMixin):
    form_class = WithdrawForm
    title = 'Withdraw Money'

    def get_initial(self):
        initial = {"transaction_type" : WITHDRAW}
        return initial
    
    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        self.request.user.account.balance -= form.cleaned_data.get('amount')

        self.request.user.account.save(update_fields = ['balance'])

        messages.success(
            self.request, f'Successfully withdrawn {"{:,.2f}".format(float(amount))}$ from your account'
        )

        send_transaction_email(self.request.user, amount, "Withdraw Message", "transactions/withdraw_email.html")

        return super().form_valid(form)
    


class LoanRequestView(TransactionCreateMixin):
    form_class = LoanRequestForm
    title = 'Request For Loan'

    def get_initial(self):
        initial = {'transaction_type' : LOAN}
        return initial
    
    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')

        current_loan_count = Transaction.objects.filter(account = self.request.user.account, transaction_type = 3, loan_approve = True).count()

        if current_loan_count >= 3:
            return HttpResponse("You have cross the loan limits")

        messages.warning(
            self.request, f'Loan request for {"{:,.2f}".format(float(amount))}$ submitted successfully'
        )

        send_transaction_email(self.request.user, amount, "Loan Request Message", "transactions/loan_email.html")

        return super().form_valid(form)
    

class TransactionReportView(LoginRequiredMixin, ListView):
    template_name = 'transactions/transaction_report.html'
    model = Transaction
    balance = 0
    context_object_name = 'transactions'

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            account = self.request.user.account
        )

        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

            queryset = queryset.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date)

            self.balance = Transaction.objects.filter(
                timestamp__date__gte=start_date, timestamp__date__lte=end_date
            ).aggregate(Sum('amount'))['amount__sum']

        else:
            self.balance = self.request.user.account.balance

        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account' : self.request.user.account
        })
        return context
    


class LoanListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'transactions/loan_request.html'
    context_object_name = 'loans'

    def get_queryset(self):
        user_account = self.request.user.account
        queryset = Transaction.objects.filter(account=user_account, transaction_type=LOAN)
        print(queryset)
        return queryset
    


class PayLoanView(LoginRequiredMixin, View):

    def get(self, request, loan_id):
        loan = get_object_or_404(Transaction, id=loan_id)
        print(loan)
        if loan.loan_approve:
            user_account = loan.account
            if loan.amount < user_account.balance:
                user_account.balance -= loan.amount
                loan.balance_after_transaction = user_account.balance
                user_account.save()
                loan.loan_approve = True
                loan.transaction_type = LOAN_PAID
                loan.save()

                messages.success(
                    self.request, f'Loan paid successfully'
                )
                
                return redirect('transaction_report')
           
            else:
                messages.error(
                    self.request, f"Loan amount is greater than available balance"
                )
        return redirect('loan_list')
    

class TransferMoneyView(TransactionCreateMixin):
    form_class = TransferForm
    title = 'Money Transfer'

    def get_initial(self):
        initial = {'transaction_type' : TRANSFER}
        return initial
    
    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        to_account_number = form.cleaned_data.get('to_account')

        try:
            to_account = UserBankAccount.objects.get(account_no=to_account_number)

        except UserBankAccount.DoesNotExist:
            form.add_error('to_account', 'The account does not exist.')
            
            return self.form_invalid(form)
        
        account = self.request.user.account
        account.balance -= amount
        to_account.balance += amount

        account.save(
            update_fields = ['balance']
        )

        to_account.save(
            update_fields = ['balance']
        )

        messages.success(
            self.request, f'{"{:,.2f}".format(float(amount))}$ was transferred from your account successfully.'
        )

        send_transaction_email(self.request.user, amount, "Money Transfer Message", "transactions/transfer_email.html")

        send_transaction_email(to_account.user, amount, "Money Receiver Message", "transactions/receiver_email.html")
        
        return super().form_valid(form)

