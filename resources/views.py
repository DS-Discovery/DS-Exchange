from django.shortcuts import render

def index(request):
    content = "<i>load</i> text here!"
    return render(request, 'one_column_view.html', {"content": content})
