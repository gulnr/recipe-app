from django.db import models
from django.utils import timezone
from django.urls import reverse

from django.shortcuts import get_object_or_404
# Create your models here.


class Ingredient(models.Model):
    ingredient = models.CharField(max_length=200)

    def __str__(self):
        return self.ingredient


class Post(models.Model):
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE,)
    title = models.CharField(max_length=200)
    image = models.ImageField()
    description = models.TextField()
    difficulty = models.CharField(max_length=1, choices=(('E', 'Easy'), ('M', 'Medium'), ('H', 'Hard')))
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    ingredient = models.ManyToManyField(Ingredient)

    # if you decide to publish and hit publish button, the publish_date will be now.
    def publish(self,user):
        self.published_date = timezone.now()
        self.author = user
        self.save()

    def approve_comment(self):
        # there is a list of comments somewhere. checking comments approved or not.
        return self.comments.filter(approved_comment=True)

    def get_absolute_url(self):
        # if you created a instance of post
        return reverse("post_detail", kwargs={'pk': self.pk})

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey('recipeblog.Post', related_name='comments', on_delete=models.CASCADE,)
    author = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now())
    approved_comment = models.BooleanField(default=False)

    def approve(self):
        self.approved_comment = True
        self.save()

    def get_absolute_url(self):
        return reverse('post_list')


    def __str__(self):
        return self.text

