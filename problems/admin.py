from django.contrib import admin

from problems.models import (
    Comment,
    ConceptBasedProblem,
    DailyContent,
    DatasetBasedProblem,
    Note,
    Submission,
)

admin.site.register(DatasetBasedProblem)
admin.site.register(ConceptBasedProblem)
admin.site.register(Submission)
admin.site.register(DailyContent)
admin.site.register(Note)
admin.site.register(Comment)
