# -*- coding: utf-8 -*-
# Third Party Stuff
from django.db.models import F, Prefetch, Q
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet

# beacon Stuff
from beacon.base import response
from beacon.base.api.mixins import MultipleSerializerMixin

from . import filters, serializers
from .models import (
    ExcludedOrganisationHomepageNavSubCategories,
    HomepageNav,
    HomepageNavCategory,
    HomepageNavSubCategory,
    Organisation,
)
from .services import get_organisation,get_organisation_new


class OrganisationsViewset(ListModelMixin, GenericViewSet):
    serializer_class = serializers.OrganisationSearchSerializer
    queryset = Organisation.objects.filter(is_active=True).order_by("created_at")
    filter_backends = (filters.FullTextSearchFilter,)
    authentication_classes = ()
    permission_classes = ()

    def filter_queryset(self, queryset):
        organisation_qs = super().filter_queryset(queryset)
        if self.action == "list":
            # Beacon team adds "DO NOT USE" in the title of Parent Organisation that
            # has any valid children. This org title then becomes visible on FE
            # webpage as the org title. So they asked us to not return parent
            # organisations if they have children.
            return organisation_qs.exclude(children__isnull=False)
        return organisation_qs


class OrganisationConfigurationView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = serializers.OrganisationSerializer
    queryset = Organisation.objects.filter(is_active=True, parent__isnull=True)

    def get(self, request):
        """
        :param request:
        :return:
        """
        organisation, domain = get_organisation(request, queryset=self.get_queryset())
        if organisation:
            return response.Ok(self.get_serializer(organisation).data)
        raise ValidationError('No organisation exists for "{}"!'.format(domain))


class HomepageNavViewSet(MultipleSerializerMixin, ListModelMixin, GenericViewSet):
    permission_classes = (AllowAny,)
    serializer_class = serializers.HomepageNavSerializer
    queryset = HomepageNav.objects.all()
    serializer_classes = {
        "list": serializers.HomepageNavSerializer,
        "categories": serializers.HomepageNavCategorySerializer,
    }
    organisation = None
    domain = None

    def get_queryset(self, **kwargs):

        organisation, domain = get_organisation_new(
            self.request,
            queryset=Organisation.objects.filter(is_active=True, parent__isnull=True),
            domain=self.domain,
        )

        if organisation:
            self.organisation = organisation
            return HomepageNav.objects.filter(
                Q(is_active=True),
                Q(Q(organisations__organisation=organisation) | Q(is_global=True)),
            ).annotate(sort_order=F("organisations__sort_order"))
        return HomepageNav.objects.filter(is_active=True, is_global=True)

    @action(methods=["GET"], detail=True, url_path="categories")
    def categories(self, request, *args, **kwargs):
        self.domain = request.GET.get('domain')
        instance = self.get_object()
        organisation = self.organisation

        excluded_subcat_qs = (
            ExcludedOrganisationHomepageNavSubCategories.objects.filter(
                organisation=organisation
            )
        )
        excluded_subcategories = excluded_subcat_qs.values_list(
            "homepage_nav_subcategory_id", flat=True
        )
        subcategories = HomepageNavSubCategory.objects.all().exclude(
            id__in=excluded_subcategories
        )
        categories = HomepageNavCategory.objects.prefetch_related(
            Prefetch(
                "subcategories",
                queryset=subcategories,
                to_attr="filtered_subcategories",
            )
        ).filter(homepage_nav=instance)
        serializer_class = self.get_serializer_class()
        context = self.get_serializer_context()
        context["parent_code"] = organisation.parent_code if organisation else None
        return response.Ok(
            serializer_class(categories, many=True, context=context).data
        )
class OrganisationConfigurationView2(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = serializers.OrganisationSerializer
    queryset = Organisation.objects.filter(is_active=True, parent__isnull=True)

    def get(self, request):
        """
        :param request:
        :return:
        """


        organisation, domain = get_organisation_new(request,
                                                    queryset=self.get_queryset().filter(
                                                        domain__regex=request.GET.get('domain')),
                                                    domain=request.GET.get('domain'))

        if organisation:
            return response.Ok(self.get_serializer(organisation).data)
        raise ValidationError('No organisation exists for "{}"!'.format(domain))
