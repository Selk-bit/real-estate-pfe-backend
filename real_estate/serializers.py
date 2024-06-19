from rest_framework import serializers
from .models import House, Equipment, HouseImage, HouseVideo, HouseEquipment
from django.contrib.auth.models import User
from .models import UserProfile, Favorite


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = '__all__'


class HouseEquipmentSerializer(serializers.ModelSerializer):
    # equipment = EquipmentSerializer(read_only=True)

    class Meta:
        model = HouseEquipment
        fields = '__all__'


class HouseImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseImage
        fields = '__all__'


class HouseVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseVideo
        fields = '__all__'


class HouseSerializer(serializers.ModelSerializer):
    # equipment_details = HouseEquipmentSerializer(source='houseequipment_set', many=True, read_only=True)
    total_interest = serializers.ReadOnlyField()
    equipment = EquipmentSerializer(many=True, read_only=True)
    images = HouseImageSerializer(many=True, read_only=True)
    videos = HouseVideoSerializer(many=True, read_only=True)
    owner_name = serializers.SerializerMethodField()
    owner_picture = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    favorite = serializers.SerializerMethodField()


    class Meta:
        model = House
        fields = [
            'id', 'title', 'description', 'house_type', 'age', 'number_of_rooms',
            'surface', 'rentability', 'price', 'interest_percentage', 'floor_number', 'number_of_salons',
            'city', 'address', 'total_interest', 'equipment', 'images', 'videos', 'owner_name', 'owner_picture', 'phone',
            'favorite'
        ]

    def get_owner_name(self, obj):
        return f"{obj.owner.first_name} {obj.owner.last_name}" if obj.owner else None

    def get_owner_picture(self, obj):
        if obj.owner and hasattr(obj.owner, 'profile') and obj.owner.profile.profile_picture:
            return obj.owner.profile.profile_picture.url
        return None

    def get_phone(self, obj):
        if obj.owner and hasattr(obj.owner, 'profile'):
            return obj.owner.profile.phone
        return None

    def get_favorite(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            house = obj
            favorite = Favorite.objects.filter(user=user, house=house).exists()
            return favorite
        return False


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'phone', 'prompt']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'profile']