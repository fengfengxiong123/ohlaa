from django.urls import path, re_path
from . import views
from .forms import LoginForm

app_name = 'accounts'

urlpatterns = [
    path('account/history/', views.HistoryView.as_view(), name='history'),
    re_path(r'^register/$', views.RegisterView.as_view(success_url='/'), name='register'),
    re_path(r'^login/$', views.LoginView.as_view(success_url='/'), name='login',kwargs={'authentication_form':LoginForm}),
    re_path(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    path(r'account/result.html', views.account_result, name='result'),
    re_path(r'^upload/$',views.upload, name='upload'),
]
