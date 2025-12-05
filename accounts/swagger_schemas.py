from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status

from .serializers import (
    ForgotPasswordSerializer,
    GoogleAuthSerializer,
    LoginRequestSerializer,
    LoginResponseSerializer,
    LogoutSerializer,
    OnboardingSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    UserDetailSerializer,
)

register_schema = swagger_auto_schema(
    request_body=RegisterSerializer,
    responses={
        201: openapi.Response(
            description="User registered successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(type=openapi.TYPE_STRING),
                },
            ),
            examples={"application/json": {"message": "User registered successfully"}},
        ),
        400: openapi.Response(
            description="Bad Request - Validation Errors",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "email": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Items(type=openapi.TYPE_STRING),
                    ),
                    "password": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Items(type=openapi.TYPE_STRING),
                    ),
                },
            ),
            examples={
                "application/json": {
                    "email": ["This field is required."],
                    "password": ["This field is required."],
                }
            },
        ),
    },
)

login_schema = swagger_auto_schema(
    request_body=LoginRequestSerializer,
    responses={
        status.HTTP_200_OK: LoginResponseSerializer,
        status.HTTP_400_BAD_REQUEST: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "message": openapi.Schema(
                    type=openapi.TYPE_STRING, example="Invalid credentials"
                ),
            },
        ),
    },
)

google_auth_schema = swagger_auto_schema(
    request_body=GoogleAuthSerializer,
    responses={
        200: openapi.Response(
            description="User authenticated successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "refresh": openapi.Schema(type=openapi.TYPE_STRING),
                    "access": openapi.Schema(type=openapi.TYPE_STRING),
                    "message": openapi.Schema(type=openapi.TYPE_STRING),
                    "is_new_user": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                },
            ),
            examples={
                "application/json": {
                    "refresh": "refresh_token_here",
                    "access": "access_token_here",
                    "message": "User authenticated successfully.",
                    "is_new_user": True,
                }
            },
        ),
        400: openapi.Response(
            description="Bad Request - Validation Errors",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING, example="Invalid data"
                    ),
                },
            ),
            examples={
                "application/json": {
                    "email": ["This field is required."],
                    "first_name": ["This field is required."],
                }
            },
        ),
    },
)

forgot_password_schema = swagger_auto_schema(
    request_body=ForgotPasswordSerializer,
    responses={
        200: openapi.Response(
            description="Password reset email sent",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
            examples={"application/json": {"message": "Password reset email sent"}},
        ),
        400: openapi.Response(
            description="Email not found",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
            examples={"application/json": {"message": "Email not found"}},
        ),
    },
)

reset_password_schema = swagger_auto_schema(
    request_body=ResetPasswordSerializer,
    responses={
        200: openapi.Response(
            description="Password reset successful",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
            examples={"application/json": {"message": "Password reset successful"}},
        ),
        400: openapi.Response(
            description="Invalid data or token",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
            examples={"application/json": {"message": "Invalid data"}},
        ),
    },
)

logout_schema = swagger_auto_schema(
    request_body=LogoutSerializer,
    responses={
        200: openapi.Response(
            description="Successfully logged out",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
            examples={"application/json": {"message": "Successfully logged out"}},
        ),
        400: openapi.Response(
            description="Refresh token not provided or invalid",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
            examples={"application/json": {"message": "Refresh token not provided"}},
        ),
    },
)

onboarding_schema = swagger_auto_schema(
    request_body=OnboardingSerializer,
    responses={
        200: openapi.Response(
            description="Onboarding completed successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
            examples={
                "application/json": {"message": "Onboarding completed successfully"}
            },
        ),
    },
)

update_user_detail_schema = swagger_auto_schema(
    request_body=UserDetailSerializer,
    responses={
        200: openapi.Response(
            description="User details updated successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
            examples={
                "application/json": {"message": "User details updated successfully"}
            },
        )
    },
)

header_data_swagger_schema = swagger_auto_schema(
    responses={
        200: openapi.Response(
            description="Header data retrieved successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "current_day_concept_read": openapi.Schema(
                        type=openapi.TYPE_BOOLEAN
                    ),
                    "current_day_problem_solved": openapi.Schema(
                        type=openapi.TYPE_BOOLEAN
                    ),
                    "current_streak": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "longest_streak": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "language_selected": openapi.Schema(type=openapi.TYPE_STRING),
                    "is_premium_user": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    "first_name": openapi.Schema(type=openapi.TYPE_STRING),
                    "last_name": openapi.Schema(type=openapi.TYPE_STRING),
                    "profile_photo_url": openapi.Schema(type=openapi.TYPE_STRING),
                    "email": openapi.Schema(type=openapi.TYPE_STRING),
                    "username": openapi.Schema(type=openapi.TYPE_STRING),
                },
            ),
            examples={
                "application/json": {
                    "current_day_concept_read": True,
                    "current_day_problem_solved": False,
                    "current_streak": 5,
                    "longest_streak": 10,
                    "language_selected": "English",
                    "is_premium_user": True,
                    "first_name": "John",
                    "last_name": "Doe",
                    "profile_photo_url": "https://example.com/photo.jpg",
                    "email": "abcd@gmail.com",
                    "username": "john_doe",
                }
            },
        ),
        401: openapi.Response(
            description="Unauthorized - User not authenticated",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING, example="Unauthorized"
                    ),
                },
            ),
            examples={
                "application/json": {
                    "message": "Unauthorized",
                }
            },
        ),
    }
)

