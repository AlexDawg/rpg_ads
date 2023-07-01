from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save


class Category(models.Model):
    name = models.CharField(max_length=25, unique=True)

    def __str__(self):
        return f'{self.name.title()}'


class Comment(models.Model):
    ads = models.ForeignKey('Ads', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    time_in = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.ads.title}'


class Ads(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    text = models.TextField()
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    video = models.FileField(upload_to='videos/', null=True, blank=True)
    category = models.ManyToManyField(Category, through='AdsCategory')
    time_in = models.DateTimeField(auto_now_add=True)
    comments = models.ManyToManyField(Comment, related_name="commented_on", blank=True)

    def __str__(self):
        return f'{self.title.title()}: {self.text[:20]}'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    follows = models.ManyToManyField("self",
                                     related_name="followed_by",
                                     symmetrical=False,
                                     blank=True)
    date_modified = models.DateTimeField(User, auto_now=True)
    comments = models.ManyToManyField(Comment,
                                       related_name="commented_by",
                                       blank=True)

    def __str__(self):
        return self.user.username


def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()
        user_profile.follows.set([instance.profile.id])
        user_profile.save()

post_save.connect(create_profile, sender=User)


# Create your models here.
