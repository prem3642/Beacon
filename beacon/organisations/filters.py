# -*- coding: utf-8 -*-
from urllib.parse import unquote

from django.conf import settings
from django.contrib.postgres.search import SearchQuery
from rest_framework import filters
from rest_framework.exceptions import ValidationError


class FullTextSearchFilter(filters.BaseFilterBackend):
    """
    Query organisations on the basis of `search_term`
    """

    def filter_queryset(self, request, queryset, view):
        search_term = request.query_params.get("search_term", None)
        if search_term is None:
            raise ValidationError("Query parameter search_term is required.")
        if len(search_term) < settings.ORG_SEARCH_TERM_CHAR_LIMIT:
            raise ValidationError(
                f"search_term should be at least {settings.ORG_SEARCH_TERM_CHAR_LIMIT} char(s) long."
            )
        search_term = unquote(search_term)
        search_query = SearchQuery(value=search_term, config="pg_catalog.english")
        return queryset.filter(search_vector=search_query)
