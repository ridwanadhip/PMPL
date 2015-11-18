from django.test import TestCase
from django.core.urlresolvers import resolve
from django.http import HttpRequest
from django.template.loader import render_to_string
from lists.views import home_page
from lists.models import Item, List


class HomePageTest(TestCase):
    def test_url_resolvers(self):
        found = resolve('/')
        self.assertEqual(found.func, home_page)

    def test_home_page(self):
        request = HttpRequest()
        response = home_page(request)

        total = Item.objects.count()
        if total == 0:
            comment = 'yey, waktunya berlibur'
        elif total < 5:
            comment = 'sibuk tapi santai'
        else:
            comment = 'oh tidak'

        expected_html = render_to_string('index.html', {'comment': comment})
        self.assertEqual(response.content.decode(), expected_html)
    
    def test_comment_empty(self):
        request = HttpRequest()
        response = home_page(request)

        self.assertIn('yey, waktunya berlibur', response.content.decode())
    
    def test_comment_partial(self):
        _list = List.objects.create()
        Item.objects.create(text='test 1', list=_list)

        request = HttpRequest()
        response = home_page(request)
        self.assertIn('sibuk tapi santai', response.content.decode())
    
    def test_comment_full(self):
        _list = List.objects.create()
        for n in range(5):
            Item.objects.create(text='test {}'.format(n + 1), list=_list)
        
        request = HttpRequest()
        response = home_page(request)
        self.assertIn('oh tidak', response.content.decode())


class ListAndItemModelsTest(TestCase):
    def test_saving_and_retrieving_items(self):
        list_ = List()
        list_.save()
        
        first_item = Item()
        first_item.text = 'The first (ever) list item'
        first_item.list = list_
        first_item.save()

        second_item = Item()
        second_item.text = 'Item the second'
        second_item.list = list_
        second_item.save()
        
        saved_list = List.objects.first()
        self.assertEqual(saved_list, list_)
        
        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(), 2)

        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]
        self.assertEqual(first_saved_item.text, 'The first (ever) list item')
        self.assertEqual(first_saved_item.list, list_)
        self.assertEqual(second_saved_item.text, 'Item the second')
        self.assertEqual(second_saved_item.list, list_)


class ListViewTest(TestCase):
    def test_uses_list_template(self):
        list_ = List.objects.create()
        response = self.client.get('/lists/{}/'.format(list_.id))
        self.assertTemplateUsed(response, 'list.html')
        
    def test_displays_only_items_for_that_list(self):
        correct_list = List.objects.create()
        Item.objects.create(text='itemey 1', list=correct_list)
        Item.objects.create(text='itemey 2', list=correct_list)
        
        other_list = List.objects.create()
        Item.objects.create(text='other list item 1', list=other_list)
        Item.objects.create(text='other list item 2', list=other_list)
        
        response = self.client.get('/lists/{}/'.format(correct_list.id))
        
        self.assertContains(response, 'itemey 1')
        self.assertContains(response, 'itemey 2')
        self.assertNotContains(response, 'other list item 1')
        self.assertNotContains(response, 'other list item 2')
        
    def test_passes_correct_list_to_template(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()
        response = self.client.get('/lists/{}/'.format(correct_list.id))
        self.assertEqual(response.context['list'], correct_list)
        
        
class NewListTest(TestCase):
    def test_post_request(self):
        data = {
            'item_text': 'A new list item',
        }
        
        self.client.post('/lists/new', data)
        
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new list item')

    def test_redirect_after_post(self):
        data = {
            'item_text': 'A new list item',
        }
        
        response = self.client.post('/lists/new', data)
        
        new_list = List.objects.first()
        self.assertRedirects(response, '/lists/{}/'.format(new_list.id))


class NewItemTest(TestCase):
    def test_can_save_a_POST_request_to_an_existing_list(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()
        
        url = '/lists/{}/add_item'.format(correct_list.id)
        data = {
            'item_text': 'A new item for an existing list'
        }
        
        self.client.post(url, data)
        
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new item for an existing list')
        self.assertEqual(new_item.list, correct_list)
    
    def test_redirect_to_list_view(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()
        
        url = '/lists/{}/add_item'.format(correct_list.id)
        data = {
            'item_text': 'A new item for an existing list'
        }
        
        response = self.client.post(url, data)
        
        self.assertRedirects(response, '/lists/{}/'.format(correct_list.id))
        
        