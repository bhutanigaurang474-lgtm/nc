import base64
from calendar import monthrange
from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ViewSet

from concepts.models import ConceptsRead
from problems.filters import ProblemFilterBackend
from problems.models import (
    Comment,
    ConceptBasedProblem,
    DailyContent,
    DatasetBasedProblem,
    Note,
    Submission,
)
from problems.paginator import ProblemListPagination
from problems.serializers import (
    CommentReactionSerializer,
    CommentSerializer,
    NotesSerializer,
    ProblemListSerializer,
    RunCodeSerializer,
)
from problems.swagger_schemas import (
    code_editor_get_swagger_schema,
    comment_get_swagger_schema,
    comment_post_swagger_schema,
    like_comment_post_swagger_schema,
    monthly_content_view_swagger_schema,
    notes_get_swagger_schema,
    notes_post_swagger_schema,
    problem_view_swagger_schema,
    problems_table_view_swagger_schema,
    run_code_post_swagger_schema,
    submission_get_swagger_schema,
    user_history_view_swagger_schema,
)
from problems.utils import (
    execute_code,
    get_content_progress_data,
    get_difficulty_counts,
    get_notes,
    get_problem_by_type_and_slug,
    get_solved_problems_count,
    get_submission_status,
    get_submissions_count,
    map_verdict_id,
)


class PublicProblemsViewSet(GenericViewSet):
    """ViewSet for public problem endpoints that don't require authentication"""

    permission_classes = [AllowAny]
    serializer_class = ProblemListSerializer
    filter_backends = (ProblemFilterBackend,)
    pagination_class = ProblemListPagination

    def get_queryset(self):
        """Get the appropriate queryset based on problem_type"""
        problem_type = self.request.query_params.get("problem_type")

        if problem_type == "concept":
            return ConceptBasedProblem.objects.all()
        elif problem_type == "dataset":
            return DatasetBasedProblem.objects.all()
        else:
            return None

    @problems_table_view_swagger_schema
    def list(self, request):
        """List problems with filtering, searching, and pagination"""
        queryset = self.get_queryset()
        filtered_problems = self.filter_queryset(queryset)

        difficulty_counts = get_difficulty_counts(filtered_problems)

        problems_solved = 0
        if request.user.is_authenticated:
            problems_solved = get_solved_problems_count(request.user, filtered_problems)

        page = self.paginate_queryset(filtered_problems)

        if page is None:
            serializer = self.serializer_class(
                filtered_problems, many=True, context={"user": request.user}
            )
            return Response(serializer.data)

        serializer = self.serializer_class(
            page, many=True, context={"user": request.user}
        )
        return self.paginator.get_paginated_response(
            serializer.data,
            difficulty_counts=difficulty_counts,
            total_problems_solved=problems_solved,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="monthly-content",
        url_name="monthly-content",
    )
    @monthly_content_view_swagger_schema
    def monthly_content(self, request):
        year = max(int(request.query_params.get("year", datetime.now().year)), 2025)
        month = min(int(request.query_params.get("month", datetime.now().month)), 12)
        user = request.user
        response_data = {
            "monthly_content": {},
            "percentage_solved": 0,
        }

        contents = DailyContent.objects.filter(
            date__year=year, date__month=month, date__lte=datetime.now()
        )
        if not contents.exists():
            return Response(response_data)

        _, last_day = monthrange(year, month)
        progress_count = 0

        for content in contents:
            problem_solved, concept_read, problem_submission_status = (
                get_content_progress_data(user, content)
            )

            if problem_solved and concept_read:
                progress_count += 1

            # Build content item inline
            concept = content.concept
            problem = content.content_object

            problem_type = (
                "concept" if isinstance(problem, ConceptBasedProblem) else "dataset"
            )

            response_data["monthly_content"][str(content.date)] = {
                "problem_data": {
                    "id": problem.id,
                    "slug": problem.slug,
                    "title": problem.title,
                    "level": problem.level,
                    "type": problem.problem_type,  # DL,ML
                    "problem_type": problem_type,  # concept, dataset
                    "tags": problem.get_tags_list(),
                    "solved": int(problem_solved),
                    "status": problem_submission_status,
                },
                "concept_data": {
                    "id": concept.id,
                    "slug": concept.slug,
                    "title": concept.title,
                    "level": concept.level,
                    "type": concept.concept_type,
                    "tags": concept.get_tags_list(),
                    "read": int(concept_read),
                },
            }
        response_data["percentage_solved"] = (progress_count / last_day) * 100

        return Response(response_data)

    @action(
        detail=False,
        methods=["get"],
        url_path=r"(?P<type>[^/.]+)/(?P<slug>[^/.]+)",
        url_name="problem-detail",
    )
    @problem_view_swagger_schema
    def problem_detail(self, request, type, slug):
        problem = get_problem_by_type_and_slug(type, slug)
        if not problem:
            return Response(
                {"message": "Problem not found"}, status=status.HTTP_404_NOT_FOUND
            )

        submission_status = None
        notes_id = None
        if request.user.is_authenticated:
            submission_status = get_submission_status(request.user, problem)
            notes_id = get_notes(request.user, problem)

        # Prepare the response data
        problem_data = {
            "id": problem.id,
            "title": problem.title,
            "description": problem.description,
            "level": problem.level,
            "acceptance_rate": problem.acceptance_rate,
            "submission_status": submission_status,
            "type": problem.problem_type,
            "tags": problem.get_tags_list(),
            "notes_id": notes_id,
        }
        if isinstance(problem, ConceptBasedProblem):
            total_submissions = problem.total_submissions
            accepted_submissions = problem.accepted_submissions
        elif isinstance(problem, DatasetBasedProblem):
            total_submissions, accepted_submissions = get_submissions_count(
                "dataset", problem
            )

        problem_data["total_submissions"] = total_submissions
        problem_data["accepted_submissions"] = accepted_submissions

        return Response(problem_data, status=status.HTTP_200_OK)


