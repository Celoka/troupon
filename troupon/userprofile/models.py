from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from deals.models import STATE_CHOICES

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User)
    first_name = models.CharField(max_length=100, null=False, blank=False, default='')
    last_name = models.CharField(max_length=100, null=False, blank=False, default='')
    user_state = models.SmallIntegerField(choices=STATE_CHOICES,
                                          default=25)

    interest = models.TextField(blank=True, default='')

    def __unicode__(self):
        return u'Profile of user: %s' % self.user.username

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User, dispatch_uid=create_user_profile)