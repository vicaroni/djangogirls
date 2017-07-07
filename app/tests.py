from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Post, Comment

# Create your tests here.
class PostListTest(TestCase):

    def test_no_post(self):
        user = User.objects.create(username='admin')
        user.set_password('123456')
        user.save()
        self.client.login(username='admin', password='123456')
        response = self.client.get(reverse('app:post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['posts'], [])
        response = self.client.get(reverse('app:post_draft_list'))
        self.assertQuerysetEqual(response.context['posts'], [])

    def test_post(self):
        user = User.objects.create(username='admin')
        user.set_password('123456')
        user.save()
        self.client.login(username='admin', password='123456')
        Post.objects.create(author=user, title='Title', published_date=timezone.now())
        response = self.client.get(reverse('app:post_list'))
        self.assertQuerysetEqual(response.context['posts'], ['<Post: Title>'])
        response = self.client.get(reverse('app:post_draft_list'))
        self.assertQuerysetEqual(response.context['posts'], [])

    def test_draft(self):
        user = User.objects.create(username='admin')
        user.set_password('123456')
        user.save()
        Post.objects.create(author=user, title='Draft', created_date=timezone.now())
        response = self.client.get(reverse('app:post_list'))
        self.assertQuerysetEqual(response.context['posts'], [])
        self.client.login(username='admin', password='123456')
        response = self.client.get(reverse('app:post_draft_list'))
        self.assertQuerysetEqual(response.context['posts'], ['<Post: Draft>'])

    def test_post_draft(self):
        user = User.objects.create(username='admin')
        user.set_password('123456')
        user.save()
        self.client.login(username='admin', password='123456')
        Post.objects.create(author=user, title='Title', published_date=timezone.now())
        Post.objects.create(author=user, title='Draft', created_date=timezone.now())
        response = self.client.get(reverse('app:post_list'))
        self.assertQuerysetEqual(response.context['posts'], ['<Post: Title>'])
        response = self.client.get(reverse('app:post_draft_list'))
        self.assertQuerysetEqual(response.context['posts'], ['<Post: Draft>'])

    def test_2_post(self):
        user = User.objects.create(username='admin')
        user.set_password('123456')
        user.save()
        self.client.login(username='admin', password='123456')
        Post.objects.create(author=user, title='Title1', published_date=timezone.now())
        Post.objects.create(author=user, title='Title2', published_date=timezone.now())
        response = self.client.get(reverse('app:post_list'))
        self.assertQuerysetEqual(response.context['posts'], ['<Post: Title1>', '<Post: Title2>'])
        response = self.client.get(reverse('app:post_draft_list'))
        self.assertQuerysetEqual(response.context['posts'], [])

class DetailTest(TestCase):

    def test_post_detail(self):
        user = User.objects.create(username='admin')
        p = Post.objects.create(author=user, title='Title', text='Text', published_date=timezone.now())
        resp = self.client.get(reverse('app:post_detail', args=(p.id,)))
        self.assertContains(resp, p.text)

    def test_no_comments(self):
        user = User.objects.create(username='admin')
        p = Post.objects.create(author=user, title='Title', text='Text', published_date=timezone.now())
        url = reverse('app:post_detail', args=(p.id,))
        resp = self.client.get(url)
        self.assertContains(resp, 'No comments here yet :(')

    def test_comment_nonappr(self):
        user = User.objects.create(username='admin')
        user.set_password('123456')
        user.save()
        p = Post.objects.create(author=user, title='Title', text='Text', published_date=timezone.now())
        c = Comment.objects.create(post=p, author='author', text='Comment')
        url = reverse('app:post_detail', args=(p.id,))
        resp = self.client.get(url)
        self.assertContains(resp, 'No comments here yet :(')
        self.client.login(username='admin', password='123456')
        resp = self.client.get(url)
        self.assertContains(resp, c.text)

    def test_comment_appr(self):
        user = User.objects.create(username='admin')
        p = Post.objects.create(author=user, title='Title', text='Text', published_date=timezone.now())
        c = Comment.objects.create(post=p, author='author', text='Comment')
        c.approve()
        resp = self.client.get(reverse('app:post_detail', args=(p.id,)))
        self.assertContains(resp, c.text)
