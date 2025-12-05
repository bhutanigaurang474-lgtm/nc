from django.urls import path
from concepts.views import (
    ConceptsView,
    FilteredConceptsView,
    ConceptDetailView,
    SaveConceptView,
    ConceptsByDateView,
)

urlpatterns = [
    path("", ConceptsView.as_view(), name="concepts"),
    path(
        "filtered-concepts/", FilteredConceptsView.as_view(), name="filtered-concepts"
    ),
    path("by-date/", ConceptsByDateView.as_view(), name="concepts-by-date"),
    path("<slug:slug>/", ConceptDetailView.as_view(), name="concept-detail"),
    path("<int:concept_id>/save/", SaveConceptView.as_view(), name="concept-save"),
]
