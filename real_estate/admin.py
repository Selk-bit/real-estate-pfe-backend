from django.contrib import admin
from .models import House, Equipment, HouseImage, HouseVideo, Prompt, UserProfile, Favorite, Synonyms

admin.site.register(House)
admin.site.register(Equipment)
admin.site.register(HouseImage)
admin.site.register(HouseVideo)
admin.site.register(Prompt)
admin.site.register(UserProfile)
admin.site.register(Favorite)
admin.site.register(Synonyms)



