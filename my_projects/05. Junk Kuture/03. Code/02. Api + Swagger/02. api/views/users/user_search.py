from datetime import timedelta

from django.db.models import Q
from django.utils import timezone
from django.utils.decorators import method_decorator

from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from services.api.serializers.users.user_search import UserSearchSerializer
from services.api.swagger.docs.user_search import doc_decorator

from apps.main.choices import ApplicationStatus, MemberStatus
from apps.main.models import Application, Member
from apps.main.utils import search_active_application_user_creator
from apps.users.choices import UserType
from apps.users.models import User


@method_decorator(name='get', decorator=doc_decorator)
class UserSearchView(ListAPIView):
    serializer_class = UserSearchSerializer
    queryset = User.objects.filter(
        type__in=[UserType.CREATOR, UserType.EDUCATOR],
    )
    search_fields = ('$username', '$name')
    RESULTS_SIZE = 10
    pagination_class = None

    def get_queryset(self):
        application = search_active_application_user_creator(
            user=self.request.user,
        )
        region_ids = Application.objects.filter(id=application.id).values_list(
            'competition__regions__id', flat=True,
        )
        current_time = timezone.now()
        active_applications_exclude = Application.objects.filter(
            Q(
                status__in=[
                    ApplicationStatus.CREATED.value,
                    ApplicationStatus.AWAITING_PARTICIPANTS.value,
                    ApplicationStatus.ACCEPTED.value,
                ],
                competition__starts_at__lte=current_time,
                competition__ends_at__gte=current_time,
            ) |
            Q(
                status=ApplicationStatus.CREATED.value,
                created_timestamp__gte=current_time - timedelta(hours=24),
            ),
        ).distinct().values('user_id')
        active_members_exclude = Member.objects.filter(
            status=MemberStatus.ACCEPTED,
            user__type=UserType.CREATOR.value,
            application__status__in=[
                ApplicationStatus.AWAITING_PARTICIPANTS.value,
                ApplicationStatus.ACCEPTED.value,
            ],
            application__competition__starts_at__lte=current_time,
            application__competition__ends_at__gte=current_time,
        ).distinct().values('user_id')
        return self.queryset.filter(region__in=region_ids).exclude(
            id=application.user.id,
        ).exclude(id__in=active_applications_exclude).exclude(
            id__in=active_members_exclude,
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(
            self.get_queryset(),
        )[:self.RESULTS_SIZE]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
