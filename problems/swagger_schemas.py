# your_app/swagger_schemas.py
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

monthly_content_view_swagger_schema = swagger_auto_schema(
    operation_description="Get Calender data also same response will be used for concept of the day and problem of the day",
    manual_parameters=[
        openapi.Parameter(
            "year",
            openapi.IN_QUERY,
            description="Year in YYYY format",
            type=openapi.TYPE_INTEGER,
            required=True,
        ),
        openapi.Parameter(
            "month",
            openapi.IN_QUERY,
            description="Month in MM format (1-12)",
            type=openapi.TYPE_INTEGER,
            required=True,
        ),
    ],
    responses={
        200: openapi.Response(
            description="Monthly content retrieved successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "monthly_content": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        additional_properties=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "problem_data": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                        "title": openapi.Schema(
                                            type=openapi.TYPE_STRING
                                        ),
                                        "level": openapi.Schema(
                                            type=openapi.TYPE_STRING
                                        ),
                                        "type": openapi.Schema(
                                            type=openapi.TYPE_STRING
                                        ),
                                        "tags": openapi.Schema(
                                            type=openapi.TYPE_ARRAY,
                                            items=openapi.Schema(
                                                type=openapi.TYPE_STRING
                                            ),
                                        ),
                                        "solved": openapi.Schema(
                                            type=openapi.TYPE_BOOLEAN
                                        ),
                                    },
                                ),
                                "concept_data": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                        "title": openapi.Schema(
                                            type=openapi.TYPE_STRING
                                        ),
                                        "level": openapi.Schema(
                                            type=openapi.TYPE_STRING
                                        ),
                                        "type": openapi.Schema(
                                            type=openapi.TYPE_STRING
                                        ),
                                        "tags": openapi.Schema(
                                            type=openapi.TYPE_ARRAY,
                                            items=openapi.Schema(
                                                type=openapi.TYPE_STRING
                                            ),
                                        ),
                                        "read": openapi.Schema(
                                            type=openapi.TYPE_BOOLEAN
                                        ),
                                    },
                                ),
                            },
                        ),
                    ),
                    "percentage_solved": openapi.Schema(
                        type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT
                    ),
                },
            ),
            examples={
                "application/json": {
                    "monthly_content": {
                        "2025-04-01": {
                            "problem_data": {
                                "id": 101,
                                "title": "Two Sum",
                                "level": "Easy",
                                "type": "Algorithm",
                                "tags": ["array", "hashmap"],
                                "solved": 1,
                            },
                            "concept_data": {
                                "id": 201,
                                "title": "Hash Tables",
                                "level": "Medium",
                                "type": "DSA",
                                "tags": ["hashing", "dictionary"],
                                "read": 0,
                            },
                        },
                        "2025-04-02": {
                            "problem_data": {
                                "id": 102,
                                "title": "Merge Intervals",
                                "level": "Medium",
                                "type": "Algorithm",
                                "tags": ["intervals", "sorting"],
                                "solved": 0,
                            },
                            "concept_data": {
                                "id": 202,
                                "title": "Sorting Algorithms",
                                "level": "Easy",
                                "type": "DSA",
                                "tags": ["sorting", "comparison"],
                                "read": 0,
                            },
                        },
                    },
                    "percentage_solved": 6.67,
                }
            },
        ),
        400: openapi.Response(
            description="Bad Request - Invalid parameters",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
            examples={
                "application/json": {
                    "message": "Invalid year or month. Use YYYY for year and MM (1-12) for month"
                }
            },
        ),
        404: openapi.Response(
            description="Not Found - No content available",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
            examples={
                "application/json": {"message": "No content available for this month"}
            },
        ),
    },
)

