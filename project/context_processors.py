import os


def export_vars(request):
    data = {}
    data["STRIPE_URL_YEAR"] = os.environ.get("STRIPE_URL_YEAR", "")
    data["STRIPE_URL_LIFE"] = os.environ.get("STRIPE_URL_LIFE", "")

    return data
