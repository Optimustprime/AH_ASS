from rest_framework import serializers
from .models import Advertiser, User


class AdvertiserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertiser
        fields = ["name", "industry", "country"]


class UserSerializer(serializers.ModelSerializer):
    advertiser = AdvertiserSerializer(required=False)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "first_name",
            "last_name",
            "username",
            "advertiser",
        ]
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        advertiser_data = validated_data.pop("advertiser", None)
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        if advertiser_data:
            advertiser = Advertiser.objects.create(**advertiser_data)
            user.advertiser = advertiser
            user.save()

        return user
