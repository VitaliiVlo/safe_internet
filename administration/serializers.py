from rest_framework import serializers

from .models import BlockRequest, Website


class WebsiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Website
        fields = ['domain']


class BlockRequestSerializer(serializers.ModelSerializer):
    website = WebsiteSerializer(many=False)

    class Meta:
        model = BlockRequest
        fields = ['pk', 'description', 'email', 'ip', 'is_accepted', 'website']

    def validate(self, attrs):
        attrs = super(BlockRequestSerializer, self).validate(attrs)
        user = self.context.get('user')
        if not (user and user.is_superuser):
            attrs['is_accepted'] = None
        return attrs

    def create(self, validated_data):
        website, created = Website.objects.get_or_create(domain=validated_data['website']['domain'])
        validated_data['website'] = website
        return super(BlockRequestSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        if 'website' in validated_data:
            website, created = Website.objects.get_or_create(domain=validated_data['website']['domain'])
            validated_data['website'] = website
        return super(BlockRequestSerializer, self).update(instance, validated_data)
