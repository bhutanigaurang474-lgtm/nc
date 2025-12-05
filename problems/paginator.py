from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class ProblemListPagination(PageNumberPagination):
    """Custom pagination class for problem lists"""

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(
        self, data, difficulty_counts=None, total_problems_solved=None
    ):
        """Return paginated response with additional metadata"""
        return Response(
            {
                "problems": data,
                "difficulty_counts": difficulty_counts or {},
                "total_pages": self.page.paginator.num_pages,
                "current_page": self.page.number,
                "total_problems": self.page.paginator.count,
                "total_problems_solved": total_problems_solved or 0,
            }
        )