user_history_view_swagger_schema = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            "date",
            openapi.IN_QUERY,
            description="Date in YYYY-MM-DD format",
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    responses={
        200: openapi.Response(
            description="Content retrieved successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "date": openapi.Schema(type=openapi.TYPE_STRING),
                    "problem_of_the_day": openapi.Schema(type=openapi.TYPE_STRING),
                    "concept_of_the_day": openapi.Schema(type=openapi.TYPE_STRING),
                },
            ),
            examples={
                "application/json": {
                    "date": "2024-03-07",
                    "problem_of_the_day": "Solve two sum problem",
                    "concept_of_the_day": "Binary Search",
                }
            },
        ),
        400: openapi.Response(
            description="Bad Request - Invalid date format",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
            examples={
                "application/json": {"message": "Invalid date format. Use YYYY-MM-DD"}
            },
        ),
        404: openapi.Response(
            description="Not Found - No content available",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
            examples={
                "application/json": {
                    "message": "No content available for the selected date"
                }
            },
        ),
    },
)

problems_table_view_swagger_schema = swagger_auto_schema(
    operation_description="Get problems based on filters. Either `problem_type` or `course_slug` must be provided.",
    manual_parameters=[
        openapi.Parameter(
            "problem_type",
            openapi.IN_QUERY,
            description="Filter by problem type ('concept' or 'dataset')",
            type=openapi.TYPE_STRING,
            required=False,
        ),
        openapi.Parameter(
            "problem_level",
            openapi.IN_QUERY,
            description="Filter by problem level ('easy', 'medium', 'hard')",
            type=openapi.TYPE_STRING,
            required=False,
        ),
        openapi.Parameter(
            "search_query",
            openapi.IN_QUERY,
            description="Search by problem title",
            type=openapi.TYPE_STRING,
            required=False,
        ),
        openapi.Parameter(
            "tags",
            openapi.IN_QUERY,
            description="Filter problems by tags (comma-separated)",
            type=openapi.TYPE_STRING,
            required=False,
        ),
        openapi.Parameter(
            "course_slug",
            openapi.IN_QUERY,
            description="Filter problems by Course",
            type=openapi.TYPE_STRING,
            required=False,
        ),
        openapi.Parameter(
            "page",
            openapi.IN_QUERY,
            description="Page number for pagination",
            type=openapi.TYPE_INTEGER,
            required=False,
        ),
        openapi.Parameter(
            "page_size",
            openapi.IN_QUERY,
            description="Number of problems per page",
            type=openapi.TYPE_INTEGER,
            required=False,
        ),
    ],
    responses={
        200: openapi.Response(
            description="Problems table retrieved successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "problems": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "title": openapi.Schema(type=openapi.TYPE_STRING),
                                "level": openapi.Schema(type=openapi.TYPE_STRING),
                                "acceptance_rate": openapi.Schema(
                                    type=openapi.TYPE_NUMBER
                                ),
                                "submission_status": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                                "type": openapi.Schema(type=openapi.TYPE_STRING),
                                "tags": openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Schema(type=openapi.TYPE_STRING),
                                ),
                                "notes": openapi.Schema(type=openapi.TYPE_STRING),
                            },
                        ),
                    )
                },
            ),
            examples={
                "application/json": {
                    "problems": [
                        {
                            "id": 1,
                            "title": "Two Sum",
                            "level": "Easy",
                            "acceptance_rate": 0.75,
                            "submission_status": 1,
                            "type": "Dataset",
                            "tags": ["Array", "Hash Table"],
                            "notes": "Use a hash map to store indices of the numbers.",
                        },
                    ]
                }
            },
        ),
        404: openapi.Response(
            description="Not Found - No problems available",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
            examples={
                "application/json": {"message": "No problems available in the database"}
            },
        ),
    },
)

notes_post_swagger_schema = swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "notes": openapi.Schema(
                type=openapi.TYPE_STRING, description="Notes content"
            ),
            "problem_id": openapi.Schema(
                type=openapi.TYPE_INTEGER, description="Problem ID"
            ),
            "problem_type": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Problem type ('concept' or 'dataset')",
            ),
        },
    ),
    responses={
        200: openapi.Response(description="Notes saved successfully"),
        400: openapi.Response(description="Bad Request - Invalid parameters"),
        404: openapi.Response(description="Not Found - Problem not found"),
    },
)

