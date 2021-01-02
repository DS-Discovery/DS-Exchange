from django.shortcuts import render


def status_400(request, exception):
    response = render(request, "400.html")
    response.status_code = 400
    return response


def status_403(request, exception):
    response = render(request, "403.html")
    response.status_code = 403
    return response


def status_404(request, exception):
    response = render(request, "404.html")
    response.status_code = 404
    return response
