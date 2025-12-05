from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from .models import ConceptBasedProblem, DatasetBasedProblem, Note, Submission
from .utils import get_problem_by_type_and_slug


class ProblemListSerializer(serializers.ModelSerializer):
    """Serializer for listing problems in the table view"""

    status = serializers.SerializerMethodField()
    notes_id = serializers.SerializerMethodField()
    problem_type = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    submissions = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = ConceptBasedProblem  # This will be overridden in the ViewSet
        fields = [
            "id",
            "title",
            "slug",
            "level",
            "acceptance_rate",
            "status",
            "problem_type",
            "tags",
            "notes_id",
            "submissions",
            "type",
        ]

    def get_status(self, obj):
        user = self.context.get("user")
        if not user or not user.is_authenticated:
            return 0

        submission = Submission.objects.filter(
            user=user,
            verdict=3,
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id,
        ).first()
        return submission.verdict if submission else 0

    def get_notes_id(self, obj):
        user = self.context.get("user")
        if not user or not user.is_authenticated:
            return None

        notes = Note.objects.filter(
            user=user,
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id,
        ).first()
        return notes.id if notes else None

    def get_type(self, obj):
        return obj.problem_type

    def get_problem_type(self, obj):
        return "concept" if isinstance(obj, ConceptBasedProblem) else "dataset"

    def get_tags(self, obj):
        return obj.get_tags_list()

    def get_submissions(self, obj):
        return obj.total_submissions


class NotesSerializer(serializers.Serializer):
    """Serializer for handling notes validation and creation"""

    notes = serializers.CharField(required=True, allow_blank=False)
    problem_type = serializers.CharField(required=True)
    problem_id = serializers.IntegerField(required=True)

    def validate_problem_type(self, value):
        """Validate that problem_type is either 'concept' or 'dataset'"""
        if value not in ["concept", "dataset"]:
            raise serializers.ValidationError(
                "Invalid problem type. Use 'concept' or 'dataset'."
            )
        return value

    def validate(self, attrs):
        """Validate the complete data"""
        notes_content = attrs.get("notes")
        problem_id = attrs.get("problem_id")

        if not notes_content or not problem_id:
            raise serializers.ValidationError("Notes and problem ID are required")

        # Validate that the problem exists
        problem_type = attrs.get("problem_type")
        problem = get_problem_by_type_and_slug(problem_type, problem_id)
        if not problem:
            raise serializers.ValidationError("Problem not found")

        attrs["problem"] = problem
        return attrs


class RunCodeSerializer(serializers.Serializer):
    """Serializer for handling run code validation"""

    code = serializers.CharField(required=True, allow_blank=False)
    problem_id = serializers.IntegerField(required=True)
    problem_type = serializers.CharField(required=True)
    testcases = serializers.ListField(required=False, allow_empty=True)
    run_only = serializers.BooleanField(required=True)

    def validate_problem_type(self, value):
        """Validate that problem_type is either 'concept' or 'dataset'"""
        if value not in ["concept", "dataset"]:
            raise serializers.ValidationError(
                "Invalid problem type. Use 'concept' or 'dataset'."
            )
        return value

    def validate(self, attrs):
        """Validate the complete data"""
        code = attrs.get("code")
        problem_id = attrs.get("problem_id")
        problem_type = attrs.get("problem_type")
        run_only = attrs.get("run_only")

        if not all([code, problem_id, problem_type]) or run_only is None:
            raise serializers.ValidationError(
                "All fields (code, problem_id, problem_type, run_only) are required."
            )

        # Validate that the problem exists
        try:
            if problem_type == "concept":
                problem = ConceptBasedProblem.objects.get(id=problem_id)
            else:
                problem = DatasetBasedProblem.objects.get(id=problem_id)
        except (ConceptBasedProblem.DoesNotExist, DatasetBasedProblem.DoesNotExist):
            raise serializers.ValidationError("Problem not found.")

        attrs["problem"] = problem
        return attrs


class CommentSerializer(serializers.Serializer):
    """Serializer for handling comment validation"""

    content = serializers.CharField(required=True, allow_blank=False)
    parent_comment_id = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, attrs):
        """Validate the complete data"""
        content = attrs.get("content")
        parent_comment_id = attrs.get("parent_comment_id")

        if not content:
            raise serializers.ValidationError("Missing required fields")

        # Validate parent comment if provided
        if parent_comment_id:
            try:
                from .models import Comment

                parent_comment = Comment.objects.get(id=parent_comment_id)
                if parent_comment.parent_comment:
                    raise serializers.ValidationError(
                        "Replies to replies are not allowed."
                    )
                attrs["parent_comment"] = parent_comment
            except Comment.DoesNotExist:
                raise serializers.ValidationError("Parent comment not found")
        else:
            attrs["parent_comment"] = None

        return attrs


class CommentReactionSerializer(serializers.Serializer):
    """Serializer for handling comment reaction validation"""

    comment_id = serializers.IntegerField(required=True)
    action = serializers.CharField(required=True)

    def validate_action(self, value):
        """Validate that action is either 'like' or 'dislike'"""
        if value not in ["like", "dislike"]:
            raise serializers.ValidationError("Invalid action")
        return value

    def validate(self, attrs):
        """Validate the complete data"""
        comment_id = attrs.get("comment_id")

        # Validate that the comment exists
        try:
            from .models import Comment

            comment = Comment.objects.get(id=comment_id)
            attrs["comment"] = comment
        except Comment.DoesNotExist:
            raise serializers.ValidationError("Comment not found")

        return attrs
