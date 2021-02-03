from django_filters import rest_framework as filters

from api_board.models import Title


class TitleFilter(filters.FilterSet):
    """
    Filter for Title model
    """
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')  # noqa
    genre = filters.CharFilter(field_name='genre__slug', label='genre')
    category = filters.CharFilter(field_name='category__slug')

    class Meta:
        model = Title
        fields = ['year']
