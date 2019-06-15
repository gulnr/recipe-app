from django.contrib import admin

# Register your models here.

from recipeblog.models import Post, Comment, Ingredient,Like,Rate


admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Ingredient)
admin.site.register(Like)
admin.site.register(Rate)