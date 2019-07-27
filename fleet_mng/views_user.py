from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User, Group
from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render


class UserForm(forms.Form):
    username = forms.CharField(max_length=191, label="Nazwa użytkownika:")
    password = forms.CharField(label="Hasło:", widget=forms.PasswordInput())
    password_confirm = forms.CharField(label="Powtórz hasło:", widget=forms.PasswordInput())
    group = forms.ChoiceField(label="Group:")

    def __init__(self, *args, **kwargs):
        search_str = kwargs.pop('search_str', None)
        super().__init__(*args, **kwargs)
        groups = Group.objects.filter(name__in=('viewer', 'user', 'admin'))
        self.fields['group'].initial = search_str
        self.fields['group'].choices = [(None, '---------')]
        self.fields['group'].choices.extend([(x.id, x) for x in groups])

    def clean(self):
        cleaned_data = super(UserForm, self).clean()

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
    users = User.objects.all()
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
        form = UserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            group = Group.objects.get(pk=int(form.cleaned_data.get('group')))
            user = User.objects.create_user(username, None, password)
            user.save()
            # adding user to group
            group.user_set.add(user)
            return HttpResponseRedirect('/')
    else:
        form = UserForm()

    return render(request, 'fleet_mng/user_new.html', {'form': form})
