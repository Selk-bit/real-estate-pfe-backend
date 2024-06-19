from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
import json

class Equipment(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    icon_svg = models.TextField(null=True, blank=True, help_text="SVG code for the icon.")
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.nameHouse


class House(models.Model):
    TYPE_CHOICES = (
        ('sell', 'Sell'),
        ('rent', 'Rent'),
    )
    RENTABILITY_CHOICES = (
        ('partial', 'Partially Rentable'),
        ('full', 'Fully Rentable'),
    )
    title = models.CharField(max_length=255, db_collation='utf8mb4_unicode_ci')
    description = models.TextField(null=True, blank=True, db_collation='utf8mb4_unicode_ci')
    house_type = models.CharField(max_length=4, choices=TYPE_CHOICES)
    age = models.PositiveIntegerField(null=True, blank=True)
    number_of_rooms = models.PositiveIntegerField(null=True, blank=True)
    surface = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    rentability = models.CharField(max_length=7, choices=RENTABILITY_CHOICES, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    equipment = models.ManyToManyField(Equipment, through='HouseEquipment', related_name='houses')
    interest_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    floor_number = models.CharField(null=True, blank=True, max_length=100)
    number_of_salons = models.PositiveIntegerField(null=True, blank=True)
    number_of_toilets = models.PositiveIntegerField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='houses', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.title


class HouseEquipment(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        unique_together = ('house', 'equipment')


class HouseImage(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='house_images/')
    name = models.CharField(max_length=255, null=True, blank=True)
    replaced = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"Image for {self.house.title}"


class HouseVideo(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='house_videos/')
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"Video for {self.house.title}"


class Prompt(models.Model):
    text = models.TextField(db_collation='utf8mb4_unicode_ci')
    order = models.IntegerField()
    expected_result = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"Prompt #{self.pk}"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_favorites')
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='favorite_houses')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'house')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} favorites {self.house.title}"


class Searchable(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_searchables')
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='searched_for_users')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'house')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.house.title} matches {self.user.username}'s prompt"


class Synonyms(models.Model):
    original_word = models.CharField(max_length=255, unique=True, db_collation='utf8mb4_unicode_ci')
    synonyms = models.TextField(null=True, blank=True, db_collation='utf8mb4_unicode_ci')

    def save(self, *args, **kwargs):
        self.original_word = self.original_word.lower()
        super(Synonyms, self).save(*args, **kwargs)

    def set_synonyms(self, synonym_list):
        self.synonyms = json.dumps(synonym_list, ensure_ascii=False)

    def get_synonyms(self):
        return json.loads(self.synonyms)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['original_word'], name='unique_original_word_case_insensitive')
        ]

    def __str__(self):
        return self.original_word


class UserLocation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='location')
    latitude = models.FloatField()
    longitude = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Location for {self.user.username}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    phone = models.CharField(null=True, blank=True, max_length=255)
    prompt = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username}\'s Profile'


class City(models.Model):
    name = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.name}'


class ExpirableToken(Token):
    def is_expired(self):
        return timezone.now() > self.created + timezone.timedelta(minutes=5)



