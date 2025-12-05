import os
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.db.models import Count, Max
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.middlewares import MaxRefreshTokenMiddleware
from accounts.models import Profile
from accounts.serializers import (
    ForgotPasswordSerializer,
    GoogleAuthSerializer,
    LogoutSerializer,
    OnboardingSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    UserDetailSerializer,
)
from accounts.swagger_schemas import (
    concepts_read_schema,
    forgot_password_schema,
    google_auth_schema,
    header_data_swagger_schema,
    login_schema,
    logout_schema,
    onboarding_schema,
    problems_attempted_schema,
    register_schema,
    reset_password_schema,
    submissions_schema,
    update_user_detail_schema,
    user_heatmap_data_schema,
    user_heatmap_schema,
)
from accounts.utils import download_and_save_profile_photo, verify_recaptcha_token
from concepts.models import Concept, ConceptsRead
from problems.models import ConceptBasedProblem, DatasetBasedProblem, Submission

RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY")


class PublicAuthViewSet(ViewSet):
    """
    ViewSet for public authentication endpoints that don't require authentication
    """

    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"], url_path="register", url_name="register")
    @register_schema
    def register(self, request):
        """POST /register/"""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        phone_number = validated_data.pop("phone_number", None)
        username = validated_data.pop("username", None)

        if not username:
            base_username = validated_data["email"].split("@")[0]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

        user = User.objects.create_user(
            username=username,
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )

        Profile.objects.create(user=user, phone_number=phone_number)

        return Response(
            {"message": "User registered successfully"},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="login", url_name="login")
    @login_schema
    def login(self, request):
        """POST /login/"""
        captcha_token = request.data.get("captchaToken")
        secret_key = RECAPTCHA_SECRET_KEY

        if not verify_recaptcha_token(captcha_token, secret_key):
            return Response(
                {"message": "Invalid CAPTCHA"}, status=status.HTTP_400_BAD_REQUEST
            )

        email = request.data.get("email")
        password = request.data.get("password")

        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist")

        user = authenticate(username=username, password=password)
        if not user:
            return Response(
                {"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
            )

        MaxRefreshTokenMiddleware.check_and_manage_sessions(user)
        refresh = RefreshToken.for_user(user)
        request.session["user_id"] = user.id
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        )

    @action(
        detail=False, methods=["post"], url_path="google-auth", url_name="google-auth"
    )
    @google_auth_schema
    def google_auth(self, request):
        """POST /google-auth/"""
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        first_name = serializer.validated_data["first_name"]
        last_name = serializer.validated_data["last_name"]
        profile_photo_url = serializer.validated_data["profile_photo_url"]

        user, user_created = User.objects.get_or_create(
            email=email,
            defaults={
                "first_name": first_name,
                "last_name": last_name,
                "username": email.split("@")[0],
            },
        )
        profile = Profile.objects.create(user=user) if user_created else user.profile

        if profile_photo_url and (user_created or not profile.profile_photo):
            download_and_save_profile_photo(profile, profile_photo_url, user.id)

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "message": "User authenticated successfully.",
                "is_new_user": user_created,
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="forgot-password",
        url_name="forgot-password",
    )
    @forgot_password_schema
    def forgot_password(self, request):
        """POST /forgot-password/"""
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.get(email=email)

        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        reset_link = settings.RESET_PASSWORD_URL.format(token=token)
        send_mail(
            "Password Reset",
            f"Click the link to reset your password: {reset_link}",
            settings.SUPPORT_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return Response({"message": "Password reset email sent"})

    @action(
        detail=False,
        methods=["post"],
        url_path="reset-password",
        url_name="reset-password",
    )
    @reset_password_schema
    def reset_password(self, request):
        """POST /reset-password/"""
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        new_password = serializer.validated_data["new_password"]

        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()

        return Response({"message": "Password reset successful"})


class DashboardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class DashboardViewSet(ViewSet):
    permission_classes = [AllowAny]
    pagination_class = DashboardPagination

    def get_user(self, username):
        """Helper method to get user with error handling"""
        try:
            return User.objects.select_related("profile").get(username=username)
        except User.DoesNotExist:
            return None

    @action(detail=False, methods=["get"], url_path="(?P<username>[^/.]+)")
    @user_heatmap_schema
    def dashboard(self, request, username=None):
        """GET /dashboard/<username>/"""
        user = self.get_user(username)
        if not user:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Get profile data
        profile_data = self._get_profile_data(user, request)

        # Get problem solved statistics
        problem_solved_data = self._get_problem_solved_data(user)

        return Response(
            {
                "profile_data": profile_data,
                "problem_solved_data": problem_solved_data,
            }
        )

    def _parse_date_param(self, date_str, default):
        """Parse date parameter with error handling"""
        if not date_str:
            return default
        try:
            naive_date = datetime.strptime(date_str, "%Y-%m-%d")
            # Make the date timezone-aware by combining with current timezone
            # Set time to start of day (00:00:00)
            return timezone.make_aware(naive_date, timezone.get_current_timezone())
        except ValueError:
            return default

    def _generate_heatmap_data(self, user, start_date, end_date):
        """Generate heatmap data for the user using efficient database aggregation"""
        # Normalize dates to start of day for consistent filtering
        if hasattr(start_date, "replace"):
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        if hasattr(end_date, "replace"):
            end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)

        # For database query, use end of day for end_date to include the entire day
        end_date_for_query = (
            end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            if hasattr(end_date, "replace")
            else end_date
        )

        # Use database aggregation to get counts grouped by date in a single query
        # This is much more efficient than querying each day individually
        # Instead of 2 queries per day (360+ queries for 6 months), we now have just 2 queries total
        submissions_by_date = (
            Submission.objects.filter(
                user=user,
                verdict=3,
                created_timestamp__gte=start_date,
                created_timestamp__lte=end_date_for_query,
            )
            .annotate(date=TruncDate("created_timestamp"))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )

        concepts_read_by_date = (
            ConceptsRead.objects.filter(
                user=user,
                read_timestamp__gte=start_date,
                read_timestamp__lte=end_date_for_query,
            )
            .annotate(date=TruncDate("read_timestamp"))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )

        # Convert to dictionaries for fast lookup
        submissions_dict = {item["date"]: item["count"] for item in submissions_by_date}
        concepts_dict = {item["date"]: item["count"] for item in concepts_read_by_date}

        # Generate heatmap data for all dates in range
        heatmap_data = []
        current_date = start_date

        while current_date <= end_date:
            # Convert date to date object for dictionary lookup (TruncDate returns date objects)
            date_key = (
                current_date.date() if hasattr(current_date, "date") else current_date
            )

            heatmap_data.append(
                {
                    "date": current_date.strftime("%Y-%m-%d"),
                    "submissions_count": submissions_dict.get(date_key, 0),
                    "concepts_read_count": concepts_dict.get(date_key, 0),
                }
            )

            current_date = current_date + timedelta(days=1)

        return heatmap_data

    @action(
        detail=False,
        methods=["get"],
        url_path="(?P<username>[^/.]+)/heatmap",
        url_name="user-heatmap",
    )
    @user_heatmap_data_schema
    def heatmap(self, request, username=None):
        user = self.get_user(username)
        if not user:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Get default dates normalized to start of day
        default_start = (timezone.now() - timedelta(days=365)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        default_end = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

        start_date = self._parse_date_param(
            request.query_params.get("start_date"), default_start
        )
        end_date = self._parse_date_param(
            request.query_params.get("end_date"), default_end
        )

        if start_date > end_date:
            return Response(
                {"error": "start_date must be before or equal to end_date"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        heatmap_data = self._generate_heatmap_data(user, start_date, end_date)
        return Response(heatmap_data)

    def _get_profile_data(self, user, request):
        """Get user profile data"""
        profile = user.profile
        return {
            "username": user.username,
            "name": user.get_full_name(),
            "profile_photo_url": request.build_absolute_uri(profile.profile_photo.url)
            if profile.profile_photo
            else None,
            "current_streak": profile.current_streak,
            "longest_streak": profile.longest_streak,
            "organisation_name": profile.organisation_name,
            "location": profile.address,
            "occupation": profile.occupation,
            "kaggle_profile_url": profile.kaggle_profile_url,
            "github": profile.github,
            "twitter": profile.twitter,
            "portfolio": profile.portfolio,
            "linkedin": profile.linkedin,
        }

    def _get_total_problems_by_difficulty(self):
        """Get total count of problems by difficulty level"""
        dataset_counts = (
            DatasetBasedProblem.objects.values("level")
            .annotate(count=Count("id"))
            .values("level", "count")
        )

        concept_counts = (
            ConceptBasedProblem.objects.values("level")
            .annotate(count=Count("id"))
            .values("level", "count")
        )

        difficulty_totals = {"easy": 0, "medium": 0, "hard": 0}

        for item in dataset_counts:
            level = item["level"]
            if level in difficulty_totals:
                difficulty_totals[level] += item["count"]

        for item in concept_counts:
            level = item["level"]
            if level in difficulty_totals:
                difficulty_totals[level] += item["count"]

        return difficulty_totals

    def _get_problem_solved_data(self, user):
        """Get problem solved statistics"""
        submissions = Submission.objects.filter(user=user, verdict=3).select_related(
            "content_type"
        )

        difficulty_counts = {"easy": 0, "medium": 0, "hard": 0}
        total_count = 0

        for submission in submissions:
            total_count += 1
            content_obj = submission.content_object
            difficulty = content_obj.level
            difficulty_counts[difficulty] = difficulty_counts.get(difficulty, 0) + 1

        difficulty_totals = self._get_total_problems_by_difficulty()

        return {
            "total_submissions_count": total_count,
            "easy_problems_submissions_count": difficulty_counts["easy"],
            "medium_problems_submissions_count": difficulty_counts["medium"],
            "hard_problems_submissions_count": difficulty_counts["hard"],
            "difficulty_totals": difficulty_totals,
        }

    def _build_problems_list(self, submissions_list):
        """Build problems list from submission objects"""
        problems_list = []
        for submission in submissions_list:
            content_obj = submission.content_object
            if not content_obj:
                continue

            problems_list.append(
                {
                    "id": content_obj.id,
                    "title": content_obj.title,
                    "level": content_obj.level,
                    "tag": content_obj.get_tags_list(),
                    "problem_type": "concept"
                    if isinstance(content_obj, ConceptBasedProblem)
                    else "dataset",
                    "slug": content_obj.slug,
                    "last_attempted": submission.created_timestamp,
                    "status": submission.verdict,
                }
            )

        return problems_list

    def _build_concepts_list(self, concept_data_list):
        """Build concepts list from concept data"""
        concepts_list = []
        for concept_data in concept_data_list:
            concept_id = concept_data["concept_id"]
            last_read = concept_data["last_read"]
            concept = Concept.objects.get(id=concept_id)

            concepts_list.append(
                {
                    "id": concept.id,
                    "title": concept.title,
                    "description": concept.description,
                    "slug": concept.slug,
                    "last_read": last_read,
                }
            )

        return concepts_list

    @action(detail=False, methods=["get"], url_path="(?P<username>[^/.]+)/problems")
    @problems_attempted_schema
    def problems_attempted(self, request, username=None):
        """GET /dashboard/<username>/problems/ - Get unique problems attempted by user"""
        user = self.get_user(username)
        if not user:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Get unique problems attempted by user using database-level query

        # Get latest submission per content_type, object_id
        latest_submissions = (
            Submission.objects.filter(user=user)
            .order_by("content_type", "object_id", "-created_timestamp")
            .distinct("content_type", "object_id")
        )

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(latest_submissions, request)

        if page is not None:
            problems_list = self._build_problems_list(page)
            return paginator.get_paginated_response(problems_list)

        # Fallback for non-paginated requests
        problems_list = self._build_problems_list(latest_submissions)
        return Response(problems_list)

    @action(detail=False, methods=["get"], url_path="(?P<username>[^/.]+)/concepts")
    @concepts_read_schema
    def concepts_read(self, request, username=None):
        """GET /dashboard/<username>/concepts/ - Get concepts read by user"""
        user = self.get_user(username)
        if not user:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Get unique concepts read by user using database-level query

        # Get unique concepts with their latest read timestamp
        unique_concepts_read = (
            ConceptsRead.objects.filter(user=user)
            .values("concept_id")
            .annotate(last_read=Max("read_timestamp"))
            .order_by("-last_read")
        )

        # Apply pagination at database level
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(unique_concepts_read, request)

        if page is not None:
            # Process only the paginated results
            concepts_list = self._build_concepts_list(page)
            return paginator.get_paginated_response(concepts_list)

        # Fallback for non-paginated requests
        concepts_list = self._build_concepts_list(unique_concepts_read)
        return Response(concepts_list)

    @action(detail=False, methods=["get"], url_path="(?P<username>[^/.]+)/submissions")
    @submissions_schema
    def submissions(self, request, username=None):
        """GET /dashboard/<username>/submissions/ - Get all submissions by user"""
        user = self.get_user(username)
        if not user:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Get all submissions by user, ordered by creation timestamp
        submissions = (
            Submission.objects.filter(user=user)
            .select_related("content_type")
            .order_by("-created_timestamp")
        )

        submissions_list = []
        for submission in submissions:
            content_obj = submission.content_object
            submissions_list.append(
                {
                    "id": submission.id,
                    "verdict": submission.verdict,
                    "verdict_display": submission.get_verdict_display(),
                    "created_timestamp": submission.created_timestamp,
                    "time_taken": submission.time_taken,
                    "memory_taken": submission.memory_taken,
                    "problem": {
                        "id": content_obj.id if content_obj else None,
                        "title": content_obj.title if content_obj else "Unknown",
                        "type": content_obj.problem_type  # DL, ML
                        if content_obj
                        else "Unknown",
                        "problem_type": "concept"  # concept, dataset
                        if isinstance(content_obj, ConceptBasedProblem)
                        else "dataset",
                        "level": content_obj.level if content_obj else "Unknown",
                        "slug": content_obj.slug if content_obj else None,
                    }
                    if content_obj
                    else None,
                }
            )

        # Apply pagination
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(submissions_list, request)

        if page is not None:
            return paginator.get_paginated_response(page)

        return Response(submissions_list)


class AuthenticatedUserViewSet(ViewSet):
    """
    ViewSet for authenticated user endpoints that require authentication
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [
        JSONParser,
        MultiPartParser,
        FormParser,
    ]

    @action(detail=False, methods=["post"], url_path="logout", url_name="logout")
    @logout_schema
    def logout(self, request):
        """POST /logout/"""
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data["refresh"]
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            request.session.flush()
            return Response({"message": "Successfully logged out"})
        except Exception:
            return Response(
                {"message": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        methods=["post"],
        url_path="complete-onboarding",
        url_name="complete-onboarding",
    )
    @onboarding_schema
    def complete_onboarding(self, request):
        """POST /complete-onboarding/"""
        user = request.user
        profile, _ = Profile.objects.get_or_create(user=user)
        serializer = OnboardingSerializer(instance=profile, data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        for field, value in validated_data.items():
            setattr(profile, field, value)
        profile.save()

        return Response({"message": "Onboarding completed successfully"})

    @action(
        detail=False, methods=["get"], url_path="user-detail", url_name="user-detail"
    )
    def get_user_detail(self, request):
        """GET /user-detail/"""
        user = request.user
        profile, _ = Profile.objects.get_or_create(user=user)

        profile_photo_url = ""
        if profile.profile_photo:
            profile_photo_url = request.build_absolute_uri(profile.profile_photo.url)

        user_data = {
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone_number": profile.phone_number or "",
            "organisation_name": profile.organisation_name or "",
            "address": profile.address or "",
            "language_selected": profile.language_selected or "",
            "profile_photo_url": profile_photo_url,
            "is_premium_user": profile.is_premium_user,
            "bio": profile.bio or "",
            "occupation": profile.occupation or "",
            "kaggle_profile_url": profile.kaggle_profile_url or "",
            "github": profile.github or "",
            "twitter": profile.twitter or "",
            "portfolio": profile.portfolio or "",
            "linkedin": profile.linkedin or "",
            "pronouns": profile.pronouns or "",
            "interests": profile.interests or "",
            "date_of_birth": (
                profile.date_of_birth.strftime("%Y-%m-%d")
                if profile.date_of_birth
                else ""
            ),
            "current_streak": profile.current_streak or 0,
            "longest_streak": profile.longest_streak or 0,
            "location": profile.address or "",
        }

        return Response({"user": user_data})

    @action(
        detail=False,
        methods=["patch"],
        url_path="user-detail-update",
        url_name="update-user-detail",
    )
    @update_user_detail_schema
    def update_user_detail(self, request):
        """PATCH /user-detail/"""
        user = request.user
        profile, created = Profile.objects.get_or_create(user=user)
        serializer = UserDetailSerializer(
            instance=profile, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)

        # Extract User model fields (first_name, last_name) from validated data
        validated_data = serializer.validated_data
        user_fields = {}
        if "first_name" in validated_data:
            user_fields["first_name"] = validated_data.pop("first_name")
        if "last_name" in validated_data:
            user_fields["last_name"] = validated_data.pop("last_name")

        # Update User model if there are user fields to update
        if user_fields:
            for field, value in user_fields.items():
                setattr(user, field, value)
            user.save()

        # Save Profile model with remaining fields
        serializer.save()
        return Response({"message": "User details updated successfully"})

    @action(
        detail=False, methods=["get"], url_path="header-data", url_name="header-data"
    )
    @header_data_swagger_schema
    def get_header_data(self, request):
        """GET /header-data/"""
        user = request.user
        profile, _ = Profile.objects.get_or_create(user=user)

        profile_photo_url = ""
        if profile.profile_photo:
            profile_photo_url = request.build_absolute_uri(profile.profile_photo.url)

        response_data = {
            "current_day_concept_read": profile.current_day_concept_read,
            "current_day_problem_solved": profile.current_day_problem_solved,
            "current_streak": profile.current_streak,
            "longest_streak": profile.longest_streak,
            "language_selected": profile.language_selected,
            "is_premium_user": profile.is_premium_user,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "profile_photo_url": profile_photo_url,
            "email": user.email,
            "username": user.username,
        }

        return Response(response_data)
