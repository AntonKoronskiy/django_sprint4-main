from django.shortcuts import render


# Create your views here.
def about(request):
    template_name = 'pages/about.html'
    return render(request, template_name)


def rules(request):
    template_name = 'pages/rules.html'
    return render(request, template_name)


def page_403(request, reason=''):
    template_name = 'pages/403csrf.html'
    return render(request, template_name, status=403)


def page_404(request, exception):
    template_name = 'pages/404.html'
    return render(request, template_name, status=404)


def page_500(request):
    template_name = 'pages/500.html'
    return render(request, template_name, status=500)
