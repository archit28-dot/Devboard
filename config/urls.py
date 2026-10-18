from django.contrib import admin
from django.urls import include, path

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from api.views import (
    IssueViewSet,
    OrganizationViewSet,
    ProjectViewSet,
    RegisterView,
    OrganizationMembershipDetail
)


router = DefaultRouter()

router.register(
    "organizations",
    OrganizationViewSet,
    basename="organization"
)

router.register(
    "projects",
    ProjectViewSet,
    basename="project"
)

router.register(
    "issues",
    IssueViewSet,
    basename="issue"
)


urlpatterns = [
    path(
        "admin/",
        admin.site.urls
    ),

    path(
        "api/",
        include(router.urls)
    ),

    path(
        "api/auth/register/",
        RegisterView.as_view(),
        name="register"
    ),

    path(
        "api/auth/login/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair"
    ),

    path(
        "api/auth/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh"
    ),
    path(
    "api/organizations/<int:organization_pk>/members/<int:pk>/",
    OrganizationMembershipDetail.as_view(),
),
]