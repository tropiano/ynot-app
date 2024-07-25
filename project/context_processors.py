import os


def export_vars(request):
    data = {}
    data["STRIPE_URL_YEAR"] = os.environ.get("STRIPE_URL_YEAR", "")
    data["STRIPE_URL_LIFE"] = os.environ.get("STRIPE_URL_LIFE", "")
    data["THREADS_APP_ID"] = os.environ.get("THREADS_APP_ID", "")
    data["THREADS_REDIRECT_URI"] = os.environ.get("THREADS_REDIRECT_URI", "")
    data["THREADS_SCOPE"] = os.environ.get("THREADS_SCOPE", "")

    return data
