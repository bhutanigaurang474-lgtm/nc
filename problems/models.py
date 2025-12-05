from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models

from concepts.models import Concept
from courses.models import Course
from ncore.models import GenericRelation, Slugged, Tagged


class BaseProblem(Tagged, Slugged, models.Model):
    LEVEL_CHOICES = [
        ("easy", "Easy"),
        ("medium", "Medium"),
        ("hard", "Hard"),
    ]
    PROBLEM_CHOICES = [
        ("ML", "Machine Learning"),
        ("DL", "Deep Learning"),
    ]

    problem_type = models.CharField(
        max_length=10, choices=PROBLEM_CHOICES, default="ML"
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    description = models.TextField(null=True, blank=True)
    editorial_description = models.TextField(null=True, blank=True)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    last_updated_timestamp = models.DateTimeField(auto_now=True)
    creation_timestamp = models.DateTimeField(auto_now_add=True)
    accepted_submissions = models.IntegerField(default=0)
    total_submissions = models.IntegerField(default=0)
    course_id = models.ForeignKey(
        Course, on_delete=models.SET_NULL, null=True, blank=True
    )

    @property
    def acceptance_rate(self):
        if self.accepted_submissions == 0:
            return 0
        return round((self.accepted_submissions / self.total_submissions) * 100, 2)

    class Meta:
        abstract = True


class DatasetBasedProblem(BaseProblem):
    evaluation_metrics_dict = models.JSONField()
    test_data_file_path = models.CharField(max_length=500, null=True, blank=True)
    data_available_to_user_file_path = models.CharField(max_length=500)
    ideal_metrics_json_file_path = models.CharField(
        max_length=500, null=True, blank=True
    )


class ConceptBasedProblem(BaseProblem):
    code_editor_template = models.TextField(null=True, blank=True)
    ideal_solution_code = models.TextField(null=True, blank=True)
    validation_testcases = models.JSONField(null=True, blank=True)
    submission_testcases = models.JSONField(null=True, blank=True)


class Submission(GenericRelation, models.Model):
    STATUS_CHOICES = [
        (1, "In Queue"),
        (2, "Processing"),
        (3, "Accepted"),
        (4, "Wrong Answer"),
        (5, "Time Limit Exceeded"),
        (6, "Compilation Error"),
        (7, "Runtime Error"),
        (8, "Judgement Failed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.TextField(null=True, blank=True)
    verdict = models.IntegerField(choices=STATUS_CHOICES, default=1)
    created_timestamp = models.DateTimeField(auto_now_add=True)
    updated_timestamp = models.DateTimeField(auto_now=True)

    time_taken = models.FloatField(null=True, blank=True)
    memory_taken = models.FloatField(null=True, blank=True)
    failed_testcase_info = models.JSONField(null=True, blank=True)

    def clean(self):
        super().clean()

        # Ensure the content type is one of our problem types
        allowed_types = [
            ContentType.objects.get_for_model(DatasetBasedProblem),
            ContentType.objects.get_for_model(ConceptBasedProblem),
        ]
        if self.content_type not in allowed_types:
            raise ValidationError(
                "Problem must be either DatasetBasedProblem or ConceptBasedProblem."
            )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Get the problem instance
        problem = self.content_object

        # Update submission counts
        problem.total_submissions += 1
        if self.verdict == 3:  # 3 is "Accepted" in STATUS_CHOICES
            problem.accepted_submissions += 1
        problem.save()

    def __str__(self):
        return f"{self.user.username} - {self.content_object.slug} - {self.verdict}"


class Note(GenericRelation, models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    note = models.TextField(default="")
    note_creation_timestamp = models.DateTimeField(auto_now_add=True)
    note_update_timestamp = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()

        # Ensure the content type is one of our problem types
        allowed_types = [
            ContentType.objects.get_for_model(DatasetBasedProblem),
            ContentType.objects.get_for_model(ConceptBasedProblem),
        ]
        if self.content_type not in allowed_types:
            raise ValidationError(
                "Problem must be either DatasetBasedProblem or ConceptBasedProblem."
            )

    def __str__(self):
        return f"{self.user.username} - {self.note_update_timestamp}"


class DailyContent(GenericRelation, models.Model):
    date = models.DateField(unique=True)

    concept = models.ForeignKey(Concept, on_delete=models.CASCADE)

    def clean(self):
        super().clean()

        # Ensure the content type is one of our problem types
        allowed_types = [
            ContentType.objects.get_for_model(DatasetBasedProblem),
            ContentType.objects.get_for_model(ConceptBasedProblem),
        ]
        if self.content_type not in allowed_types:
            raise ValidationError(
                "Problem must be either DatasetBasedProblem or ConceptBasedProblem."
            )

    def __str__(self):
        return str(self.date)


class UserDailyProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    daily_content = models.ForeignKey(DailyContent, on_delete=models.CASCADE)
    solved = models.BooleanField(default=False)
    concept_read = models.BooleanField(default=False)

    class Meta:
        unique_together = (
            "user",
            "daily_content",
        )  # Ensures one entry per user per date

    def __str__(self):
        return f"{self.user.username} - {self.daily_content.date} - Solved: {self.solved}, Concept Read: {self.concept_read}"


class Comment(GenericRelation, models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    content = models.TextField()
    parent_comment = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    like_by_users = models.ManyToManyField(
        User, related_name="liked_comments", blank=True
    )
    dislike_by_users = models.ManyToManyField(
        User, related_name="disliked_comments", blank=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.created_at}"

    def get_replies(self):
        return Comment.objects.filter(parent_comment=self)

    def clean(self):
        super().clean()

        # Ensure the content type is one of our problem types
        allowed_types = [
            ContentType.objects.get_for_model(DatasetBasedProblem),
            ContentType.objects.get_for_model(ConceptBasedProblem),
        ]
        if self.content_type not in allowed_types:
            raise ValidationError(
                "Problem must be either DatasetBasedProblem or ConceptBasedProblem."
            )

        if self.parent_comment and self.parent_comment.parent_comment:
            raise ValidationError("Replies to replies are not allowed.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=["parent_comment"]),
        ]
