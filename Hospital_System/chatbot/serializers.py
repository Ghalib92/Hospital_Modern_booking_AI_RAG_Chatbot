from rest_framework import serializers


class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=2000)
    history = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField()),
        required=False,
        help_text='Prior turns: [{"role": "user"|"assistant", "content": "..."}]',
    )


class ChatResponseSerializer(serializers.Serializer):
    answer = serializers.CharField()
    sources = serializers.ListField(child=serializers.DictField(), required=False)
    emergency = serializers.BooleanField()
    disclaimer = serializers.CharField()
