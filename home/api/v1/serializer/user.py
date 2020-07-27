from django.contrib.auth import get_user_model
from rest_framework import serializers
from typing import List

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'user_type', 'first_name', 'last_name', 'status', 'role', 'accepted_terms_date']


class UserSerializerBase(serializers.ModelSerializer):
    """List any users Serializer."""

    class Meta(object):
        model = User
        fields: List[str] = [
            'id',
            'email',
            'first_name',
            'last_name',
            'user_type',
            'accepted_terms_date',
            'role',
        ]
        read_only_fields: List[str] = ['created', 'modified']

    def is_admin(self) -> bool:
        """Is caller User.ROLE.ADMIN or not."""
        return 'request' in self.context and self.context['request'].user.role == User.ROLE.ADMIN


class UserList(UserSerializerBase):
    """List any users Serializer."""

    class Meta(UserSerializerBase.Meta):
        fields = UserSerializerBase.Meta.fields + ['status', 'username']


class UserCreate(UserSerializerBase):
    """Create a user Serializer."""

    class Meta(UserSerializerBase.Meta):
        fields = UserSerializerBase.Meta.fields + ['password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """Admin create user."""
        validated_data['username'] = validated_data['email']
        new_user = super().create(validated_data)
        if new_user.send_invitation_email():
            new_user.status = User.STATUS.INVITATION
            new_user.save()
        return new_user


class UserUpdate(UserSerializerBase):
    """Update a user Serializer."""

    class Meta(UserSerializerBase.Meta):
        fields = ['role', 'user_type']


class UserEditorUpdate(UserSerializerBase):
    """Update a user with Role Editor Serializer."""

    class Meta(UserSerializerBase.Meta):
        fields = ['first_name', 'last_name']


class ResetPasswordSerializer(serializers.Serializer):
    """For user reset-password."""

    email = serializers.EmailField(required=True)


class InvitationSerializer(serializers.Serializer):
    """For user send-invitation."""

    id = serializers.IntegerField(required=True)

