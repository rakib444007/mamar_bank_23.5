from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.http import HttpResponse
from django.views.generic import CreateView, ListView,FormView
from transactions.constants import DEPOSIT, WITHDRAWAL,LOAN, LOAN_PAID,TRANSFER_MONEY
from datetime import datetime
from django.db.models import Sum
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from accounts.models import UserBankAccount,UserAddress
from transactions.forms import (
    DepositForm,
    WithdrawForm,
    LoanRequestForm,
    MoneyTransferForm,
)
from transactions.models import Transaction

class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = 'transactions/transaction_form.html'
    model = Transaction
    title = ''
    success_url = reverse_lazy('transaction_report')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account
        })
        print('My new account: ',kwargs['account'].account_type)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) # template e context data pass kora
        context.update({
            'title': self.title
        })

        return context

def send_transaction_email(user, amount, subject, template):
        message = render_to_string(template, {
            'user' : user,
            'amount' : amount,
        })
        send_email = EmailMultiAlternatives(subject, '', to=[user.email])
        send_email.attach_alternative(message, "text/html")
        send_email.send()


def send_transfer_money_email(user,user_account_no, amount, subject, template):
        message = render_to_string(template, {
            'user' : user,
            'user_account_no' : user_account_no,
            'amount' : amount,
        })
        send_email = EmailMultiAlternatives(subject, '', to=[user.email])
        send_email.attach_alternative(message, "text/html")
        send_email.send()


        



class DepositMoneyView(TransactionCreateMixin):
    form_class = DepositForm
    title = 'Deposit'

    def get_initial(self):
        initial = {'transaction_type': DEPOSIT}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        # if not account.initial_deposit_date:
        #     now = timezone.now()
        #     account.initial_deposit_date = now
        account.balance += amount # amount = 200, tar ager balance = 0 taka new balance = 0+200 = 200
        account.save(
            update_fields=[
                'balance'
            ]
        )

        messages.success(
            self.request,
            f'{"{:,.2f}".format(float(amount))}$ was deposited to your account successfully'
        )
        send_transaction_email(self.request.user, amount, "Deposite Message", "transactions/deposite_email.html")

        return super().form_valid(form)


class WithdrawMoneyView(TransactionCreateMixin):
    form_class = WithdrawForm
    title = 'Withdraw Money'

    def get_initial(self):
        initial = {'transaction_type': WITHDRAWAL}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')

        self.request.user.account.balance -= form.cleaned_data.get('amount')
        # balance = 300
        # amount = 5000
        self.request.user.account.save(update_fields=['balance'])

        messages.success(
            self.request,
            f'Successfully withdrawn {"{:,.2f}".format(float(amount))}$ from your account'
        )
        send_transaction_email(self.request.user, amount, "Withdrawal Message", "transactions/withdrawal_email.html")
        return super().form_valid(form)

class LoanRequestView(TransactionCreateMixin):
    form_class = LoanRequestForm
    title = 'Request For Loan'

    def get_initial(self):
        initial = {'transaction_type': LOAN}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        current_loan_count = Transaction.objects.filter(
            account=self.request.user.account,transaction_type=3,loan_approve=True).count()
        if current_loan_count >= 3:
            return HttpResponse("You have cross the loan limits")
        messages.success(
            self.request,
            f'Loan request for {"{:,.2f}".format(float(amount))}$ submitted successfully'
        )
        send_transaction_email(self.request.user, amount, "Loan Request Message", "transactions/loan_email.html")
        return super().form_valid(form)
    
class TransactionReportView(LoginRequiredMixin, ListView):
    template_name = 'transactions/transaction_report.html'
    model = Transaction
    balance = 0 # filter korar pore ba age amar total balance ke show korbe
    
    def get_queryset(self):
        # get_queryset ar maddome amra database theke user account filter kore niya aslam .
        #ay khane queryset ar modde filter kora user ar transaction table data database theke niya contain kore rhakbe . 
        queryset = super().get_queryset().filter(
            account=self.request.user.account
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
       
        return queryset.distinct() # unique queryset hote hobe
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account': self.request.user.account
        })

        return context
    
        
class PayLoanView(LoginRequiredMixin, View):
    def get(self, request, loan_id):
        # in loan variable we contain pk id wala user transaction model object 
        loan = get_object_or_404(Transaction, id=loan_id)
        print('This is loan: ',loan)
        if loan.loan_approve:
            user_account = loan.account
                # Reduce the loan amount from the user's balance
                # 5000, 500 + 5000 = 5500
                # balance = 3000, loan = 5000
            if loan.amount < user_account.balance:
                user_account.balance -= loan.amount
                loan.balance_after_transaction = user_account.balance
                user_account.save()
                loan.transaction_type = LOAN_PAID 
                loan.save()
                return redirect('loan_list')
            else:
                messages.error(
            self.request,
            f'Loan amount is greater than available balance'
        )

        return redirect('loan_list')


class LoanListView(LoginRequiredMixin,ListView):
    model = Transaction
    template_name = 'transactions/loan_request.html'
    context_object_name = 'loans' # loan list ta ei loans context er moddhe thakbe
    
    def get_queryset(self):
        user_account = self.request.user.account
        queryset = Transaction.objects.filter(account=user_account,transaction_type=3)
        print('hello query',queryset)
        return queryset
    
# def send_transfer_money_email(user,user_account_no, amount, subject, template):
#         message = render_to_string(template, {
#             'user' : user,
#             'user_account_no' : user_account_no,
#             'amount' : amount,
#         })
#         send_email = EmailMultiAlternatives(subject, '', to=[user.email])
#         send_email.attach_alternative(message, "text/html")
#         send_email.send()


        
class MoneyTransfervView(LoginRequiredMixin, FormView):
    template_name = 'transactions/transfer_money.html'
    form_class = MoneyTransferForm
    success_url = reverse_lazy('transaction_report')
    title = 'Transfer Money'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account
        })
        return kwargs
    
    def get_initial(self):
        initial = {'transaction_type': TRANSFER_MONEY}
        return initial

    def form_valid(self, form):
        account_no = form.cleaned_data.get('transfared_user_account_no')
        amount = form.cleaned_data.get('amount')
        try:
            another_account = UserBankAccount.objects.get(account_no=account_no)
        except UserBankAccount.DoesNotExist:
            form.add_error('transfared_user_account_no', f"The account number {account_no} does not exist.")
            return self.form_invalid(form)
        
        if self.request.user.account.balance < amount:
            form.add_error('amount', "Insufficient balance for this transfer.")
            return self.form_invalid(form)
        self.request.user.account.balance -= amount
        another_account.balance += amount
        self.request.user.account.save(update_fields=['balance'])
        another_account.save(update_fields=['balance'])
        form.save()  
        messages.success(
            self.request,
            f'Successfully transferred ${"{:,.2f}".format(float(amount))} to account number {account_no}.'
        )
        
        send_transfer_money_email(self.request.user,account_no,amount,'Transfer Money message','transactions/transfer_email_you.html')
        send_transfer_money_email(another_account.user,self.request.user.account.account_no,amount,'Transfer Money message','./transactions/money_transfer_other.html')
        
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({

            'title': self.title
            
        })
        return context
