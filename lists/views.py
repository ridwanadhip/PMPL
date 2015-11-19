from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from lists.models import Item, List

# Create your views here.

def home_page(request):
    total_items = Item.objects.count()
    if total_items == 0:
        comment = "yey, waktunya berlibur"
    elif total_items < 5:
        comment = "sibuk tapi santai"
    else:
        comment = "oh tidak"
    
    data = {
        'comment': comment,
    }
    
    return render(request, 'index.html', data)


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
    item = Item.objects.create(text=request.POST['item_text'], list=list_)
    try:
        item.full_clean()
        item.save()
    except ValidationError:
        list_.delete()
        error = "You can't have an empty list item"
        return render(request, 'index.html', {'error': error})
    return redirect('/lists/{}/'.format(list_.id))


def add_item(request, list_id):
    list_ = List.objects.get(id=int(list_id))
    Item.objects.create(text=request.POST['item_text'], list=list_)
    return redirect('/lists/{}/'.format(list_.id))
