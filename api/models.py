from django.conf import settings
from django.db import models

class Organization(models.Model):

    name = models.CharField(
        max_length=200
    )

    slug = models.SlugField(
        max_length=200,
        unique=True
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_organizations"
    )

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="OrganizationMembership",
        related_name="organizations"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


class OrganizationMembership(models.Model):

    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        MEMBER = "member", "Member"
        VIEWER = "viewer", "Viewer"

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="memberships"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organization_memberships"
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.MEMBER
    )

    joined_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "user"],
                name="unique_organization_member"
            )
        ]

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.organization.name} "
            f"({self.role})"
        )

class Project(models.Model):

    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name="projects"
    )

    name = models.CharField(
        max_length=200
    )

    key = models.CharField(
        max_length=20
    )

    description = models.TextField(
        blank=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_projects"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "key"],
                name="unique_project_key_per_organization"
            )
        ]

    def __str__(self):
        return f"{self.key} - {self.name}"
    
class Issue(models.Model):

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In Progress"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        related_name="issues",
        null=True,
        blank=True
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField()

    priority = models.CharField(
        max_length=20,
        choices=Priority.choices
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_issues"
    )

    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_issues"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title