notes_get_swagger_schema = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            "problem_id",
            openapi.IN_QUERY,
            description="Problem ID",
            type=openapi.TYPE_INTEGER,
            required=True,
        ),
        openapi.Parameter(
            "problem_type",
            openapi.IN_QUERY,
            description="Problem type ('concept' or 'dataset')",
            type=openapi.TYPE_STRING,
            required=True,
        ),
    ],
    responses={
        200: openapi.Response(
            description="Notes retrieved successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "notes": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "problem_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "notes": openapi.Schema(type=openapi.TYPE_STRING),
                            },
                        ),
                    )
                },
            ),
            examples={
                "application/json": {
                    "notes": [
                        {
                            "problem_id": 1,
                            "notes": "This is a sample note.",
                        },
                    ]
                }
            },
        ),
        404: openapi.Response(
            description="Not Found - No notes available",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
            examples={
                "application/json": {
                    "message": "No notes available for the selected problem"
                }
            },
        ),
    },
)

problem_view_swagger_schema = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            "slug",
            openapi.IN_PATH,
            description="Problem Slug",
            type=openapi.TYPE_STRING,
            required=True,
        ),
        openapi.Parameter(
            "type",
            openapi.IN_PATH,
            description="Problem type ('concept' or 'dataset')",
            type=openapi.TYPE_STRING,
            required=True,
        ),
    ],
    responses={
        200: openapi.Response(
            description="Problem details retrieved successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "problem": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "title": openapi.Schema(type=openapi.TYPE_STRING),
                            "description": openapi.Schema(type=openapi.TYPE_STRING),
                            "level": openapi.Schema(type=openapi.TYPE_STRING),
                            "acceptance_rate": openapi.Schema(
                                type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT
                            ),
                            "evaluation_file_path": openapi.Schema(
                                type=openapi.TYPE_STRING
                            ),
                            "solution_file_path": openapi.Schema(
                                type=openapi.TYPE_STRING
                            ),
                            "test_data_file_path": openapi.Schema(
                                type=openapi.TYPE_STRING
                            ),
                            "data_available_to_user_file_path": openapi.Schema(
                                type=openapi.TYPE_STRING
                            ),
                            "ideal_metrics_json_file_path": openapi.Schema(
                                type=openapi.TYPE_STRING
                            ),
                        },
                    )
                },
            ),
            examples={
                "application/json": {
                    "problem": {
                        "id": 1,
                        "title": "Two Sum",
                        "description": "Given an array of integers, return indices of the two numbers such that they add up to a specific target.",
                        "level": "Easy",
                        "acceptance_rate": 0.75,
                        "evaluation_file_path": "/path/to/evaluation/file",
                        "solution_file_path": "/path/to/solution/file",
                        "test_data_file_path": "/path/to/test/data/file",
                        "data_available_to_user_file_path": "/path/to/user/data/file",
                        "ideal_metrics_json_file_path": "/path/to/metrics/file",
                    }
                }
            },
        ),
        404: openapi.Response(
            description="Not Found - Problem not found",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
            examples={
                "application/json": {"message": "Problem not found in the database"}
            },
        ),
        400: openapi.Response(
            description="Bad Request - Invalid parameters",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
            examples={
                "application/json": {
                    "message": "Invalid problem ID or type. Use 'concept' or 'dataset' for problem type."
                }
            },
        ),
    },
)

run_code_post_swagger_schema = swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "run_only": openapi.Schema(
                type=openapi.TYPE_BOOLEAN, description="Run only the code"
            ),
            "code": openapi.Schema(type=openapi.TYPE_STRING, description="Code to run"),
            "problem_id": openapi.Schema(
                type=openapi.TYPE_INTEGER, description="Problem ID"
            ),
            "problem_type": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Problem type ('concept' or 'dataset')",
            ),
            "testcases": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_STRING,
                ),
            ),
        },
    ),
    responses={
        200: openapi.Response(
            description="Code run successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "verdict": openapi.Schema(type=openapi.TYPE_STRING),
                    "stdout": openapi.Schema(type=openapi.TYPE_STRING),
                    "stderr": openapi.Schema(type=openapi.TYPE_STRING),
                    "time_taken": openapi.Schema(type=openapi.TYPE_NUMBER),
                    "memory_taken": openapi.Schema(type=openapi.TYPE_NUMBER),
                },
            ),
        ),
        400: openapi.Response(description="Bad Request - Invalid parameters"),
        404: openapi.Response(description="Not Found - Problem not found"),
    },
)


