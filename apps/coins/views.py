from django.shortcuts import render
from django.views.generic import TemplateView, FormView, View, ListView

# Create your views here.

class IndexView(TemplateView):
    template_name = 'index.html'

class ExchangeRateView(View):
    """
    Displaying the exchange rate based on the amount.
    If no amount entered will take the minimum transaction amount
    """
    def post(self, request, *args, **kwargs):
        convert_from = CURRENCY[request.POST.get('from')]
        convert_to = CURRENCY[request.POST.get('to')]
        amount = request.POST.get('amount')
        
        if amount:
            params =  {
                    "from": convert_from,
                    "to": convert_to,
                    "amount": amount
                }
            method = "getExchangeAmount"
        else:
            params =  {
                    "from": convert_from,
                    "to": convert_to,
                }
            method = 'getMinAmount'
        data = changelly_transaction(method,params)
        if not data.get('error'):
            request.session['convert_from'] = convert_from
            request.session['convert_to'] = convert_to
            request.session['amount'] = amount
            if not amount:
                request.session['amount'] = '1'
        return HttpResponse(json.dumps(data), content_type='application/json')