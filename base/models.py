from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

GAME_MODES = (
    ('RANKED_SOLO', 'Ranked Solo/Duo'),
    ('RANKED_FLEX', 'Ranked Flex'),
    ('NORMAL', 'Normal Blind/Draft'),
    ('ARAM', 'ARAM'),
    ('CLASH', 'Clash'),
)


RANKS = (
    ('IRON', 'Iron'),
    ('BRONZE', 'Bronze'),
    ('SILVER', 'Silver'),
    ('GOLD', 'Gold'),
    ('PLATINUM', 'Platinum'),
    ('EMERALD', 'Emerald'),
    ('DIAMOND', 'Diamond'),
    ('MASTER', 'Master+'),
    ('UNRANKED', 'Unranked'),
)


ROLES = (
    ('TOP', 'Top'),
    ('JUNGLE', 'Jungle'),
    ('MID', 'Mid'),
    ('BOTTOM', 'Bottom'),
    ('SUPPORT', 'Support'),
    ('FILL', 'Fill')
)


class LFGPost(models.Model):
    host = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    game_mode = models.CharField(max_length=20, choices=GAME_MODES, default='RANKED_SOLO')

    host_rank = models.CharField(max_length=20, choices=RANKS, default='UNRANKED')
    min_rank = models.CharField(max_length=20, choices=RANKS, default='UNRANKED')

    host_role = models.CharField(max_length=20, choices=ROLES, default="FILL")
    looking_for_role = models.CharField(max_length=20, choices=ROLES, default="FILL")

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']
    
    def __str__(self):
        return self.title

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    riot_id = models.CharField(max_length=100, blank=True, null=True)
    discord_handle = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return str(self.user)

class Message(models.Model):
    name = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(LFGPost, on_delete=models.CASCADE)
    body = models.TextField()

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']
    
    def __str__(self):
        return self.body[0:50]
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()