user_heatmap_schema = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            name="username",
            in_=openapi.IN_PATH,
            type=openapi.TYPE_STRING,
            required=True,
            description="Username",
        ),
    ],
    responses={
        200: openapi.Response(
            description="User dashboard data retrieved successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "profile_data": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "username": openapi.Schema(type=openapi.TYPE_STRING),
                            "name": openapi.Schema(type=openapi.TYPE_STRING),
                            "profile_photo_url": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_URI
                            ),
                            "current_streak": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "longest_streak": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "organisation_name": openapi.Schema(
                                type=openapi.TYPE_STRING
                            ),
                            "location": openapi.Schema(type=openapi.TYPE_STRING),
                            "occupation": openapi.Schema(type=openapi.TYPE_STRING),
                            "kaggle_profile_url": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_URI
                            ),
                            "github": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_URI
                            ),
                            "twitter": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_URI
                            ),
                            "portfolio": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_URI
                            ),
                            "linkedin": openapi.Schema(
                                type=openapi.TYPE_STRING, format=openapi.FORMAT_URI
                            ),
                        },
                    ),
                    "problem_solved_data": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "total_submissions_count": openapi.Schema(
                                type=openapi.TYPE_INTEGER
                            ),
                            "easy_problems_submissions_count": openapi.Schema(
                                type=openapi.TYPE_INTEGER
                            ),
                            "medium_problems_submissions_count": openapi.Schema(
                                type=openapi.TYPE_INTEGER
                            ),
                            "hard_problems_submissions_count": openapi.Schema(
                                type=openapi.TYPE_INTEGER
                            ),
                        },
                    ),
                },
            ),
            examples={
                "application/json": {
                    "profile_data": {
                        "username": "john_doe",
                        "name": "John Doe",
                        "profile_photo_url": "https://example.com/photo.jpg",
                        "current_streak": 5,
                        "longest_streak": 10,
                        "organisation_name": "Tech Corp",
                        "location": "New York",
                        "occupation": "Data Scientist",
                        "kaggle_profile_url": "https://kaggle.com/johndoe",
                        "github": "https://github.com/johndoe",
                        "twitter": "https://twitter.com/johndoe",
                        "portfolio": "https://johndoe.com",
                        "linkedin": "https://linkedin.com/in/johndoe",
                    },
                    "problem_solved_data": {
                        "total_submissions_count": 50,
                        "easy_problems_submissions_count": 20,
                        "medium_problems_submissions_count": 25,
                        "hard_problems_submissions_count": 5,
                    },
                }
            },
        ),
        404: openapi.Response(
            description="User not found",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"error": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
        ),
    },
)

user_heatmap_data_schema = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            name="username",
            in_=openapi.IN_PATH,
            type=openapi.TYPE_STRING,
            required=True,
            description="Username",
        ),
        openapi.Parameter(
            name="start_date",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=False,
            description="Start date for heatmap data in YYYY-MM-DD format. Defaults to 365 days ago if not provided.",
        ),
        openapi.Parameter(
            name="end_date",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=False,
            description="End date for heatmap data in YYYY-MM-DD format. Defaults to current date if not provided.",
        ),
    ],
    responses={
        200: openapi.Response(
            description="User heatmap data retrieved successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "heatmap_data": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "date": openapi.Schema(type=openapi.TYPE_STRING),
                                "submissions_count": openapi.Schema(
                                    type=openapi.TYPE_INTEGER
                                ),
                                "concepts_read_count": openapi.Schema(
                                    type=openapi.TYPE_INTEGER
                                ),
                            },
                        ),
                    ),
                },
            ),
            examples={
                "application/json": {
                    "heatmap_data": [
                        {
                            "date": "2024-01-01",
                            "submissions_count": 10,
                            "concepts_read_count": 5,
                        },
                        {
                            "date": "2024-01-02",
                            "submissions_count": 3,
                            "concepts_read_count": 2,
                        },
                    ]
                }
            },
        ),
        400: openapi.Response(
            description="Bad Request - Invalid date format or start_date after end_date",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"error": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
            examples={
                "application/json": {
                    "error": "start_date must be before or equal to end_date"
                }
            },
        ),
        404: openapi.Response(
            description="User not found",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"error": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
        ),
    },
)

