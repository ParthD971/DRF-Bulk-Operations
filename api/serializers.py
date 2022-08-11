from rest_framework import serializers

from api.models import Book


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'name', 'details']


class BulkCreateSerializer(BookSerializer):

    def validate(self, attrs):
        attrs = super(BulkCreateSerializer, self).validate(attrs)
        duplicate_data_count = self.context.get('duplicate_data_count')

        if duplicate_data_count and attrs['name'] and duplicate_data_count[attrs['name']] > 1:
            raise serializers.ValidationError({'non_field_error': 'Pakdai gyo, same name che'})

        return attrs


class BulkUpdateSerializer(BookSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()

    def validate(self, attrs):
        attrs = super(BulkUpdateSerializer, self).validate(attrs)
        id_count = self.context.get('id_count', None)
        name_count = self.context.get('name_count', None)
        ids = id_count.keys()

        if id_count and id_count[f"{attrs['id']}"] > 1:
            raise serializers.ValidationError({'id': 'Same id\'s present in data.'})

        if name_count and name_count[attrs['name']] > 1:
            raise serializers.ValidationError({'id': 'Same name\'s present in data.'})

        if Book.objects.all().exclude(id=attrs['id']).filter(name=attrs['name']).exists():
            raise serializers.ValidationError({'name': 'Unique constraints failed.'})

        return attrs

    def create(self, validated_data):
        instance = Book.objects.get(id=validated_data['id'])
        return self.update(instance, validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data['name']
        instance.details = validated_data['details']
        instance.save()
        return instance

    class Meta:
        model = Book
        fields = ['id', 'name', 'details']
        validators = []

