import base64

import requests
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from problems.models import (
    ConceptBasedProblem,
    DatasetBasedProblem,
    Note,
    Submission,
    UserDailyProgress,
)


def get_filtered_problems(problem_type):
    return (
        ConceptBasedProblem.objects.all()
        if problem_type == "concept"
        else DatasetBasedProblem.objects.all()
    )


def get_solved_problems_count(user, problems):
    """Get count of solved problems for a user"""
    if not problems:
        return 0

    # Group problems by their content type
    problems_by_content_type = {}

    for problem in problems:
        content_type = ContentType.objects.get_for_model(problem)
        if content_type not in problems_by_content_type:
            problems_by_content_type[content_type] = []
        problems_by_content_type[content_type].append(problem.id)

    total_solved = 0

    # Count solved problems for each content type
    for content_type, problem_ids in problems_by_content_type.items():
        solved_count = (
            Submission.objects.filter(
                user=user,
                verdict=3,
                content_type=content_type,
                object_id__in=problem_ids,
            )
            .values("object_id")
            .distinct()
            .count()
        )
        total_solved += solved_count

    return total_solved


def get_difficulty_counts(problems):
    """Get count of problems by difficulty level"""
    difficulty_counts = {"easy": 0, "medium": 0, "hard": 0}

    for problem in problems:
        problem_level = problem.level.lower()
        difficulty_counts[problem_level] += 1

    return difficulty_counts


def get_content_progress_data(user, content):
    """Get progress data for a daily content item"""
    if not user.is_authenticated:
        return 0, 0, 0

    problem = content.content_object
    submission_status = get_submission_status(user, problem)

    progress = UserDailyProgress.objects.filter(daily_content=content, user=user).last()

    if progress:
        problem_solved = progress.solved
        concept_read = progress.concept_read
        return problem_solved, concept_read, submission_status

    return 0, 0, submission_status


def get_problem_by_type_and_slug(problem_type, slug):
    """Get a problem by type and slug, handling both concept and dataset problems"""
    try:
        if problem_type == "concept":
            return ConceptBasedProblem.objects.get(slug=slug)
        else:
            problem = DatasetBasedProblem.objects.get(slug=slug)
            return problem
    except (ConceptBasedProblem.DoesNotExist, DatasetBasedProblem.DoesNotExist):
        return None


def map_verdict_id(status_id):
    """Map Judge0 status IDs to internal verdict IDs."""
    if 7 <= status_id <= 14:
        return 7  # Compilation or runtime error
    if status_id == 15:
        return 8  # Internal error
    return status_id  # Otherwise return as-is


def get_submissions_count(problem_type, problem):
    filter_args = {}
    if problem_type == "concept":
        filter_args["concept_problem"] = problem
    else:
        filter_args["dataset_problem"] = problem

    return problem.total_submissions, problem.accepted_submissions


def get_submission_status(user, problem):
    submission_status = 0

    submission = Submission.objects.filter(
        user=user,
        verdict=3,
        content_type=ContentType.objects.get_for_model(problem),
        object_id=problem.id,
    ).last()
    if submission:
        submission_status = submission.verdict

    return submission_status


def get_notes(user, problem):
    notes_id = None
    note = Note.objects.filter(
        user=user,
        content_type=ContentType.objects.get_for_model(problem),
        object_id=problem.id,
    ).last()
    if note:
        notes_id = note.id
    return notes_id


def execute_code(code, input_data, language_id=71, expected_output=None):
    """
    Submit code to Judge0 (RapidAPI).
    language_id: defaults to 71 (Python 3), override if needed
    """
    url = settings.RUN_CODE_API_URL
    headers = {
        "Content-Type": "application/json",
        "x-rapidapi-host": "judge0-ce.p.rapidapi.com",
        "x-rapidapi-key": settings.RAPIDAPI_KEY,  # keep your key in Django settings
    }

    payload = {
        "language_id": language_id,
        "source_code": base64.b64encode(code.encode()).decode(),
        "stdin": base64.b64encode(input_data.encode()).decode(),
        "expected_output": (
            base64.b64encode(expected_output.encode()).decode()
            if expected_output
            else None
        ),
    }

    params = {"base64_encoded": "true", "wait": "true", "fields": "*"}

    try:
        response = requests.post(
            url, headers=headers, params=params, json=payload, timeout=15
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"Error while communicating with Judge0 API: {str(e)}",
        }
    except ValueError:
        return {"status": "error", "message": "Invalid JSON received from Judge0 API."}
