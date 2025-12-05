from calendar import c
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from courses.models import Course
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from courses.swagger_schemas import (
    get_all_courses_docs,
    like_dislike_course_docs,
    single_course_details_docs,
    follow_course_docs,
)


# Create your views here.
class CoursesView(GenericAPIView):
    permission_classes = [AllowAny]  # Allow both authenticated and guest users
    serializer_class = None  #

    @get_all_courses_docs
    def get(self, request):
        """
        Get a list of all courses.
        """
        courses = Course.objects.all()
        courses_data = [
            {
                "id": course.id,
                "slug": course.slug,
                "title": course.title,
                "description": course.description,
                "followers_count": course.followers.count(),
                "likes_count": course.likes.count(),
            }
            for course in courses
        ]
        return Response(courses_data, status=status.HTTP_200_OK)


class LikeDislikeCourseView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = None

    @like_dislike_course_docs
    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"message": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        # Check if the user is already in the likes list

        if user in course.likes.all():
            course.likes.remove(user)
            message = "Course unliked successfully."
        else:
            course.likes.add(user)
            message = "Course liked successfully."

        return Response(
            {"message": message, "likes_count": course.likes.count()},
            status=status.HTTP_200_OK,
        )


class CourseDetailView(GenericAPIView):
    permission_classes = [AllowAny]  # Allow both authenticated and guest users
    serializer_class = None

    @single_course_details_docs
    def get(self, request, slug):
        """
        Get details of a specific course.
        """
        try:
            course = Course.objects.get(slug=slug)
        except Course.DoesNotExist:
            return Response(
                {"message": "Course not found."}, status=status.HTTP_404_NOT_FOUND
            )

        course_data = {
            "id": course.id,
            "slug": course.slug,
            "title": course.title,
            "description": course.description,
            "followers_count": course.followers.count(),
            "likes_count": course.likes.count(),
        }

        return Response(course_data, status=status.HTTP_200_OK)


class FollowCourseView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = None  #

    @follow_course_docs
    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        user = request.user

        if user not in course.followers.all():
            course.followers.add(user)

        return Response(
            status=status.HTTP_200_OK,
        )
