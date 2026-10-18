from rest_framework import serializers
from .models import Issue
from django.contrib.auth import get_user_model
from .models import (
    Issue,
    Organization,
    OrganizationMembership,
    Project,
)


User = get_user_model()


class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
        ]
        read_only_fields = [
            "id",
            "username",
            "email"
        ]
        
        
        
class OrganizationMembershipSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)

    class Meta:
        model = OrganizationMembership
        fields = [
            "id",
            "user",
            "role",
            "joined_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "joined_at"
        ]
        
        
    
class OrganizationSerializer(serializers.ModelSerializer):

    owner = UserSummarySerializer(
        read_only=True
    )

    memberships = OrganizationMembershipSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "slug",
            "owner",
            "memberships",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "owner",
            "memberships",
            "created_at",
        ]
        
        
        
class ProjectSerializer(serializers.ModelSerializer):

    organization = OrganizationSerializer(
        read_only=True
    )

    organization_id = serializers.PrimaryKeyRelatedField(
        source="organization",
        queryset=Organization.objects.all(),
        write_only=True
    )

    created_by = UserSummarySerializer(
        read_only=True
    )

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "key",
            "description",
            "organization",
            "organization_id",
            "created_by",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "organization",
            "created_by",
            "created_at",
        ]
        def validate_organization_id(self, value):
            request = self.context["request"]

            is_member = OrganizationMembership.objects.filter(
                organization=value,
                user=request.user
            ).exists()

            if not is_member:
                raise serializers.ValidationError(
                    "You must be a member of this organization."
                )

            return value
        


class ProjectSummarySerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "key",
        ]
        read_only_fields = [
            "id",
            "name",
            "key",
        ]
        
        
class IssueSerializer(serializers.ModelSerializer):

    project = ProjectSummarySerializer(
        read_only=True
    )

    project_id = serializers.PrimaryKeyRelatedField(
        source="project",
        queryset=Project.objects.all(),
        write_only=True
    )

    created_by = UserSummarySerializer(
        read_only=True
    )

    assignee = UserSummarySerializer(
        read_only=True
    )

    assignee_id = serializers.PrimaryKeyRelatedField(
        source="assignee",
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Issue

        fields = [
            "id",
            "title",
            "description",
            "priority",
            "status",
            "project",
            "project_id",
            "created_by",
            "assignee",
            "assignee_id",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "project",
            "created_by",
            "assignee",
            "created_at",
        ]

        extra_kwargs = {
            "title": {
                "allow_blank": False
            },
            "description": {
                "allow_blank": False
            },
        }

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "Title cannot contain only whitespace."
            )

        return value.strip()

    def validate(self, attrs):

        request = self.context["request"]

        project = attrs.get(
            "project",
            getattr(self.instance, "project", None)
        )

        assignee = attrs.get(
            "assignee",
            getattr(self.instance, "assignee", None)
        )

        if project:

            is_project_member = OrganizationMembership.objects.filter(
                organization=project.organization,
                user=request.user
            ).exists()

            if not is_project_member:
                raise serializers.ValidationError({
                    "project_id": (
                        "You cannot create or modify an issue "
                        "in an organization you do not belong to."
                    )
                })

        if assignee and project:

            is_assignee_member = OrganizationMembership.objects.filter(
                organization=project.organization,
                user=assignee
            ).exists()

            if not is_assignee_member:
                raise serializers.ValidationError({
                    "assignee_id": (
                        "The assignee must be a member "
                        "of the project's organization."
                    )
                })

        new_status = attrs.get("status")

        if (
            self.instance
            and self.instance.status == Issue.Status.CLOSED
            and new_status == Issue.Status.IN_PROGRESS
        ):
            raise serializers.ValidationError({
                "status": (
                    "A closed issue cannot be moved directly "
                    "to in_progress. Reopen it first."
                )
            })

        return attrs
    
class OrganizationMembershipSerializer(
    serializers.ModelSerializer
):
    user = UserSummarySerializer(
        read_only=True
    )

    user_id = serializers.PrimaryKeyRelatedField(
        source="user",
        queryset=User.objects.all(),
        write_only=True
    )

    class Meta:
        model = OrganizationMembership

        fields = [
            "id",
            "user",
            "user_id",
            "role",
            "joined_at",
        ]

        read_only_fields = [
            "id",
            "user",
            "joined_at",
        ]

    def validate(self, attrs):
        organization = self.context["organization"]
        user = attrs.get("user")
        role = attrs.get(
            "role",
            OrganizationMembership.Role.MEMBER
        )

        if role == OrganizationMembership.Role.OWNER:
            raise serializers.ValidationError({
                "role": (
                    "The organization owner is created "
                    "when the organization is created."
                )
            })

        if user:
            if not user.is_active:
                raise serializers.ValidationError({
                    "user_id": "This user is not active."
                })

            already_member = (
                OrganizationMembership.objects
                .filter(
                    organization=organization,
                    user=user
                )
                .exclude(
                    pk=getattr(self.instance, "pk", None)
                )
                .exists()
            )

            if already_member:
                raise serializers.ValidationError({
                    "user_id": (
                        "This user is already a member "
                        "of the organization."
                    )
                })

        return attrs