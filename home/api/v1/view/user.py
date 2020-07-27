from rest_framework import exceptions, mixins, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from home.api.v1.serializer.auth import SignupSerializer
from home.api.v1.serializer.user import ResetPasswordSerializer, InvitationSerializer, UserEditorUpdate
from home.api.v1.view.auth import internal_login

from home.api.v1.serializer.user import (
    UserCreate,
    UserList,
    UserSerializerBase,
    UserUpdate,
)

from django.contrib.auth import get_user_model

User = get_user_model()


def validate_password(new_password: str, password_field='newPassword'):
    """Validate newPassword field using system password validators."""
    if not new_password:
        raise ValidationError(detail={password_field: 'required'})
    try:
        password_validation.validate_password(password=new_password)
    except DjangoValidationError as django_error:
        raise ValidationError({password_field: list(django_error)})


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Updates and retrieves user accounts."""

    queryset = User.objects.all()
    serializer_class = UserSerializerBase

    def get_queryset(self: 'UserViewSet'):
        """Custom filter permissions."""
        queryset = super().get_queryset()
        role = self.request.user.role
        if role == User.ROLE.ADMIN:
            # admin has access to all users
            pass
        elif role == User.ROLE.EDITOR:
            # customer has access only to himself
            queryset = queryset.filter(pk=self.request.user.pk)
        else:
            raise PermissionDenied
        return queryset

    def get_serializer(self, *args, **kwargs):
        """
        Route serializers based on action.

            list                    UserList
            retrieve                UserUpdate
            update, partial_update  UserUpdate
            create                  UserCreate
        """
        if self.request.user.is_anonymous and AllowAny in self.permission_classes:
            kwargs['context'] = self.get_serializer_context()
            return self.serializer_class(*args, **kwargs)
        invoker_role = self.request.user.role

        # Use ADMIN fields by default in reset framework html forms
        updating_role = User.ROLE.ADMIN
        if args and isinstance(args[0], UserList.Meta.model):
            updating_role = args[0].role
        elif 'data' in kwargs and 'role' in kwargs['data']:
            updating_role = kwargs['data']['role']
        elif kwargs.get('instance'):
            # occurs only when rendering html form by calling /user/1/ from browser (not ajax)
            updating_role = kwargs['instance'].role
        serializer_class = super().get_serializer_class()
        if invoker_role == User.ROLE.ADMIN:
            if self.action == 'list':
                serializer_class = UserList
            elif self.action == 'retrieve':
                if updating_role in {User.ROLE.ADMIN, User.ROLE.EDITOR}:
                    serializer_class = UserSerializerBase
                else:
                    serializer_class = None
            elif self.action in {'update', 'partial_update'}:
                if updating_role in {User.ROLE.ADMIN, User.ROLE.EDITOR}:
                    serializer_class = UserUpdate  # TODO for Natali
                else:
                    serializer_class = None
            elif self.action == 'create':
                if updating_role in {User.ROLE.ADMIN, User.ROLE.EDITOR}:
                    serializer_class = UserCreate  # Admin create form is the same for both roles
                else:
                    serializer_class = None
        elif invoker_role == User.ROLE.EDITOR:
            if self.action == 'retrieve':
                serializer_class = UserSerializerBase  # TODO for Natali
            elif self.action in {'update', 'partial_update'}:
                serializer_class = UserEditorUpdate  # TODO for Natali
            elif self.action in {'list', 'create'}:
                serializer_class = None  # TODO for Natali it's correct
        else:
            serializer_class = None
        if serializer_class is None:
            raise exceptions.ValidationError(detail={self.action: ['Permission error.']})
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    @action(
        detail=False,
        methods=['post'],
        url_path='confirm-token',
        permission_classes=[AllowAny],
        serializer_class=SignupSerializer,
    )
    def confirm_token(self, request):
        """Activate new password by token from Email link (User.send_confirmation_email)."""
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_password = serializer.data['newPassword']
        validate_password(new_password)
        token = serializer.data['token']
        token = token.strip()
        user = get_object_or_404(self.queryset, emailConfirmationToken=token)
        user.emailConfirmationToken = None
        if serializer.data['signUp']:
            user.accepted_terms_date = timezone.now().date()
            user.status = User.STATUS.ACTIVE
        user.set_password(new_password)
        user.save()
        # authenticate new user and respond default /auth content
        return internal_login(request, user.username, new_password)

    @action(
        detail=False,
        methods=['post'],
        url_path='reset-password',
        permission_classes=[AllowAny],
        serializer_class=ResetPasswordSerializer,
    )
    def reset_password(self, request):
        """Password reset functional."""
        user = User.objects.filter(status=User.STATUS.ACTIVE, email=request.data['email']).first()
        if user:
            user.send_confirmation_email()
        return Response(
            data={
                'detail': 'Password reset instructions have been sent to you if you have an account.',
            },
        )

    @action(detail=False, methods=['post'], url_path='send-invitation', serializer_class=InvitationSerializer)
    def send_invitation(self, request):
        """Re-send invitation to user."""
        if self.request.user.role == User.ROLE.ADMIN:
            to_user = User.objects.filter(id=request.data['id']).first()
            if to_user:
                if to_user.status == User.STATUS.ACTIVE:
                    return Response(
                        data={
                            'detail': 'This user is already activated.',
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )
                if to_user.send_invitation_email():
                    to_user.status = User.STATUS.INVITATION
                    to_user.save()
                    return Response(
                        data={
                            'detail': 'Invitation instructions have been sent to the user.',
                        },
                    )
            raise NotFound
        raise PermissionDenied
