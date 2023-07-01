from django.contrib import admin
from django.contrib.auth.models import User

from .models import Ads, Category, Comment, Profile

admin.site.unregister(User)


class ProfileInline(admin.StackedInline):
    model = Profile


class UserAdmin(admin.ModelAdmin):
    model = User
    fields = ["username"]
    inlines = [ProfileInline]


admin.site.register(Ads)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(User, UserAdmin)

# Register your models here.
