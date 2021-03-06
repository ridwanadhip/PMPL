from django.test import TestCase
from django.core.urlresolvers import resolve
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.html import escape
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

    def test_can_save_a_POST_request_to_an_existing_list(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()
        
        self.client.post(
            '/lists/{}/'.format(correct_list.id),
            data={'item_text': 'A new item for an existing list'}
        )
        
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new item for an existing list')
        self.assertEqual(new_item.list, correct_list)

    def test_POST_redirects_to_list_view(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()
        
        response = self.client.post(
            '/lists/{}/'.format(correct_list.id),
            data={'item_text': 'A new item for an existing list'}
        )
        self.assertRedirects(response, '/lists/{}/'.format(correct_list.id))

    def test_validation_errors_end_up_on_lists_page(self):
        list_ = List.objects.create()
        response = self.client.post(
            '/lists/{}/'.format(list_.id),
            data={'item_text': ''}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list.html')
        expected_error = escape("You can't have an empty list item")
        self.assertContains(response, expected_error)

        
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

    def test_validation_errors_are_sent_back_to_home_page_template(self):
        response = self.client.post('/lists/new', data={'item_text': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        expected_error = escape("You can't have an empty list item")
        self.assertContains(response, expected_error)

    def test_invalid_list_items_arent_saved(self):
        self.client.post('/lists/new', data={'item_text': ''})
        self.assertEqual(List.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)

        