submission_get_swagger_schema = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            "type",
            openapi.IN_PATH,
            description="Problem type ('concept' or 'dataset')",
            type=openapi.TYPE_STRING,
            required=True,
        ),
        openapi.Parameter(
            "slug",
            openapi.IN_PATH,
            description="Problem slug",
            type=openapi.TYPE_STRING,
            required=True,
        ),
    ],
    responses={
        200: openapi.Response(description="Submissions retrieved successfully"),
        400: openapi.Response(description="Bad Request - Invalid parameters"),
        404: openapi.Response(description="Not Found - Problem not found"),
    },
)

comment_get_swagger_schema = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            "type",
            openapi.IN_PATH,
            description="Problem type ('concept' or 'dataset')",
            type=openapi.TYPE_STRING,
            required=True,
        ),
        openapi.Parameter(
            "slug",
            openapi.IN_PATH,
            description="Problem slug",
            type=openapi.TYPE_STRING,
            required=True,
        ),
    ],
    responses={
        200: openapi.Response(description="Comments retrieved successfully"),
        400: openapi.Response(description="Bad Request - Invalid parameters"),
        404: openapi.Response(description="Not Found - Problem not found"),
    },
)

comment_post_swagger_schema = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            "type",
            openapi.IN_PATH,
            description="Problem type ('concept' or 'dataset')",
            type=openapi.TYPE_STRING,
            required=True,
        ),
        openapi.Parameter(
            "slug",
            openapi.IN_PATH,
            description="Problem slug",
            type=openapi.TYPE_STRING,
            required=True,
        ),
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "content": openapi.Schema(
                type=openapi.TYPE_STRING, description="Comment content"
            ),
            "parent_comment_id": openapi.Schema(
                type=openapi.TYPE_INTEGER, description="Parent comment ID"
            ),
        },
    ),
    responses={
        201: openapi.Response(description="Comment created successfully"),
        400: openapi.Response(description="Bad Request - Invalid parameters"),
        404: openapi.Response(description="Not Found - Problem not found"),
    },
)

like_comment_post_swagger_schema = swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "comment_id": openapi.Schema(
                type=openapi.TYPE_INTEGER, description="Comment ID"
            ),
            "action": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Action to perform ('like' or 'dislike')",
            ),
        },
    ),
    responses={
        200: openapi.Response(description="Comment liked/disliked successfully"),
        400: openapi.Response(description="Bad Request - Invalid parameters"),
        404: openapi.Response(description="Not Found - Comment not found"),
        401: openapi.Response(description="Unauthorized - User not authenticated"),
    },
)

code_editor_get_swagger_schema = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            "type",
            openapi.IN_PATH,
            description="Problem type ('concept' or 'dataset')",
            type=openapi.TYPE_STRING,
            required=True,
        ),
        openapi.Parameter(
            "slug",
            openapi.IN_PATH,
            description="Problem slug",
            type=openapi.TYPE_STRING,
            required=True,
        ),
    ],
    responses={
        200: openapi.Response(
            description="Code editor retrieved successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "problem_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "code_editor_data": openapi.Schema(type=openapi.TYPE_OBJECT),
                },
            ),
            examples={
                "application/json": {
                    "problem_id": 1,
                    "code_editor_data": {
                        "template_code": "print('Hello, World!')",
                        "validation_testcases": ["test_case_1", "test_case_2"],
                    },
                },
            },
        ),
        400: openapi.Response(description="Bad Request - Invalid parameters"),
        404: openapi.Response(description="Not Found - Problem not found"),
    },
)


# This file contains the swagger schemas for the problems app in the Django project.
