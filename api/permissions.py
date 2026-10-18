from rest_framework.permissions import BasePermission
from .models import OrganizationMembership, Issue

class IsOrganizationMember(BasePermission):
    """
    User must be a member of the object's organization.
    """

    def has_object_permission(
        self,
        request,
        view,
        obj
    ):
        if isinstance(obj, Issue):
            organization = obj.project.organization
        else:
            organization = obj

        return OrganizationMembership.objects.filter(
            organization=organization,
            user=request.user
        ).exists()


class IsOrganizationAdminOrOwner(BasePermission):
    """
    User must be an organization owner or admin.
    """

    allowed_roles = {
        OrganizationMembership.Role.OWNER,
        OrganizationMembership.Role.ADMIN,
    }

    def has_object_permission(
        self,
        request,
        view,
        obj
    ):
        organization = obj

        return OrganizationMembership.objects.filter(
            organization=organization,
            user=request.user,
            role__in=self.allowed_roles
        ).exists()       
        
class IsIssueCreatorOrReadOnly(BasePermission):

    def has_object_permission(
        self,
        request,
        view,
        obj
    ):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True

        return obj.created_by == request.user

class IsProjectOrganizationMember(BasePermission):
    """
    User must belong to the project's organization.
    """

    def has_object_permission(
        self,
        request,
        view,
        obj
    ):
        return OrganizationMembership.objects.filter(
            organization=obj.organization,
            user=request.user
        ).exists()

class IsProjectOrganizationAdminOrOwner(BasePermission):
    """
    User must be an owner or admin of the project's organization.
    """

    allowed_roles = {
        OrganizationMembership.Role.OWNER,
        OrganizationMembership.Role.ADMIN,
    }

    def has_object_permission(
        self,
        request,
        view,
        obj
    ):
        return OrganizationMembership.objects.filter(
            organization=obj.organization,
            user=request.user,
            role__in=self.allowed_roles
        ).exists()


class IsIssueOrganizationMember(BasePermission):

    def has_object_permission(
        self,
        request,
        view,
        obj
    ):
        return OrganizationMembership.objects.filter(
            organization=obj.project.organization,
            user=request.user
        ).exists()


class IsOrganizationMembershipMember(
    BasePermission
):
    """
    User must belong to the membership's organization.
    """

    def has_object_permission(
        self,
        request,
        view,
        obj
    ):
        return OrganizationMembership.objects.filter(
            organization=obj.organization,
            user=request.user
        ).exists()


class IsOrganizationMembershipAdminOrOwner(
    BasePermission
):
    """
    User must be an admin or owner of the organization.
    """

    allowed_roles = {
        OrganizationMembership.Role.OWNER,
        OrganizationMembership.Role.ADMIN,
    }

    def has_object_permission(
        self,
        request,
        view,
        obj
    ):
        if obj.role == OrganizationMembership.Role.OWNER:
            return False

        return OrganizationMembership.objects.filter(
            organization=obj.organization,
            user=request.user,
            role__in=self.allowed_roles
        ).exists()