from rest_framework import generics, permissions, viewsets, action, status
from django.db import transaction
from api.permissions import (IsIssueCreatorOrReadOnly, IsOrganizationMember, 
                             IsOrganizationAdminOrOwner,IsProjectOrganizationAdminOrOwner,
                             IsProjectOrganizationMember,IsIssueOrganizationMember,
                             IsOrganizationMembershipMember,IsOrganizationMembershipAdminOrOwner)
from rest_framework.permissions import IsAuthenticated
from .auth_serializers import RegisterSerializer
from .models import Issue
from .serializers import(
    IssueSerializer,
    OrganizationSerializer,
    ProjectSerializer,
    OrganizationMembershipSerializer,
    )
from django.shortcuts import get_object_or_404 

from .models import Organization, OrganizationMembership, Project

class OrganizationViewSet(
    viewsets.ModelViewSet
):
    serializer_class = OrganizationSerializer

    def get_queryset(self):
        return (
            Organization.objects
            .filter(
                memberships__user=self.request.user
            )
            .select_related("owner")
            .prefetch_related(
                "memberships__user"
            )
            .distinct()
        )

    def get_permissions(self):

        if self.action == "members":

            if self.request.method == "GET":
                permission_classes = [
                    permissions.IsAuthenticated,
                    IsOrganizationMember,
                ]

            else:
                permission_classes = [
                    permissions.IsAuthenticated,
                    IsOrganizationAdminOrOwner,
                ]

        elif self.action in [
            "list",
            "retrieve"
        ]:
            permission_classes = [
                permissions.IsAuthenticated,
                IsOrganizationMember,
            ]

        elif self.action in [
            "update",
            "partial_update",
            "destroy"
        ]:
            permission_classes = [
                permissions.IsAuthenticated,
                IsOrganizationAdminOrOwner,
            ]

        else:
            permission_classes = [
                permissions.IsAuthenticated,
            ]

        return [
            permission()
            for permission in permission_classes
        ]

    def perform_create(self, serializer):

        with transaction.atomic():

            organization = serializer.save(
                owner=self.request.user
            )

            OrganizationMembership.objects.create(
                organization=organization,
                user=self.request.user,
                role=OrganizationMembership.Role.OWNER
            )

    @action(
        detail=True,
        methods=["GET", "POST"],
        url_path="members"
    )
    def members(self, request, pk=None):

        organization = self.get_object()

        if request.method == "GET":

            memberships = (
                organization.memberships
                .select_related("user")
                .all()
            )

            serializer = OrganizationMembershipSerializer(
                memberships,
                many=True,
                context={
                    "request": request,
                    "organization": organization,
                }
            )

            return Response(serializer.data)

        serializer = OrganizationMembershipSerializer(
            data=request.data,
            context={
                "request": request,
                "organization": organization,
            }
        )

        serializer.is_valid(
            raise_exception=True
        )

        membership = serializer.save(
            organization=organization
        )

        return Response(
            OrganizationMembershipSerializer(
                membership,
                context={
                    "request": request,
                    "organization": organization,
                }
            ).data,
            status=status.HTTP_201_CREATED
        )


class ProjectViewSet(viewsets.ModelViewSet):

    serializer_class = ProjectSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]
    def get_queryset(self):
        return(
            Project.objects.filter(
                organization__members__user = self.request.user
            ).select_related("organization","created_by")
        )
    
    def get_permissions(self):

        if self.action in [
            "list",
            "retrieve"
        ]:
            permission_classes = [
                permissions.IsAuthenticated,
                IsProjectOrganizationMember,
            ]

        elif self.action in [
            "update",
            "partial_update",
            "destroy"
        ]:
            permission_classes = [
                permissions.IsAuthenticated,
                IsProjectOrganizationAdminOrOwner,
            ]

        else:
            permission_classes = [
                permissions.IsAuthenticated,
            ]

        return [
            permission()
            for permission in permission_classes
        ]
    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user
        )

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [
        permissions.AllowAny
    ]


class IssueViewSet(viewsets.ModelViewSet):

    serializer_class = IssueSerializer

    def get_queryset(self):
        return (
            Issue.objects
            .filter(
                project__organization__memberships__user=self.request.user
            )
            .select_related(
                "project",
                "created_by",
                "assignee"
            )
        )

    permission_classes = [
        permissions.IsAuthenticated,
        IsIssueOrganizationMember,
        IsIssueCreatorOrReadOnly,
    ]
    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user
        )
        

class OrganizationMembershipDetail(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = OrganizationMembershipSerializer

    def get_queryset(self):

        return (
            OrganizationMembership.objects
            .filter(
                organization_id=self.kwargs[
                    "organization_pk"
                ]
            )
            .select_related(
                "organization",
                "user"
            )
        )

    def get_serializer_context(self):

        context = super().get_serializer_context()

        context["organization"] = get_object_or_404(
            Organization,
            pk=self.kwargs["organization_pk"]
        )

        return context

    def get_permissions(self):

        if self.request.method == "GET":
            permission_classes = [
                permissions.IsAuthenticated,
                IsOrganizationMembershipMember,
            ]

        else:
            permission_classes = [
                permissions.IsAuthenticated,
                IsOrganizationMembershipAdminOrOwner,
            ]

        return [
            permission()
            for permission in permission_classes
        ]