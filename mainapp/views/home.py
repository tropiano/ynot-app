from django.views.generic import TemplateView
from django.shortcuts import redirect


class HomeView(TemplateView):
    template_name = "mainapp/home.html"

    def post(self, request, *args, **kwargs):
        # Handle the form submission logic here
        email = request.POST["email"]

        # Save the email in the session object
        request.session["email"] = email
        print("email", request.session["email"])

        # Redirect to the threads authorization flow
        return redirect("threads_start_oauth_flow")
