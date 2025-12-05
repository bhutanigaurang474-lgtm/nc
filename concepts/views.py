from datetime import datetime

from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from concepts.models import Concept, ConceptsRead
from concepts.swagger_schemas import (
    get_concept_detail_docs,
    get_concepts_by_date_docs,
    get_concepts_docs,
    get_filtered_concepts_docs,
    save_concept_docs,
)
from problems.models import DailyContent


class ConceptsView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = None

    @get_concepts_docs
    def get(self, request):
        """
        Get a list of all concepts.
        """
        page = request.query_params.get("page", 1)
        page_size = request.query_params.get("page_size", 10)

        # Fetching concepts with pagination with django paginator
        concepts = Concept.objects.all().order_by("-creation_timestamp")
        paginator = Paginator(concepts, page_size)
        page_obj = paginator.get_page(page)
        concepts_data = [
            {
                "id": concept.id,
                "title": concept.title,
                "slug": concept.slug,
                "preview_image_url": concept.preview_image_url,
                "creation_timestamp": concept.creation_timestamp,
                "tags": concept.get_tags_list(),
                "short_description": concept.one_liner_desc,
            }
            for concept in page_obj.object_list
        ]
        response_data = {
            "concepts": concepts_data,
            "page": page_obj.number,
            "total_pages": paginator.num_pages,
            "total_items": paginator.count,
        }
        return Response(response_data, status=status.HTTP_200_OK)


class FilteredConceptsView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = None

    @get_filtered_concepts_docs
    def get(self, request):
        """
        Get a filtered list of concepts based on tags and date range.
        """
        tags = request.query_params.get("tags", None)
        start_date = request.query_params.get("start_date", None)
        end_date = request.query_params.get("end_date", None)
        page = request.query_params.get("page", 1)
        page_size = request.query_params.get("page_size", 10)
        search_query = request.query_params.get("search_query", None)
        show_saved_only = request.query_params.get("show_saved_only", False)
        user_id = request.query_params.get("user_id", None)

        concepts = Concept.objects.all()

        if tags:
            tags_list = [tag.strip() for tag in tags.split(",")]
            concepts = concepts.filter(tags__name__in=tags_list).distinct()

        if search_query:
            concepts = concepts.filter(title__icontains=search_query)

        if start_date:
            concepts = concepts.filter(creation_timestamp__gte=start_date)

        if end_date:
            concepts = concepts.filter(creation_timestamp__lte=end_date)

        if show_saved_only and request.user.is_authenticated:
            concepts = concepts.filter(saved_by=request.user)

        if user_id:
            concepts = concepts.filter(concepts_read__user_id=user_id).distinct()

        paginator = Paginator(concepts, page_size)
        page_obj = paginator.get_page(page)

        concepts_data = [
            {
                "id": concept.id,
                "title": concept.title,
                "slug": concept.slug,
                "creation_timestamp": concept.creation_timestamp,
                "tags": concept.get_tags_list(),
                "description": concept.one_liner_desc,
            }
            for concept in page_obj.object_list
        ]

        response_data = {
            "concepts": concepts_data,
            "page": page_obj.number,
            "total_pages": paginator.num_pages,
            "total_items": paginator.count,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class ConceptDetailView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = None

    @get_concept_detail_docs
    def get(self, request, slug):
        """
        Get details of a specific concept by slug.
        """
        concept = get_object_or_404(Concept, slug=slug)
        concept_saved = False
        if request.user.is_authenticated:
            concept_saved = request.user in concept.saved_by.all()

        concept_data = {
            "id": concept.id,
            "title": concept.title,
            "slug": concept.slug,
            "level": concept.level,
            "preview_image_url": concept.preview_image_url,
            "creation_timestamp": concept.creation_timestamp,
            "tags": concept.get_tags_list(),
            "one_liner_desc": concept.one_liner_desc,
            "description": concept.description,
            "concept_saved": concept_saved,
        }
        return Response(concept_data, status=status.HTTP_200_OK)


class SaveConceptView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = None

    @save_concept_docs
    def post(self, request, concept_id):
        concept = get_object_or_404(Concept, id=concept_id)
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"message": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if user in concept.saved_by.all():
            concept.saved_by.remove(user)
            message = "Concept saved successfully."
        else:
            concept.saved_by.add(user)
            message = "Concept unsaved successfully."

        return Response(
            {"message": message, "saved_count": concept.saved_by.count()},
            status=status.HTTP_200_OK,
        )


class ConceptsByDateView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = None

    @get_concepts_by_date_docs
    def get(self, request):
        """
        Get concept data for a particular date using DailyContent model.
        """
        date_str = request.query_params.get("date")
        if not date_str:
            return Response(
                {"message": "Date query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"message": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get daily content for the given date
        try:
            daily_content = DailyContent.objects.get(date=date)
        except DailyContent.DoesNotExist:
            return Response(
                {"message": "No content found for the specified date."},
                status=status.HTTP_404_NOT_FOUND,
            )

        concept = daily_content.concept

        # Check if concept was read by the user on this date
        concept_read = ConceptsRead.objects.filter(
            user=request.user,
            concept=concept,
            read_timestamp__date=date,
        ).exists()

        concept_data = {
            "id": concept.id,
            "slug": concept.slug,
            "title": concept.title,
            "level": concept.level,
            "type": concept.concept_type,
            "tags": concept.get_tags_list(),
            "preview_image_url": concept.preview_image_url,
            "read": int(concept_read),
        }

        return Response(
            {
                "date": date_str,
                "concept_data": concept_data,
            },
            status=status.HTTP_200_OK,
        )
