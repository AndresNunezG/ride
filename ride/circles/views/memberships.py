# Django REST framework
from rest_framework import mixins, viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import Serializer

# Models
from ride.circles.models import Circle, Membership, Invitation

# Serializers
from ride.circles.serializers import MembershipSerializer, AddMemberSerializer

# Permissions
from rest_framework.permissions import IsAuthenticated
from ride.circles.permissions import IsActiveCircleMember
from ride.circles.permissions.memberships import IsAdminOrMembershipOwner, IsSelfMember


class MembershipViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """Circle membership viewset"""

    serializer_class = MembershipSerializer

    def dispatch(self, request, *args, **kwargs):
        """Verify that the circle exists"""
        slug_name = kwargs["slug_name"]
        self.circle = get_object_or_404(Circle, slug_name=slug_name)
        return super(MembershipViewSet, self).dispatch(request, *args, **kwargs)

    def get_permissions(self):
        """Assign permissions based on action"""
        permissions = [IsAuthenticated]
        if self.action != "create":
            permissions.append(IsActiveCircleMember)
        if self.action == "destroy":
            permissions.append(IsAdminOrMembershipOwner)
        if self.action == "invitations":
            permissions.append(IsSelfMember)
        return [p() for p in permissions]

    def get_queryset(self):
        """Return circle members"""
        return Membership.objects.filter(circle=self.circle, is_active=True)

    def get_object(self):
        """Return the circle member by using the user's username"""
        return get_object_or_404(
            Membership,
            user__username=self.kwargs["pk"],
            circle=self.circle,
            is_active=True,
        )

    def perform_destroy(self, instance):
        """Disable membership"""
        instance.is_active = False
        instance.save()

    def create(self, request, *args, **kwargs):
        serializer = AddMemberSerializer(
            data=request.data, context={"circle": self.circle, "request": request}
        )

        serializer.is_valid(raise_exception=True)
        member = serializer.save()
        # self.get_serializer use the class serializer MembershipSerializer
        data = self.get_serializer(member).data
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def invitations(self, request, *args, **kwargs):
        """Retrieve a member's invitations breakdown
        Will return a list containing all the members that have
        used its invitations and another list containing the
        invitations that haven't being used yet.
        """
        member = self.get_object()
        invited_members = Membership.objects.filter(
            circle=self.circle, invited_by=request.user, is_active=True
        )

        unused_invitations = Invitation.objects.filter(
            circle=self.circle,
            issued_by=request.user,
            used=False,
        ).values_list("code")

        diff = member.remaining_invitations - len(unused_invitations)

        invitations = [invitation[0] for invitation in unused_invitations]
        for _ in range(0, diff):
            invitations.append(
                Invitation.objects.create(
                    issued_by=request.user, circle=self.circle
                ).code
            )

        data = {
            "used_invitations": MembershipSerializer(invited_members, many=True).data,
            "invitations": invitations,
        }

        return Response(data)


# // circles/<circle_lug_name>/members/

# {
#   "count": 2,
#   "next": null,
#   "previous": null,
#   "results": [
#     {
#       "user": {
#         "username": "camilo",
#         "first_name": "camilo",
#         "last_name": "nunez",
#         "email": "camilo@nunez.com",
#         "phone": "1234567890",
#         "profile": {
#           "picture": null,
#           "biography": "",
#           "rides_taken": 0,
#           "rides_offered": 0,
#           "reputation": 5
#         }
#       },
#       "is_admin": false,
#       "is_active": true,
#       "used_invitations": 0,
#       "remaining_invitations": 0,
#       "invited_by": "camsky",
#       "rides_taken": 0,
#       "rides_offered": 0,
#       "joined_at": "2021-12-15T03:31:14.987923Z"
#     },
#     {
#       "user": {
#         "username": "camsky",
#         "first_name": "camilo",
#         "last_name": "nunez",
#         "email": "camsky@camsky.com",
#         "phone": "3165203926",
#         "profile": {
#           "picture": "http://localhost:8000/media/users/pictures/camilo.png",
#           "biography": "Enginner",
#           "rides_taken": 0,
#           "rides_offered": 0,
#           "reputation": 5
#         }
#       },
#       "is_admin": true,
#       "is_active": true,
#       "used_invitations": 0,
#       "remaining_invitations": 10,
#       "invited_by": null,
#       "rides_taken": 0,
#       "rides_offered": 0,
#       "joined_at": "2021-12-05T17:26:49.194603Z"
#     }
#   ]
# }

# // circles/<circle_lug_name>/members/camsky/invitations/

# {
#   "used_invitations": [
#     {
#       "user": {
#         "username": "camilo",
#         "first_name": "camilo",
#         "last_name": "nunez",
#         "email": "camilo@nunez.com",
#         "phone": "1234567890",
#         "profile": {
#           "picture": null,
#           "biography": "",
#           "rides_taken": 0,
#           "rides_offered": 0,
#           "reputation": 5
#         }
#       },
#       "is_admin": false,
#       "is_active": true,
#       "used_invitations": 0,
#       "remaining_invitations": 0,
#       "invited_by": "camsky",
#       "rides_taken": 0,
#       "rides_offered": 0,
#       "joined_at": "2021-12-15T03:31:14.987923Z"
#     }
#   ]
# }
