from django.test import TestCase
from django.core.urlresolvers import resolve
from django.http import HttpRequest
from django.template.loader import render_to_string
from lists.views import home_page
from lists.models import Item


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

	def test_post_request(self):
		request = HttpRequest()
		request.method = 'POST'
		request.POST['item_text'] = 'A new list item'

		response = home_page(request)

		self.assertEqual(Item.objects.count(), 1)
		new_item = Item.objects.first()
		self.assertEqual(new_item.text, 'A new list item')

	def test_redirect_after_post(self):
		request = HttpRequest()
		request.method = 'POST'
		request.POST['item_text'] = 'A new list item'

		response = home_page(request)

		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['location'], '/')

	def test_save_item(self):
		request = HttpRequest()
		home_page(request)
		self.assertEqual(Item.objects.count(), 0)

	def test_display_all_items(self):
		Item.objects.create(text='itemey 1')
		Item.objects.create(text='itemey 2')

		request = HttpRequest()
		response = home_page(request)

		self.assertIn('itemey 1', response.content.decode())
		self.assertIn('itemey 2', response.content.decode())

	def test_comment_empty(self):
		request = HttpRequest()
		response = home_page(request)

		self.assertIn('yey, waktunya berlibur', response.content.decode())
	
	def test_comment_partial(self):
		Item.objects.create(text='test 1')

		request = HttpRequest()
		response = home_page(request)
		self.assertIn('sibuk tapi santai', response.content.decode())
	
	def test_comment_full(self):
		for n in range(5):
			Item.objects.create(text='test {}'.format(n + 1))
		
		request = HttpRequest()
		response = home_page(request)
		self.assertIn('oh tidak', response.content.decode())


class ItemModelTest(TestCase):
	def test_items(self):
		first_item = Item()
		first_item.text = 'The first (ever) list item'
		first_item.save()

		second_item = Item()
		second_item.text = 'Item the second'
		second_item.save()

		saved_items = Item.objects.all()
		self.assertEqual(saved_items.count(), 2)

		first_saved_item = saved_items[0]
		second_saved_item = saved_items[1]
		self.assertEqual(first_saved_item.text, 'The first (ever) list item')
		self.assertEqual(second_saved_item.text, 'Item the second')
