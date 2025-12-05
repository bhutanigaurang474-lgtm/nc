from django.db.models import Q
from rest_framework import filters

from .models import ConceptBasedProblem, DatasetBasedProblem


class ProblemFilterBackend(filters.BaseFilterBackend):
    """Custom filter class for handling problem filtering logic"""

    def filter_queryset(self, request, queryset, view=None):
        """Apply all filters to the queryset"""
        if queryset is None:
            return self._filter_mixed_queryset(request, queryset)

        queryset = self._apply_filters_to_queryset(request, queryset)
        return queryset

    def _filter_mixed_queryset(self, request, _):
        """Handle filtering for mixed queryset (concept + dataset)"""
        concept_qs = ConceptBasedProblem.objects.all()
        dataset_qs = DatasetBasedProblem.objects.all()

        concept_filtered = self._apply_filters_to_queryset(request, concept_qs)
        dataset_filtered = self._apply_filters_to_queryset(request, dataset_qs)

        all_problems = list(concept_filtered) + list(dataset_filtered)
        all_problems.sort(key=lambda x: x.creation_timestamp, reverse=True)

        return all_problems

    def _apply_filters_to_queryset(self, request, queryset):
        """Apply filters to a single queryset"""
        problem_levels = request.query_params.get("problem_level", "")
        if problem_levels:
            levels = [level.strip().lower() for level in problem_levels.split(",")]
            queryset = queryset.filter(level__in=levels)

        search_query = request.query_params.get("search_query", "")
        if search_query:
            queryset = queryset.filter(Q(title__icontains=search_query))

        tags = request.query_params.get("tags", "")
        if tags:
            tags_list = [tag.strip() for tag in tags.split(",")]
            queryset = queryset.filter(tags__name__in=tags_list).distinct()

        course_slug = request.query_params.get("course_slug")
        if course_slug:
            queryset = queryset.filter(course__slug=course_slug)

        created_after = request.query_params.get("created_after")
        if created_after:
            queryset = queryset.filter(creation_timestamp__gte=created_after)

        created_before = request.query_params.get("created_before")
        if created_before:
            queryset = queryset.filter(creation_timestamp__lte=created_before)

        author_id = request.query_params.get("author")
        if author_id:
            queryset = queryset.filter(author_id=author_id)

        return queryset
