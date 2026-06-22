from rest_framework import serializers

from .models import AiChatMessage, QuickCategory, QuickStyle


class QuickCategorySerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source="created_by_id", read_only=True)

    class Meta:
        model = QuickCategory
        fields = ["id", "owner_id", "key", "name", "description", "fabrics", "processes"]
        read_only_fields = ["id", "owner_id"]


class QuickStyleSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source="created_by_id", read_only=True)
    accessory_pack = serializers.FloatField()
    expected_profit = serializers.FloatField()
    minimum_price = serializers.FloatField()
    quote_price = serializers.FloatField()
    total_cost = serializers.FloatField()
    profit = serializers.FloatField()

    class Meta:
        model = QuickStyle
        fields = [
            "id",
            "owner_id",
            "name",
            "category",
            "image",
            "image_data",
            "fabrics",
            "processes",
            "accessory_pack",
            "expected_profit",
            "minimum_price",
            "quote_price",
            "total_cost",
            "profit",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner_id", "created_at", "updated_at"]


class AiChatMessageSerializer(serializers.ModelSerializer):
    text = serializers.CharField(source="content", read_only=True)
    costDraft = serializers.JSONField(source="cost_draft", read_only=True)
    needMoreInfo = serializers.BooleanField(source="need_more_info", read_only=True)

    class Meta:
        model = AiChatMessage
        fields = [
            "id",
            "role",
            "text",
            "intent",
            "costDraft",
            "calculation",
            "needMoreInfo",
            "created_at",
        ]
