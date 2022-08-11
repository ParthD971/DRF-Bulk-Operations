from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.models import Book
from api.serializers import BookSerializer, BulkCreateSerializer, BulkUpdateSerializer


class BookView(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True

        return super(BookView, self).get_serializer(*args, **kwargs)

    @action(methods=['post'], detail=False)
    def bulk_create(self, request, *args, **kwargs):
        data = request.data

        if data:
            if not isinstance(data, list):
                raise ValidationError('Expected list of dict.')

            temp = {}
            for i in data:
                temp[i['name']] = temp.get(i['name'], 0) + 1

            context = {
                'request': request,
                'duplicate_data_count': temp
            }

            serializer = BulkCreateSerializer(data=data, context=context, many=True)
            if serializer.is_valid():
                items = [
                    Book(**item) for item in serializer.validated_data
                ]
                Book.objects.bulk_create(items, batch_size=5000)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('No Data to process', status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False)
    def bulk_update(self, request, *args, **kwargs):
        data = request.data

        if data:
            if not isinstance(data, list):
                raise ValidationError('Expected list of dict.')

            try:
                id_count = {}
                name_count = {}
                for i in data:
                    id_count[i['id']] = id_count.get(i['id'], 0) + 1
                    name_count[i['name']] = name_count.get(i['name'], 0) + 1
            except KeyError:
                raise ValidationError('id or name is not present in data.')

            context = {
                'request': request,
                'id_count': id_count,
                'name_count': name_count,
            }

            serializer = BulkUpdateSerializer(data=data, context=context, many=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('No Data to process', status=status.HTTP_400_BAD_REQUEST)