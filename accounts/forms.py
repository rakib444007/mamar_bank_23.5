from django import forms 
from .models import UserAddress,UserBankAccount
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from django.contrib.auth.forms import PasswordChangeForm
from .constants import ACCOUNT_TYPE,GENDER_TYPE
class UserRegistrationForm(UserCreationForm):
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=GENDER_TYPE)
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)
    street_address = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    postal_code = forms.IntegerField()
    country = forms.CharField(max_length=100)
    class Meta:
        model = User
        fields = ['username','password1','password2','first_name','last_name','email',
                  'account_type','gender','street_address','postal_code','birth_date','city','country']
        
        #when we save form.save from view . then 3 of database get there data from userregistration from and save data in database.
        #form.save()
    def save(self,commit=True):
        #super key word diya user ar data niya asslam
        user = super().save(commit=False)#aytar mane hocce amra akhon data database save korbo nah
        if commit == True:
            user.save()#user model e data save korlam
            account_type = self.cleaned_data.get('account_type')
            gender = self.cleaned_data.get('gender')
            postal_code = self.cleaned_data.get('postal_code')
            country = self.cleaned_data.get('country')
            birth_date = self.cleaned_data.get('birth_date')
            city = self.cleaned_data.get('city')
            street_address = self.cleaned_data.get('street_address')

            UserAddress.objects.create(
                user=user,
                postal_code=postal_code,
                country=country,
                city = city,
                street_address = street_address

            )
            UserBankAccount.objects.create(

                user = user,
                account_type = account_type,
                gender = gender,
                birth_date = birth_date,
                account_no = 100000 + user.id
            )
        return user

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({

                'class': (
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500'

                )
            })

            

class UserUpdateForm(forms.ModelForm):
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=GENDER_TYPE)
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)
    street_address = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    postal_code = forms.IntegerField()
    country = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['first_name','last_name','email']
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)  #model ke init korlam to override and push new data . Means updated data
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': (
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500'
                )
            })
        
        #jodi user er account thake
        if self.instance:
            try:
                user_account = self.instance.account
                user_address = self.instance.address
               
            
            except UserBankAccount.DoesNotExist:
                user_account = None
                user_address = None

            if user_account:
                self.fields['account_type'].initial = user_account.account_type
                self.fields['gender'].initial = user_account.gender
                self.fields['birth_date'].initial = user_account.birth_date
                self.fields['street_address'].initial = user_address.street_address
                self.fields['city'].initial = user_address.city
                self.fields['postal_code'].initial = user_address.postal_code
                self.fields['country'].initial = user_address.country

    def save(self,commit = True):
        user = super().save(commit=False)
        if commit :
            user.save()

            user_accout , created = UserBankAccount.objects.get_or_create(user=user) 
            user_address , created = UserAddress.objects.get_or_create(user=user) 

            user_accout.account_type = self.cleaned_data['account_type']
            user_accout.gender = self.cleaned_data['gender']
            user_accout.birth_date = self.cleaned_data['birth_date']
            user_accout.save()


            user_address.street_address = self.cleaned_data['street_address']
            user_address.city = self.cleaned_data['city']
            user_address.postal_code = self.cleaned_data['postal_code']
            user_address.country = self.cleaned_data['country'] 
            user_address.save()
        return user




class Password_Change_Form(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(Password_Change_Form, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': (
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500'
                )
            })
