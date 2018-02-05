
from django.urls import path
from django.views.generic import TemplateView, FormView, View, ListView
from . views import IndexView, ExchangeRateView

app_name = 'coins'
urlpatterns = [
    path('', IndexView.as_view(), name = 'home'),
    path('exchange/', TemplateView.as_view(template_name='exchange.html'), name='exchange'),

]