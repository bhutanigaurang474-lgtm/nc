# docs/concepts_docs.py
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

get_concepts_docs = swagger_auto_schema(
    operation_summary="Get List of Concepts",
    manual_parameters=[
        openapi.Parameter(
            "page",
            openapi.IN_QUERY,
            description="Page number for pagination",
            type=openapi.TYPE_INTEGER,
        ),
        openapi.Parameter(
            "page_size",
            openapi.IN_QUERY,
            description="Number of items per page",
            type=openapi.TYPE_INTEGER,
        ),
    ],
    responses={
        200: openapi.Response(
            description="List of concepts will be returned in sorted order of dates and from today to past with pagination",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "concepts": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Items(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "title": openapi.Schema(type=openapi.TYPE_STRING),
                                "slug": openapi.Schema(type=openapi.TYPE_STRING),
                                "preview_image_url": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                                "creation_timestamp": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                                "tags": openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Items(type=openapi.TYPE_STRING),
                                ),
                                "short_description": openapi.Schema(type=openapi.TYPE_STRING),
                            },
                        ),
                    )
                },
            ),
        )
    },
)

get_filtered_concepts_docs = swagger_auto_schema(
    operation_summary="Get Filtered List of Concepts",
    manual_parameters=[
        openapi.Parameter(
            "tags",
            openapi.IN_QUERY,
            description="Comma-separated list of tags",
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            "start_date",
            openapi.IN_QUERY,
            description="Start date (YYYY-MM-DD)",
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            "end_date",
            openapi.IN_QUERY,
            description="End date (YYYY-MM-DD)",
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            "page",
            openapi.IN_QUERY,
            description="Page number",
            type=openapi.TYPE_INTEGER,
        ),
        openapi.Parameter(
            "page_size",
            openapi.IN_QUERY,
            description="Items per page",
            type=openapi.TYPE_INTEGER,
        ),
        openapi.Parameter(
            "search_query",
            openapi.IN_QUERY,
            description="Filter by title",
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            "show_saved_only",
            openapi.IN_QUERY,
            description="Show only saved concepts",
            type=openapi.TYPE_BOOLEAN,
        ),
    ],
    responses={
        200: openapi.Response(
            description="Filtered list of concepts.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "concepts": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Items(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "title": openapi.Schema(type=openapi.TYPE_STRING),
                                "creation_timestamp": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                                "tags": openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Items(type=openapi.TYPE_STRING),
                                ),
                                "description": openapi.Schema(type=openapi.TYPE_STRING),
                            },
                        ),
                    )
                },
            ),
        )
    },
)

get_concept_detail_docs = swagger_auto_schema(
    operation_summary="Get Concept Detail",
    responses={
        200: openapi.Response(
            description="Details of the concept.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "title": openapi.Schema(type=openapi.TYPE_STRING),
                    "preview_image_url": openapi.Schema(type=openapi.TYPE_STRING),
                    "creation_timestamp": openapi.Schema(type=openapi.TYPE_STRING),
                    "tags": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Items(type=openapi.TYPE_STRING),
                    ),
                    "description": openapi.Schema(type=openapi.TYPE_STRING),
                },
            ),
        ),
    },
)

save_concept_docs = swagger_auto_schema(
    operation_summary="Save a Concept",
    responses={
        200: openapi.Response(
            description="Concept saved successfully.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
        ),
        400: openapi.Response(
            description="Bad request. Concept ID is required.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
        ),
        404: openapi.Response(description="Concept not found."),
    },
)

get_concepts_by_date_docs = swagger_auto_schema(
    operation_summary="Get Concept by Date",
    manual_parameters=[
        openapi.Parameter(
            "date",
            openapi.IN_QUERY,
            description="Date in YYYY-MM-DD format",
            type=openapi.TYPE_STRING,
            required=True,
        ),
    ],
    responses={
        200: openapi.Response(
            description="Concept data for the specified date with read status using DailyContent model.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "date": openapi.Schema(type=openapi.TYPE_STRING),
                    "concept_data": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "slug": openapi.Schema(type=openapi.TYPE_STRING),
                            "title": openapi.Schema(type=openapi.TYPE_STRING),
                            "level": openapi.Schema(type=openapi.TYPE_STRING),
                            "type": openapi.Schema(type=openapi.TYPE_STRING),
                            "tags": openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Items(type=openapi.TYPE_STRING),
                            ),
                            "preview_image_url": openapi.Schema(type=openapi.TYPE_STRING),
                            "read": openapi.Schema(type=openapi.TYPE_INTEGER),
                        },
                    ),
                },
            ),
        ),
        400: openapi.Response(
            description="Bad request. Date parameter is required or invalid format.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
        ),
        401: openapi.Response(description="Authentication required."),
        404: openapi.Response(
            description="No content found for the specified date.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
        ),
    },
)