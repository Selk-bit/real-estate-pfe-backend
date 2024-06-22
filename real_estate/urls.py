from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HouseListCreate, HouseListUpdate, EquipmentListCreate, HouseImageListCreate, HouseVideoListCreate, \
    HouseEquipmentCreate, HouseViewSet, UserViewSet, EquipmentViewSet, HouseSearchAPIView, HouseSearchPrompt, SignoutAPIView, \
    SignupAPIView, AddFavoriteAPIView, ListFavoritesAPIView, CreateHouseAPIView, UpdateHouseAPIView, DeleteHouseAPIView, \
    ListUserHousesAPIView, UpdateLocationAPIView, RemoveFromFavoriteAPIView, UpdateUserPrompt, CheckTokenView, CustomObtainAuthToken, isFavorite
from rest_framework.authtoken.views import obtain_auth_token


router = DefaultRouter()
router.register(r'houses', HouseViewSet)
router.register(r'users', UserViewSet)
router.register(r'equipment', EquipmentViewSet)

api_urlpatterns = [
    path('houses/list/create', HouseListCreate.as_view(), name='house-create'),
    path('houses/list/update/<int:house_id>', HouseListUpdate.as_view(), name='house-create'),
    path('equipments/', EquipmentListCreate.as_view(), name='equipment-create'),
    path('house_equip/', HouseEquipmentCreate.as_view(), name='house-equipment-create'),
    path('images/', HouseImageListCreate.as_view(), name='images-create'),
    path('videos/', HouseVideoListCreate.as_view(), name='videos-create'),
    path('houses/search/', HouseSearchAPIView.as_view(), name='house-search'),
    path('houses/prompt/', HouseSearchPrompt.as_view(), name='house-prompt'),
    path('signin/', CustomObtainAuthToken.as_view(), name='api_token_auth'),
    path('signout/', SignoutAPIView.as_view(), name='api_signout'),
    path('signup/', SignupAPIView.as_view(), name='api_signup'),
    path('houses/<int:house_id>/add_to_favorites/', AddFavoriteAPIView.as_view(), name='add_to_favorites'),
    path('houses/<int:house_id>/remove_from_favorotes/', RemoveFromFavoriteAPIView.as_view(), name='remove_to_favorites'),
    path('houses/<int:house_id>/isfavorite/', isFavorite.as_view(), name='is_favorite'),
    path('favorites/', ListFavoritesAPIView.as_view(), name='list_favorites'),
    path('houses/create/', CreateHouseAPIView.as_view(), name='create_house'),
    path('houses/', ListUserHousesAPIView.as_view(), name='list_houses'),
    path('houses/<int:pk>/update/', UpdateHouseAPIView.as_view(), name='update_house'),
    path('houses/<int:pk>/delete/', DeleteHouseAPIView.as_view(), name='delete_house'),
    path('update-location/', UpdateLocationAPIView.as_view(), name='update_location'),
    path('update-prompt/', UpdateUserPrompt.as_view(), name='update_prompt'),
    path('token/check/', CheckTokenView.as_view(), name='check-token'),
]

urlpatterns = [
    path('', include(router.urls)),
    path('api/', include(api_urlpatterns)),
]