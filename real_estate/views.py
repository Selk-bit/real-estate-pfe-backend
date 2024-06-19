from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import status
from .models import House, HouseEquipment, Equipment, HouseImage, Prompt, Favorite, UserLocation, Searchable, UserProfile, Synonyms
from .serializers import HouseSerializer, EquipmentSerializer, HouseImageSerializer, HouseVideoSerializer, \
    HouseEquipmentSerializer, UserSerializer
from .filters import HouseFilter
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .tasks import check_and_notify_user, prompt_search, synonyms_search
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.files.base import ContentFile
import boto3
import base64
import environ
from rest_framework.authtoken.views import ObtainAuthToken
from django.db.models import Q


class CheckTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # If the token is valid, the request will be successfully authenticated
        return Response({"valid": True}, status=status.HTTP_200_OK)


class ListFavoritesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        favorites = Favorite.objects.filter(user=request.user).select_related('house')
        serializer = HouseSerializer([fav.house for fav in favorites], many=True)
        return Response(serializer.data)


class AddFavoriteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, house_id):
        try:
            house = House.objects.get(pk=house_id)
            Favorite.objects.create(user=request.user, house=house)
            return Response({'message': 'House added to favorites'}, status=status.HTTP_201_CREATED)
        except House.DoesNotExist:
            return Response({'error': 'House not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class isFavorite(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, house_id):
        try:
            house = House.objects.get(pk=house_id)
            favorite = Favorite.objects.get(user=request.user, house=house)
            if favorite:
                return Response({'isFavorite': True}, status=status.HTTP_200_OK)
            return Response({'isFavorite': False}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({'isFavorite': False}, status=status.HTTP_404_NOT_FOUND)


class RemoveFromFavoriteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, house_id):
        try:
            house = House.objects.get(pk=house_id)
            Favorite.objects.filter(user=request.user, house=house).delete()
            return Response({'message': 'House removed from favorites'}, status=status.HTTP_201_CREATED)
        except House.DoesNotExist:
            return Response({'error': 'House not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SignupAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format='json'):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username is already taken."}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(username=username, password=password)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user_id": user.id}, status=status.HTTP_201_CREATED)


class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(CustomObtainAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        return Response({'token': token.key, 'user_id': token.user_id}, status=status.HTTP_200_OK)


class SignoutAPIView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class HouseSearchPrompt(APIView):

    def post(self, request, format=None):
        prompt = request.data.get("prompt", None)
        if not prompt:
            return Response({'error': 'No description is received'}, status=status.HTTP_400_BAD_REQUEST)
        return prompt_search(prompt, request.user)


class HouseSearchAPIView(APIView):
    filterset_class = HouseFilter

    def post(self, request, *args, **kwargs):
        houses = House.objects.all()

        filters = request.data.get("filters", {})
        search_query = request.data.get("search", None)

        if filters:
            filtered_houses = self.filterset_class(filters, queryset=houses)
            houses = filtered_houses.qs if filtered_houses.is_valid() else houses
        elif not search_query:
            return Response({'error': 'At least one filter or a search query must be provided.'}, status=status.HTTP_400_BAD_REQUEST)

        if search_query:
            houses = houses.filter(
                title__icontains=search_query
            )

        serializer = HouseSerializer(houses, many=True)
        return Response(serializer.data)


class HouseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = House.objects.order_by("id").all()
    serializer_class = HouseSerializer

    def filter_queryset(self, queryset):
        if "search" in self.request.query_params:
            seached_item = self.request.query_params.get("search")
            synonyms_instance = Synonyms.objects.filter(original_word=seached_item).first()
            if seached_item != "" and not synonyms_instance:
                synonyms_search.delay(seached_item)
                self.queryset = self.queryset.filter(title__icontains=seached_item).all()
            else:
                synonyms = synonyms_instance.get_synonyms()
                if synonyms:
                    query = Q()
                    query |= Q(title__icontains=seached_item)
                    for term in synonyms:
                        if term != "":
                            print(term)
                            query |= Q(title__icontains=term)
                    self.queryset = self.queryset.filter(query).all()

        if "min_price" in self.request.query_params and "max_price" in self.request.query_params:
            min_price = self.request.query_params.get("min_price")
            max_price = self.request.query_params.get("max_price")
            if float(min_price) == 0 and float(max_price) == 0:
                pass
            else:
                try:
                    float(min_price)
                except ValueError:
                    return Response({'error': 'The starting price is not a number'},
                                    status=status.HTTP_400_BAD_REQUEST)
                try:
                    float(max_price)
                except ValueError:
                    return Response({'error': 'The ending price is not a number'},
                                    status=status.HTTP_400_BAD_REQUEST)

                self.queryset = self.queryset.filter(price__gte=float(min_price)*1000, price__lte=float(max_price)*1000).all()

        if "number_of_rooms" in self.request.query_params:
            number_of_rooms = self.request.query_params.get("number_of_rooms")
            try:
                float(number_of_rooms)
                self.queryset = self.queryset.filter(number_of_rooms=float(number_of_rooms)).all()
            except ValueError:
                pass

        if "favorites" in self.request.query_params:
            user_id = self.request.query_params.get("favorites")
            try:
                user = User.objects.get(id=user_id)
                favorites = Favorite.objects.filter(user=user).select_related('house')
                houses_ids = [fav.house.id for fav in favorites]
                self.queryset = self.queryset.filter(pk__in=houses_ids).all()
            except ValueError:
                pass
        if "searchables" in self.request.query_params:
            user_id = self.request.query_params.get("searchables")
            try:
                user = User.objects.get(id=user_id)
                searchables = Searchable.objects.filter(user=user).select_related('house')
                houses_ids = [fav.house.id for fav in searchables]
                self.queryset = self.queryset.filter(pk__in=houses_ids).all()
            except ValueError:
                pass

        return self.queryset


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated]
        return super(UserViewSet, self).get_permissions()

    def list(self, request, *args, **kwargs):
        return Response({"detail": "Access denied."}, status=status.HTTP_403_FORBIDDEN)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.id != instance.id:
            return Response({"detail": "You do not have permission to view this user's data."},
                            status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance)
        print(serializer.data)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        env = environ.Env()
        environ.Env.read_env()
        instance = self.get_object()
        if request.user.id != instance.id:
            return Response({"detail": "You do not have permission to update this user's data."},
                            status=status.HTTP_403_FORBIDDEN)

        # Handle UserProfile data
        profile_instance = instance.profile
        if 'profile_picture' in request.FILES:
            profile_picture = request.FILES['profile_picture'].read()
            imgstr = base64.b64encode(profile_picture).decode('utf-8')
            ext = request.FILES['profile_picture'].name.split('.')[-1]
            file_name = f'{instance.username}_profile.{ext}'
            img_data = base64.b64decode(imgstr)

            # Upload to S3
            s3 = boto3.client(
                's3',
                aws_access_key_id=env('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=env('AWS_SECRET_ACCESS_KEY')
            )
            s3.upload_fileobj(
                ContentFile(img_data),
                env('AWS_STORAGE_BUCKET_NAME'),
                f"{env('AWS_LOCATION')}/{file_name}",
                ExtraArgs={
                    'ACL': env('AWS_DEFAULT_ACL'),
                    'CacheControl': 'max-age=86400',
                    'ContentType': 'image/jpeg'
                }
            )
            # file_url = f"https://{env('AWS_STORAGE_BUCKET_NAME')}.s3.amazonaws.com/{env('AWS_LOCATION')}/{file_name}"
            profile_instance.profile_picture = file_name

        profile_instance.phone = request.data.get('phone', profile_instance.phone)
        profile_instance.prompt = request.data.get('prompt', profile_instance.prompt)
        profile_instance.save()

        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.pop('partial', False))
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        env = environ.Env()
        environ.Env.read_env()

        # Extract user data from request
        user_data = {
            'first_name': request.data.get('first_name'),
            'last_name': request.data.get('last_name'),
            'username': request.data.get('username'),
            'email': request.data.get('email'),
            'password': request.data.get('password')
        }

        # Create User
        user = User.objects.create_user(**user_data)

        # Create UserProfile
        # profile_data = {
        #     'user': user,
        #     'phone': request.clsdata.get('phone')
        # }
        user.profile.phone = request.data.get('phone')
        profile_picture = request.data.get('profile_picture')
        if profile_picture:
            format, imgstr = profile_picture.split(';base64,')
            ext = format.split('/')[-1]
            img_data = base64.b64decode(imgstr)
            file_name = f'{user.username}_profile.{ext}'
            # Upload to S3
            s3 = boto3.client(
                's3',
                aws_access_key_id=env('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=env('AWS_SECRET_ACCESS_KEY')
            )
            s3.upload_fileobj(
                ContentFile(img_data),
                env('AWS_STORAGE_BUCKET_NAME'),
                f"{env('AWS_LOCATION')}/{file_name}",
                ExtraArgs={
                    'ACL': env('AWS_DEFAULT_ACL'),
                    'CacheControl': env('AWS_S3_OBJECT_PARAMETERS')['CacheControl'],
                    'ContentType': 'image/jpeg'
                }
            )
            file_url = f"https://{env('AWS_S3_CUSTOM_DOMAIN')}/{env('AWS_LOCATION')}/{file_name}"
            user.profile.profile_picture = file_name

        # UserProfile.objects.create(**profile_data)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user_id": user.id}, status=status.HTTP_201_CREATED)


class EquipmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer


class ListUserHousesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        houses = House.objects.filter(owner=request.user)
        serializer = HouseSerializer(houses, many=True)
        return Response(serializer.data)


# class CreateCityAPIView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request):
#         serializer = HouseSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(owner=request.user)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateHouseAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = HouseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateHouseAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        house = House.objects.filter(pk=pk, owner=request.user).first()
        if not house:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = HouseSerializer(house, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteHouseAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        house = House.objects.filter(pk=pk, owner=request.user).first()
        if house:
            house.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)


class HouseListCreate(APIView):
    def post(self, request, format=None):
        existing_house = House.objects.filter(title__iexact=request.data.get('title')).first()
        if existing_house:
            serializer = HouseSerializer(existing_house)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = HouseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EquipmentListCreate(APIView):
    def post(self, request, format=None):
        existing_equipment = Equipment.objects.filter(name__iexact=request.data.get('name')).first()
        if existing_equipment:
            serializer = EquipmentSerializer(existing_equipment)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = EquipmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HouseEquipmentCreate(APIView):
    def post(self, request, format=None):
        house_id = request.data.get('house')
        equipment_id = request.data.get('equipment')

        existing_entry = HouseEquipment.objects.filter(house=house_id, equipment=equipment_id).first()
        if existing_entry:
            serializer = HouseEquipmentSerializer(existing_entry)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = HouseEquipmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HouseImageListCreate(APIView):
    def post(self, request, format=None):
        existing_image = HouseImage.objects.filter(name=request.data.get('name')).first()
        if existing_image:
            serializer = HouseImageSerializer(existing_image)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = HouseImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HouseVideoListCreate(APIView):
    def post(self, request, format=None):
        serializer = HouseVideoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateLocationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')

        if latitude is None or longitude is None:
            return Response({'error': 'Latitude and longitude are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_location, created = UserLocation.objects.update_or_create(
                user=request.user,
                defaults={'latitude': latitude, 'longitude': longitude},
            )
            check_and_notify_user.delay(request.user.id)
            # result = check_and_notify_user(request.user.id)
            return Response({'message': 'Location updated successfully.'}, status=status.HTTP_200_OK)
        except (TypeError, ValueError):
            return Response({'error': 'Invalid latitude or longitude.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateUserPrompt(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        prompt = request.data.get("prompt")
        if prompt:
            try:
                UserProfile.objects.filter(user=request.user).update(prompt=prompt)
                return Response({'message': 'Prompt updated successfully.'}, status=status.HTTP_200_OK)
            except (TypeError, ValueError):
                return Response({'error': 'Invalid latitude or longitude.'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


