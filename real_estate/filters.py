from django_filters import rest_framework as filters
from .models import House


class HouseFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')

    class Meta:
        model = House
        fields = ['house_type', 'city']