problems_attempted_schema = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            name="username",
            in_=openapi.IN_PATH,
            type=openapi.TYPE_STRING,
            required=True,
            description="Username",
        ),
        openapi.Parameter(
            name="page",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            required=False,
            description="Page number",
        ),
        openapi.Parameter(
            name="page_size",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            required=False,
            description="Number of items per page",
        ),
    ],
    responses={
        200: openapi.Response(
            description="Problems attempted by user retrieved successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "count": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "next": openapi.Schema(
                        type=openapi.TYPE_STRING, format=openapi.FORMAT_URI
                    ),
                    "previous": openapi.Schema(
                        type=openapi.TYPE_STRING, format=openapi.FORMAT_URI
                    ),
                    "results": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "title": openapi.Schema(type=openapi.TYPE_STRING),
                                "level": openapi.Schema(type=openapi.TYPE_STRING),
                                "tag": openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Schema(type=openapi.TYPE_STRING),
                                ),
                                "problem_type": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                                "slug": openapi.Schema(type=openapi.TYPE_STRING),
                                "last_attempted": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    format=openapi.FORMAT_DATETIME,
                                ),
                            },
                        ),
                    ),
                },
            ),
            examples={
                "application/json": {
                    "count": 50,
                    "next": "http://api/dashboard/john_doe/problems/?page=2",
                    "previous": None,
                    "results": [
                        {
                            "id": 1,
                            "title": "Linear Regression Problem",
                            "level": "easy",
                            "tag": ["machine-learning", "regression"],
                            "problem_type": "dataset",
                            "slug": "linear-regression-problem",
                            "last_attempted": "2024-01-15T10:30:00Z",
                        }
                    ],
                }
            },
        ),
        404: openapi.Response(
            description="User not found",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"error": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
        ),
    },
)

concepts_read_schema = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            name="username",
            in_=openapi.IN_PATH,
            type=openapi.TYPE_STRING,
            required=True,
            description="Username",
        ),
        openapi.Parameter(
            name="page",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            required=False,
            description="Page number",
        ),
        openapi.Parameter(
            name="page_size",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            required=False,
            description="Number of items per page",
        ),
    ],
    responses={
        200: openapi.Response(
            description="Concepts read by user retrieved successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "count": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "next": openapi.Schema(
                        type=openapi.TYPE_STRING, format=openapi.FORMAT_URI
                    ),
                    "previous": openapi.Schema(
                        type=openapi.TYPE_STRING, format=openapi.FORMAT_URI
                    ),
                    "results": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "title": openapi.Schema(type=openapi.TYPE_STRING),
                                "description": openapi.Schema(type=openapi.TYPE_STRING),
                                "slug": openapi.Schema(type=openapi.TYPE_STRING),
                                "last_read": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    format=openapi.FORMAT_DATETIME,
                                ),
                            },
                        ),
                    ),
                },
            ),
            examples={
                "application/json": {
                    "count": 25,
                    "next": "http://api/dashboard/john_doe/concepts/?page=2",
                    "previous": None,
                    "results": [
                        {
                            "id": 1,
                            "title": "Machine Learning Basics",
                            "description": "Introduction to machine learning concepts",
                            "slug": "machine-learning-basics",
                            "last_read": "2024-01-15T09:15:00Z",
                        }
                    ],
                }
            },
        ),
        404: openapi.Response(
            description="User not found",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"error": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
        ),
    },
)

submissions_schema = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            name="username",
            in_=openapi.IN_PATH,
            type=openapi.TYPE_STRING,
            required=True,
            description="Username",
        ),
        openapi.Parameter(
            name="page",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            required=False,
            description="Page number",
        ),
        openapi.Parameter(
            name="page_size",
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            required=False,
            description="Number of items per page",
        ),
    ],
    responses={
        200: openapi.Response(
            description="Submissions by user retrieved successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "count": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "next": openapi.Schema(
                        type=openapi.TYPE_STRING, format=openapi.FORMAT_URI
                    ),
                    "previous": openapi.Schema(
                        type=openapi.TYPE_STRING, format=openapi.FORMAT_URI
                    ),
                    "results": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "verdict": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "verdict_display": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                                "created_timestamp": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    format=openapi.FORMAT_DATETIME,
                                ),
                                "time_taken": openapi.Schema(type=openapi.TYPE_NUMBER),
                                "memory_taken": openapi.Schema(
                                    type=openapi.TYPE_NUMBER
                                ),
                                "problem": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                        "title": openapi.Schema(
                                            type=openapi.TYPE_STRING
                                        ),
                                        "problem_type": openapi.Schema(
                                            type=openapi.TYPE_STRING
                                        ),
                                        "level": openapi.Schema(
                                            type=openapi.TYPE_STRING
                                        ),
                                        "slug": openapi.Schema(
                                            type=openapi.TYPE_STRING
                                        ),
                                    },
                                ),
                            },
                        ),
                    ),
                },
            ),
            examples={
                "application/json": {
                    "count": 100,
                    "next": "http://api/dashboard/john_doe/submissions/?page=2",
                    "previous": None,
                    "results": [
                        {
                            "id": 1,
                            "verdict": 3,
                            "verdict_display": "Accepted",
                            "created_timestamp": "2024-01-15T10:30:00Z",
                            "time_taken": 1.25,
                            "memory_taken": 256.5,
                            "problem": {
                                "id": 1,
                                "title": "Linear Regression Problem",
                                "problem_type": "dataset",
                                "level": "easy",
                                "slug": "linear-regression-problem",
                            },
                        }
                    ],
                }
            },
        ),
        404: openapi.Response(
            description="User not found",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"error": openapi.Schema(type=openapi.TYPE_STRING)},
            ),
        ),
    },
)