class AuthenticatedProblemsViewSet(ViewSet):
    """ViewSet for authenticated problem endpoints that require authentication"""

    permission_classes = [IsAuthenticated]

    @action(
        detail=False,
        methods=["get"],
        url_path=r"(?P<type>[^/.]+)/(?P<slug>[^/.]+)/code-editor",
        url_name="code-editor",
    )
    @code_editor_get_swagger_schema
    def code_editor(self, request, type, slug):
        problem = get_problem_by_type_and_slug(type, slug)
        if not problem:
            return Response(
                {"message": "Problem not found"}, status=status.HTTP_404_NOT_FOUND
            )

        code_editor_data = {}

        if isinstance(problem, ConceptBasedProblem):
            code_editor_data["template_code"] = problem.code_editor_template
            code_editor_data["validation_testcases"] = (
                problem.validation_testcases or []
            )
        elif isinstance(problem, DatasetBasedProblem):
            code_editor_data["evaluation_metrics_dict"] = (
                problem.evaluation_metrics_dict
            )
            code_editor_data["test_data_file_path"] = problem.test_data_file_path
            code_editor_data["data_available_to_user_file_path"] = (
                problem.data_available_to_user_file_path
            )
            code_editor_data["ideal_metrics_json_file_path"] = (
                problem.ideal_metrics_json_file_path
            )

        return Response(
            {
                "problem_id": problem.id,
                "code_editor_data": code_editor_data,
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path=r"(?P<type>[^/.]+)/(?P<slug>[^/.]+)/editorial",
        url_name="editorial",
    )
    def editorial(self, request, type, slug):
        problem = get_problem_by_type_and_slug(type, slug)
        if not problem:
            return Response(
                {"message": "Provided problem type and slug do not match any problem"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"editorial": problem.editorial_description}, status=status.HTTP_200_OK
        )

    @action(
        detail=False, methods=["get"], url_path="user-history", url_name="user-history"
    )
    @user_history_view_swagger_schema
    def user_history(self, request):
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

        submissions = Submission.objects.filter(
            user=request.user, created_timestamp__date=date
        ).order_by("-created_timestamp")

        # Dictionary to store the latest submission for each (problem, status) pair
        latest_submissions = {}

        for submission in submissions:
            problem = submission.content_object
            key = (problem, submission.verdict)

            if key not in latest_submissions:
                latest_submissions[key] = submission

        # Convert dictionary to sorted list of dicts
        problems_submitted = [
            {
                "problem_id": problem.id,
                "submission_id": submission.id,
                "problem_title": problem.title,
                "submission_status": status,
            }
            for (problem, status), submission in sorted(
                latest_submissions.items(),
                key=lambda x: x[1].created_timestamp,
                reverse=True,
            )
        ]

        # Get concepts read on the given date
        concepts = ConceptsRead.objects.filter(
            user=request.user,
            read_timestamp__date=date,
        )

        concepts_read = [
            {
                "concept_id": concept_read.concept.id,
                "concept_title": concept_read.concept.title,
            }
            for concept_read in concepts
        ]

        return Response(
            {"problems_submitted": problems_submitted, "concepts_read": concepts_read},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="notes", url_name="notes")
    @notes_post_swagger_schema
    def notes_post(self, request):
        serializer = NotesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        notes_content = validated_data["notes"]
        problem = validated_data["problem"]

        # Check if the user already has notes for this problem
        notes, _ = Note.objects.get_or_create(
            user=request.user,
            content_type=ContentType.objects.get_for_model(problem),
            object_id=problem.id,
        )
        notes.note = notes_content
        notes.save()

        return Response({"message": "Notes saved successfully"})

    @action(detail=False, methods=["get"], url_path="notes", url_name="notes")
    @notes_get_swagger_schema
    def notes_get(self, request):
        problem_slug = request.query_params.get("problem_slug")
        problem_type = request.query_params.get("problem_type")

        if not problem_slug:
            return Response(
                {"message": "Problem slug is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        problem = get_problem_by_type_and_slug(problem_type, problem_slug)
        if not problem:
            return Response(
                {"message": "Problem not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Fetch notes for the user and the specified problem
        notes, _ = Note.objects.get_or_create(
            user=request.user,
            content_type=ContentType.objects.get_for_model(problem),
            object_id=problem.id,
        )

        return Response(
            {"notes": notes.note},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="run-code", url_name="run-code")
    @run_code_post_swagger_schema
    def run_code(self, request):
        serializer = RunCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        code = validated_data["code"]
        problem = validated_data["problem"]
        testcases = validated_data.get("testcases", [])
        run_only = validated_data["run_only"]

        if run_only:
            testcases = testcases or problem.validation_testcases
            ordered_testcases = []
            for testcase_input in testcases:
                ideal_result = execute_code(
                    code=problem.ideal_solution_code, input_data=testcase_input
                )
                expected_output = base64.b64decode(
                    ideal_result.get("stdout", "")
                ).decode()
                user_result = execute_code(
                    code=code,
                    input_data=testcase_input,
                    expected_output=expected_output,
                )
                if user_result.get("status") == "error":
                    return Response(
                        user_result, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

                ordered_testcases.append(
                    {
                        "input": testcase_input,
                        "actual_output": base64.b64decode(
                            user_result.get("stdout", "")
                        ).decode(),
                        "expected_output": expected_output,
                        "verdict": user_result.get("status", {}).get(
                            "description", "Unknown Error"
                        ),
                    }
                )

            return Response(
                {"ordered_testcases": ordered_testcases}, status=status.HTTP_200_OK
            )

        # Else, run code for official submission testcases
        submission_testcases = problem.submission_testcases
        verdict_id = 3
        stdout = ""
        stderr = ""
        time_taken = 0.0
        memory_taken = 0.0
        testcase_passed = 0
        failed_testcase_info = {}

        for tc in submission_testcases:
            testcase_input = tc.get("input", "")
            expected_output = tc.get("output", "")
            user_result = execute_code(
                code=code, input_data=testcase_input, expected_output=expected_output
            )
            if user_result.get("status") == "error":
                return Response(
                    user_result, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            status_info = user_result.get("status", {})
            status_id = status_info.get("id", 0)

            stdout = base64.b64decode(user_result.get("stdout", "")).decode()
            stderr = base64.b64decode(user_result.get("stderr", "")).decode()
            time_taken = max(float(time_taken), float(user_result.get("time", 0)) or 0)
            memory_taken = max(
                float(memory_taken), float(user_result.get("memory", 0)) or 0
            )
            testcase_passed += 1

            if status_id > 3:
                verdict_id = map_verdict_id(status_id)
                failed_testcase_info = {
                    "testcase_index": testcase_passed,
                    "input": testcase_input,
                    "output": stdout,
                    "expected_output": expected_output,
                    "error": stderr,
                }
                break

        # Save the submission
        Submission.objects.create(
            user=request.user,
            content_type=ContentType.objects.get_for_model(problem),
            object_id=problem.id,
            code=code,
            verdict=verdict_id,
            time_taken=time_taken,
            memory_taken=memory_taken,
            failed_testcase_info=failed_testcase_info,
        )

        data = {
            "verdict": verdict_id,
            "passed_count": testcase_passed,
            "total_count": len(submission_testcases),
            "stdout": stdout,
            "stderr": stderr,
            "time_taken": time_taken,
            "memory_taken": memory_taken,
            "problem_accepted": problem.accepted_submissions,
            "problem_total_submissions": problem.total_submissions,
            "problem_acceptance_rate": problem.acceptance_rate,
            "failed_testcase_info": failed_testcase_info,
        }

        return Response(data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["get"],
        url_path=r"(?P<type>[^/.]+)/(?P<slug>[^/.]+)/submissions",
        url_name="submissions",
    )
    @submission_get_swagger_schema
    def submissions(self, request, type, slug):
        # Get the problem first
        problem = get_problem_by_type_and_slug(type, slug)
        if not problem:
            return Response(
                {"message": "Problem not found"}, status=status.HTTP_404_NOT_FOUND
            )

        submissions = Submission.objects.filter(
            content_type=ContentType.objects.get_for_model(problem),
            object_id=problem.id,
            user=request.user,
        )
        submissions_data = []
        for submission in submissions:
            submissions_data.append(
                {
                    "verdict": submission.verdict,
                    "time_taken": submission.time_taken,
                    "memory_taken": submission.memory_taken,
                    "created_timestamp": submission.created_timestamp,
                    "code_submitted": submission.code,
                    "failed_testcase_info": submission.failed_testcase_info,
                }
            )

        return Response(submissions_data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["get"],
        url_path=r"(?P<type>[^/.]+)/(?P<slug>[^/.]+)/comments",
        url_name="comments",
    )
    @comment_get_swagger_schema
    def comments_get(self, request, type, slug):
        problem = get_problem_by_type_and_slug(type, slug)
        if not problem:
            return Response({"message": "Problem not found"}, status=404)

        comments = Comment.objects.filter(
            content_type=ContentType.objects.get_for_model(problem),
            object_id=problem.id,
            parent_comment=None,
        )

        comments_data = []
        for comment in comments:
            replies = comment.get_replies()
            comments_data.append(
                {
                    "id": comment.id,
                    "content": comment.content,
                    "created_at": comment.created_at,
                    "action_performed": "liked"
                    if request.user in comment.like_by_users.all()
                    else "disliked"
                    if request.user in comment.dislike_by_users.all()
                    else None,
                    "like_count": comment.like_by_users.count(),
                    "dislike_count": comment.dislike_by_users.count(),
                    "replies": [
                        {
                            "id": reply.id,
                            "content": reply.content,
                            "created_at": reply.created_at,
                            "like_count": reply.like_by_users.count(),
                            "dislike_count": reply.dislike_by_users.count(),
                            "action_performed": "liked"
                            if request.user in reply.like_by_users.all()
                            else "disliked"
                            if request.user in reply.dislike_by_users.all()
                            else None,
                        }
                        for reply in replies
                    ],
                }
            )

        return Response(comments_data, status=200)

    @action(
        detail=False,
        methods=["post"],
        url_path=r"(?P<type>[^/.]+)/(?P<slug>[^/.]+)/comments",
        url_name="comments",
    )
    @comment_post_swagger_schema
    def comments_post(self, request, type, slug):
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        content = validated_data["content"]
        parent_comment = validated_data["parent_comment"]

        problem = get_problem_by_type_and_slug(type, slug)
        if not problem:
            return Response({"message": "Problem not found"}, status=404)

        Comment.objects.create(
            user=request.user,
            content=content,
            content_type=ContentType.objects.get_for_model(problem),
            object_id=problem.id,
            parent_comment=parent_comment,
        )

        return Response({"message": "Comment created successfully"}, status=201)

    @action(
        detail=False,
        methods=["post"],
        url_path="comments/react",
        url_name="react-comment",
    )
    @like_comment_post_swagger_schema
    def react_comment(self, request):
        serializer = CommentReactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        comment = validated_data["comment"]
        action = validated_data["action"]

        if action == "like":
            comment.like_by_users.add(request.user)
            comment.dislike_by_users.remove(request.user)
        else:
            comment.dislike_by_users.add(request.user)
            comment.like_by_users.remove(request.user)

        return Response({"message": f"Comment {action}d successfully"}, status=200)
