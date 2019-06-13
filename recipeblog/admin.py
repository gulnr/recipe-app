from django.contrib import admin

# Register your models here.

from recipeblog.models import Post, Comment, Ingredient


admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Ingredient)