from django.urls import path
from courses.views import (
    CoursesView,
    LikeDislikeCourseView,
    CourseDetailView,
    FollowCourseView,
)

urlpatterns = [
    path("", CoursesView.as_view(), name="courses"),
    path("<slug:slug>/", CourseDetailView.as_view(), name="course-detail"),
    path("<int:course_id>/like/", LikeDislikeCourseView.as_view(), name="course-like"),
    path("<int:course_id>/follow/", FollowCourseView.as_view(), name="course-follow"),
]
