from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.forms import widgets
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


class RegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget = widgets.TextInput(attrs={'placeholder': '请输入用户名', 'class': 'form-control'})
        self.fields['email'].widget = widgets.EmailInput(attrs={'placeholder': '电子邮件', 'class': 'form-control'})
        self.fields['password1'].widget = widgets.PasswordInput(
            attrs={'placeholder': '输入密码', 'class': 'form-control'})
        self.fields['password2'].widget = widgets.PasswordInput(
            attrs={'placeholder': '再次输入密码', 'class': 'form-control'})

    def clean_email(self):
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise ValidationError('该邮箱已存在')
        return email

    class Meta:
        model = get_user_model()
        fields = ("username", "email")


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget = widgets.TextInput(attrs={'placeholder': '输入用户名', 'class': 'form-control mb-xl-4'})
        self.fields['password'].widget = widgets.PasswordInput(
            attrs={'placeholder': '输入密码', 'class': 'form-control mb-xl-4'})
