from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

get_all_courses_docs = swagger_auto_schema(
    responses={
        200: openapi.Response(
            description="List of courses",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "courses": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Items(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "title": openapi.Schema(type=openapi.TYPE_STRING),
                                "description": openapi.Schema(type=openapi.TYPE_STRING),
                                "followers_count": openapi.Schema(
                                    type=openapi.TYPE_INTEGER
                                ),
                                "likes_count": openapi.Schema(
                                    type=openapi.TYPE_INTEGER
                                ),
                            },
                        ),
                    )
                },
            ),
            examples={
                "application/json": {
                    "courses": [
                        {
                            "id": 1,
                            "title": "Course 1",
                            "description": "Description of Course 1",
                            "followers_count": 100,
                            "likes_count": 50,
                        },
                        {
                            "id": 2,
                            "title": "Course 2",
                            "description": "Description of Course 2",
                            "followers_count": 200,
                            "likes_count": 80,
                        },
                    ]
                }
            },
        ),
    }
)

like_dislike_course_docs = swagger_auto_schema(
    operation_description="Like or unlike a course.",
    responses={
        200: openapi.Response(
            description="Course liked or unliked successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(type=openapi.TYPE_STRING),
                    "likes_count": openapi.Schema(type=openapi.TYPE_INTEGER),
                },
            ),
            examples={
                "application/json": {
                    "message": "Course liked successfully.",
                    "likes_count": 51,
                }
            },
        ),
        404: openapi.Response(description="Course not found"),
        401: openapi.Response(
            description="Authentication credentials were not provided.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(type=openapi.TYPE_STRING),
                },
            ),
            examples={
                "application/json": {
                    "message": "Authentication credentials were not provided."
                }
            },
        ),
    },
)

single_course_details_docs = swagger_auto_schema(
    responses={
        200: openapi.Response(
            description="Course details",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "title": openapi.Schema(type=openapi.TYPE_STRING),
                    "description": openapi.Schema(type=openapi.TYPE_STRING),
                    "followers_count": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "likes_count": openapi.Schema(type=openapi.TYPE_INTEGER),
                },
            ),
            examples={
                "application/json": {
                    "id": 1,
                    "title": "Course 1",
                    "description": "Description of Course 1",
                    "followers_count": 100,
                    "likes_count": 50,
                }
            },
        ),
    }
)

follow_course_docs = swagger_auto_schema(
    operation_description="Follow or unfollow a course.",
    responses={
        200: openapi.Response(
            description="Course followed or unfollowed successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(type=openapi.TYPE_STRING),
                    "followers_count": openapi.Schema(type=openapi.TYPE_INTEGER),
                },
            ),
            examples={
                "application/json": {
                    "message": "Course followed successfully.",
                    "followers_count": 101,
                }
            },
        ),
        404: openapi.Response(description="Course not found"),
    },
)
