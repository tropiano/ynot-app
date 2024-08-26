from django.views.generic import TemplateView
from usermodel.models import User


class PaymentConfirmView(TemplateView):
    model = User
    template_name = "mainapp/payment_confirm.html"

    # def get_context_data(self, **kwargs):
    # user_name = self.request.user.username
    # User.objects.filter(username=user_name).update(is_paid=1)
