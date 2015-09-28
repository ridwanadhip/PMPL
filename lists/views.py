from django.shortcuts import render, redirect
from django.http import HttpResponse
from lists.models import Item, List

# Create your views here.

def home_page(request):
    return render(request, 'index.html')


def view_list(request, list_id):
    list_ = List.objects.get(id=int(list_id))

    total_items = Item.objects.count()
    if total_items == 0:
        comment = "yey, waktunya berlibur"
    elif total_items < 5:
        comment = "sibuk tapi santai"
    else:
        comment = "oh tidak"
    
    data = {
        'comment': comment,
        'list': list_,
    }
    
    return render(request, 'list.html', data)


def new_list(request):
    list_ = List.objects.create()
    Item.objects.create(text=request.POST['item_text'], list=list_)
    return redirect('/lists/{}/'.format(list_.id))


def add_item(request, list_id):
    list_ = List.objects.get(id=int(list_id))
    Item.objects.create(text=request.POST['item_text'], list=list_)
    return redirect('/lists/{}/'.format(list_.id))