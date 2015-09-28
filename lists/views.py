from django.shortcuts import render, redirect
from django.http import HttpResponse
from lists.models import Item

# Create your views here.

def home_page(request):
    return render(request, 'index.html')


def view_list(request):
    total_items = Item.objects.count()
    if total_items == 0:
        comment = "yey, waktunya berlibur"
    elif total_items < 5:
        comment = "sibuk tapi santai"
    else:
        comment = "oh tidak"
    
    data = {
        'items': Item.objects.all(),
        'comment': comment,
    }
    
    return render(request, 'list.html', data)


def new_list(request):
    Item.objects.create(text=request.POST['item_text'])
    return redirect('/lists/the-only-list-in-the-world/')