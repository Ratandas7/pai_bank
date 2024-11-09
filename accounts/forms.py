from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from accounts.constants import ACCOUNT_TYPE, GENDER_TYPE
from accounts.models import UserBankAccount, UserAddress


class UserRegistrationForm(UserCreationForm):
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)
    gender_type = forms.ChoiceField(choices=GENDER_TYPE)
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type' : 'date'}))
    street_address = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    postal_code = forms.IntegerField()
    country = forms.CharField(max_length=100)
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'account_type', 'gender_type', 'birth_date', 'street_address', 'city', 'postal_code', 'country']

    
    def save(self, commit = True):
        our_user = super().save(commit=False)
        if commit == True:
            our_user.save()
            account_type = self.cleaned_data.get('account_type')
            gender_type = self.cleaned_data.get('gender_type')
            birth_date = self.cleaned_data.get('birth_date')
            street_address = self.cleaned_data.get('street_address')
            city = self.cleaned_data.get('city')
            postal_code = self.cleaned_data.get('postal_code')
            country = self.cleaned_data.get('country')
            UserBankAccount.objects.create(
                user = our_user,
                account_type = account_type,
                gender_type = gender_type,
                birth_date = birth_date,
                account_no = 1000000+our_user.id
            )
            UserAddress.objects.create(
                user = our_user,
                street_address = street_address,
                city = city,
                postal_code = postal_code,
                country = country
            )
        return our_user
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            # print(field)
            self.fields[field].widget.attrs.update({
                'class' : (
                    # 'appearance-none block w-full bg-gray-200 '
                    # 'text-gray-700 border border-gray-200 rounded '
                    # 'py-2 px-3 leading-tight focus:outline-none '
                    # 'focus:bg-white focus:border-gray-500'
                    'block w-full rounded-md border-0 px-3.5 py-2 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm/6'
                )
            })




class UserUpdateForm(forms.ModelForm):
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)
    gender_type = forms.ChoiceField(choices=GENDER_TYPE)
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type' : 'date'}))
    street_address = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    postal_code = forms.IntegerField()
    country = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            # print(field)
            self.fields[field].widget.attrs.update({
                'class' : (
                    # 'appearance-none block w-full bg-gray-200 '
                    # 'text-gray-700 border border-gray-200 rounded '
                    # 'py-2 px-3 leading-tight focus:outline-none '
                    # 'focus:bg-white focus:border-gray-500'
                    'block w-full rounded-md border-0 px-3.5 py-2 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm/6'
                )
            })

        if 'username' in self.fields:
            self.fields['username'].widget.attrs['readonly'] = True
        

        if self.instance:
            try:
                user_account = self.instance.account
                user_address = self.instance.address
            except UserBankAccount.DoesNotExist:
                user_account = None
                user_address = None

            if user_account:
                self.fields['account_type'].initial = user_account.account_type
                self.fields['gender_type'].initial = user_account.gender_type
                self.fields['birth_date'].initial = user_account.birth_date
                self.fields['street_address'].initial = user_address.street_address
                self.fields['city'].initial = user_address.city
                self.fields['postal_code'].initial = user_address.postal_code
                self.fields['country'].initial = user_address.country

    def save(self, commit = True):
        our_user = super().save(commit=False)

        if commit == True:
            our_user.save()

            user_account, created = UserBankAccount.objects.get_or_create(user=our_user)
            user_address, created = UserAddress.objects.get_or_create(user=our_user)

            user_account.account_type = self.cleaned_data['account_type']
            user_account.gender_type = self.cleaned_data['gender_type']
            user_account.birth_date = self.cleaned_data['birth_date']
            user_account.save()

            user_address.street_address = self.cleaned_data['street_address']
            user_address.city = self.cleaned_data['city']
            user_address.postal_code = self.cleaned_data['postal_code']
            user_address.country = self.cleaned_data['country']
            user_address.save()
        return our_user

