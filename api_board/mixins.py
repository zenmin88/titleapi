from rest_framework import viewsets, mixins
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated

from api_board.permissions import IsAdminOrModeratorOrAuthor, IsAdminRole


class ReviewCommentMixin(viewsets.ModelViewSet):
    """ Mixin with permissions where users can publishing their review and view it."""
    serializer_class = None
    model = None
    related_model = None
    related_field = str()
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_permissions(self):
        """Set permission for various methods for various role."""
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated]
        elif self.action in ['partial_update', 'destroy']:
            permission_classes = [IsAdminOrModeratorOrAuthor]
        else:
            permission_classes = [IsAdminRole]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        obj_id = self.kwargs.get(self.related_field + '_id')
        obj = get_object_or_404(self.related_model, id=obj_id)
        data = {
            self.related_field: obj
        }
        queryset = self.model.objects.filter(**data)
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        obj_id = self.kwargs.get(self.related_field + '_id')
        obj = get_object_or_404(self.related_model, id=obj_id)
        data = {
            'author': user,
            self.related_field: obj
        }
        serializer.save(**data)


class CategoryGenreMixin(mixins.CreateModelMixin,
                         mixins.ListModelMixin,
                         mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):
    """Mixin for category and genre."""
    lookup_field = 'slug'
    filter_backends = [SearchFilter]
    search_fields = ['name']
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminRole]
        return [permission() for permission in permission_classes]
