from datetime import timedelta

from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import serializers

from .models import Membership, Tenant, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "display_name", "shop_name", "shop_location", "phone", "is_staff"]


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(min_length=6, write_only=True)
    display_name = serializers.CharField(max_length=80, required=False, allow_blank=True)
    shop_name = serializers.CharField(max_length=120, required=False, allow_blank=True)
    shop_location = serializers.CharField(max_length=120, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=30, required=False, allow_blank=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("账号已存在")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        tenant = Tenant.objects.create(
            name=validated_data.get("shop_name") or f"{user.username}的档口",
            contact_name=validated_data.get("display_name", ""),
            contact_phone=validated_data.get("phone", ""),
        )
        # 注册即送3天旗舰版试用
        tenant.apply_plan("ultimate")
        tenant.trial_ends_at = timezone.now() + timedelta(days=3)
        tenant.save()
        Membership.objects.create(tenant=tenant, user=user, role=Membership.Role.OWNER)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs["username"], password=attrs["password"])
        if not user:
            raise serializers.ValidationError("账号或密码不正确")
        attrs["user"] = user
        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["display_name", "shop_name", "shop_location", "phone"]
