import itertools
from typing import Any

from authentication.models import User
from django.contrib.postgres.search import (
    TrigramSimilarity,
)
from django.db.models import (
    FloatField,
    TextField,
    Value,
)
from django.db.models.functions import Concat
from django.db.models.query import QuerySet
from django_filters import (
    rest_framework as filters,
)
from rest_framework.filters import SearchFilter
from rest_framework.request import Request


class MySearchFilter(SearchFilter):
    def get_search_terms(self, request: Request) -> str:
        params: str = " ".join(request.query_params.getlist(self.search_param))
        return params.replace(",", " ").split()


class RankedFuzzySearchFilter(MySearchFilter):
    @staticmethod
    def search_queryset(
        queryset: QuerySet[Any], search_fields: tuple[str], search_terms, min_rank
    ) -> QuerySet[Any]:
        full_text_vector: tuple = sum(
            itertools.zip_longest(search_fields, (), fillvalue=Value(" ")), ()
        )
        if len(search_fields) > 1:
            full_text_vector = full_text_vector[:-1]

        full_text_expr: Concat = Concat(*full_text_vector, output_field=TextField())

        similarity: TrigramSimilarity = TrigramSimilarity(full_text_expr, search_terms)
        queryset: QuerySet[Any] = queryset.annotate(rank=similarity)

        if min_rank is None:
            queryset = queryset.filter(rank__gt=0.0)
        elif min_rank > 0.0:
            queryset = queryset.filter(rank__gte=min_rank)

        return queryset[:5]

    def filter_queryset(
        self, request: Request, queryset: QuerySet[Any], view
    ) -> QuerySet[Any]:
        search_fields: tuple[str] = getattr(view, "search_fields", None)
        search_terms: str = " ".join(self.get_search_terms(request))

        if search_fields and search_terms:
            min_rank = getattr(view, "min_rank", None)

            queryset: QuerySet[Any] = self.search_queryset(
                queryset, search_fields, search_terms, min_rank
            )
        else:
            queryset: QuerySet[Any] = queryset.annotate(
                rank=Value(1.0, output_field=FloatField())
            )

        return queryset[:5]


class UserAgeRangeFilter(filters.FilterSet):
    profile__age = filters.RangeFilter()

    class Meta:
        model: User = User
        fields = ["profile__age", "profile__position", "profile__gender", "is_online"]
