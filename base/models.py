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

TIERS = (
    ('UNRANKED', 'Unranked'),
    ('IRON', 'Iron'),
    ('BRONZE', 'Bronze'),
    ('SILVER', 'Silver'),
    ('GOLD', 'Gold'),
    ('PLATINUM', 'Platinum'),
    ('EMERALD', 'Emerald'),
    ('DIAMOND', 'Diamond'),
    ('MASTER', 'Master'),
    ('GRANDMASTER', 'Grandmaster'),
    ('CHALLENGER', 'Challenger'),
)

ROLES = (
    ('TOP', 'Top'),
    ('JUNGLE', 'Jungle'),
    ('MID', 'Mid'),
    ('BOTTOM', 'Bottom'),
    ('SUPPORT', 'Support'),
    ('FILL', 'Fill')
)

REGIONS = (
    ('BR', 'Brazil'),
    ('EUNE', 'Europe Nordic & East'),
    ('EUW', 'Europe West'),
    ('LAN', 'Latin America North'),
    ('LAS', 'Latin America South'),
    ('NA', 'North America'),
    ('OCE', "Oceania"),
    ("RU", 'Russia'),
    ('TR', 'Turkey'),
    ('ME', 'Middle East'),
    ('JP', 'Japan'),
    ('KR', 'Republic of Korea'),
    ('SEA', 'Southeast Asia'),
    ('TW', 'Taiwan, Hong Kong, Macao'),
    ('VN', 'Vietnam'),
    ('PBE', 'Public Beta Environment')
)

class LFGPost(models.Model):
    host = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    game_mode = models.CharField(max_length=20, choices=GAME_MODES, default='RANKED_SOLO')
    region = models.CharField(max_length=30, choices=REGIONS, default='EUW')
    host_tier = models.CharField(max_length=20, choices=TIERS, default='UNRANKED')
    min_tier = models.CharField(max_length=20, choices=TIERS, default='UNRANKED')
    participants = models.ManyToManyField(User, related_name="participants", blank=True)
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

    #puuid = models.CharField(max_length=200, blank=True, null=True)
    summoner_id = models.CharField(max_length=50, blank=True, null=True)
    summonel_lvl = models.IntegerField(default=0)
    #profile_icon_id = models.IntegerField(default=)
    rank_tier = models.CharField(max_length=20, blank=True, null=True)
    rank_division = models.CharField(max_length=10, blank=True, null=True)
    league_points = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)

    def __str__(self):
        return str(self.user)

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chat_room = models.ForeignKey(LFGPost, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
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