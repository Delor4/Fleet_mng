from django.contrib.admin.models import LogEntry, CHANGE, ADDITION
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Group
from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render

from fleet_mng.models import log_user_entry


class NewUserForm(forms.Form):
    username = forms.CharField(max_length=191, label="Nazwa użytkownika:")
    password = forms.CharField(label="Hasło:", widget=forms.PasswordInput(attrs={'autocomplete': "new-password"}))
    password_confirm = forms.CharField(label="Powtórz hasło:",
                                       widget=forms.PasswordInput(attrs={'autocomplete': "new-password"}))
    group = forms.ChoiceField(label="Typ:")
    blocked = forms.BooleanField(label="zablokowany", widget=forms.CheckboxInput, required=False)

    def __init__(self, *args, **kwargs):
        search_str = kwargs.pop('search_str', None)
        super().__init__(*args, **kwargs)
        groups = Group.objects.filter(name__in=('viewer', 'user', 'admin'))
        self.fields['group'].initial = search_str
        self.fields['group'].choices = [(None, '---------')]
        self.fields['group'].choices.extend([(x.id, x) for x in groups])

    def clean(self):
        cleaned_data = super(NewUserForm, self).clean()

        username = cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Duplicated username!')

        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if not password or password == '':
            raise forms.ValidationError('Empty password!')

        if not (password == password_confirm):
            raise forms.ValidationError('Different passwords!')
        group = int(cleaned_data.get('group'))
        groups_id = [x.id for x in Group.objects.filter(name__in=('viewer', 'user', 'admin'))]

        if group not in groups_id:
            raise forms.ValidationError('Select group!')


# pokazuje listę użytkowników
# /user/
@login_required
@permission_required('auth.view_user')
def show_users(request):
    users = User.objects.filter(is_superuser=False).order_by('-is_active')
    return render(request, 'fleet_mng/users.html', {'users_list': users})


# pokazuje użytkownika
# /user/<int:pk>/
@login_required
@permission_required('auth.view_user')
def show_user(request, pk):
    user = User.objects.get(pk=pk)
    return render(request, 'fleet_mng/user.html', {'user': user})


# Obsługa formularza dodawania użytkownika
# /user/new/    => user_new.html
@login_required
@permission_required('auth.add_user')
def new_user(request):
    if request.user.has_perm('auth.add_user') and \
            request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            group = Group.objects.get(pk=int(form.cleaned_data.get('group')))
            user = User.objects.create_user(username, None, password)

            user.is_active = not form.cleaned_data.get('blocked')
            user.save()
            # adding user to group
            group.user_set.add(user)
            log_user_entry(request, user, ADDITION, 'User added.')
            return HttpResponseRedirect('/user/')
    else:
        form = NewUserForm()

    return render(request, 'fleet_mng/user_new.html', {'form': form})


class UserUpdatePassForm(forms.Form):
    password = forms.CharField(label="Hasło:", widget=forms.PasswordInput(attrs={'autocomplete': "new-password"}))
    password_confirm = forms.CharField(label="Powtórz hasło:",
                                       widget=forms.PasswordInput(attrs={'autocomplete': "new-password"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(UserUpdatePassForm, self).clean()

        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if not password or password == '':
            raise forms.ValidationError('Empty password!')

        if not (password == password_confirm):
            raise forms.ValidationError('Different passwords!')


# Obsługa formularza ustawiania hasła użytkownika
# /user/<int:pk>/pass/    => user_new.html
@login_required
@permission_required('auth.change_user')
def change_user_pass(request, pk):
    if request.user.has_perm('auth.change_user') and \
            request.method == 'POST':
        form = UserUpdatePassForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            user = User.objects.get(id=pk)
            user.password = password
            user.save()
            log_user_entry(request, user, CHANGE, 'User pass changed.')
            return HttpResponseRedirect('/user/')
    else:
        form = UserUpdatePassForm()

    return render(request, 'fleet_mng/user_new.html', {'form': form})


class UserUpdateForm(forms.Form):
    username = forms.CharField(max_length=191, label="Nazwa użytkownika:", disabled=True, required=False)
    group = forms.ChoiceField(label="Typ:")
    blocked = forms.BooleanField(label="zablokowany", widget=forms.CheckboxInput, required=False)

    def __init__(self, *args, **kwargs):
        search_str = kwargs.pop('search_str', None)
        super().__init__(*args, **kwargs)
        groups = Group.objects.filter(name__in=('viewer', 'user', 'admin'))
        self.fields['group'].initial = search_str
        self.fields['group'].choices = [(None, '---------')]
        self.fields['group'].choices.extend([(x.id, x) for x in groups])

    def clean(self):
        cleaned_data = super(UserUpdateForm, self).clean()

        group = int(cleaned_data.get('group'))
        groups_id = [x.id for x in Group.objects.filter(name__in=('viewer', 'user', 'admin'))]

        if group not in groups_id:
            raise forms.ValidationError('Select group!')


# Obsługa formularza zmiany danych użytkownika
# /user/<int:pk>/edit/    => user_new.html
@login_required
@permission_required('auth.change_user')
def user_edit(request, pk):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST)
        if form.is_valid():
            user = User.objects.get(id=pk)
            # user.username = form.cleaned_data.get('username')
            # removing from old groups
            for user_group in Group.objects.filter(name__in=('viewer', 'user', 'admin')):
                user_group.user_set.remove(user)
            group = Group.objects.get(pk=int(form.cleaned_data.get('group')))
            # adding user to group
            group.user_set.add(user)
            # set is_active
            user.is_active = not form.cleaned_data.get('blocked')
            user.save()
            log_user_entry(request, user, CHANGE, 'User data changed.')
        return HttpResponseRedirect('/user/')
    else:
        user = User.objects.get(id=pk)
        form = UserUpdateForm(initial={'username': user.username,
                                       'group': user.groups.all()[0].id,
                                       'blocked': not user.is_active,
                                       })

        return render(request, 'fleet_mng/user_new.html', {'form': form})
