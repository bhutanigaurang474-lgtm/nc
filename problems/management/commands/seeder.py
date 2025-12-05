import random

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from concepts.models import Concept
from problems.models import ConceptBasedProblem, DailyContent, DatasetBasedProblem


class Command(BaseCommand):
    help = "Populate dummy ConceptBasedProblem and DatasetBasedProblem instances"

    def handle(self, *args, **kwargs):
        # fake = Faker()
        # levels = ["easy", "medium", "hard"]
        # problem_types = ["ML", "DL"]
        # concept_types = ["ML", "DL"]

        # for _ in range(50):
        #     level = random.choice(levels)
        #     problem_type = random.choice(problem_types)
        #     concept_type = random.choice(concept_types)
        #     user = User.objects.get(id=1)

        #     # # ConceptBasedProblem dummy
        #     # ConceptBasedProblem.objects.create(
        #     #     title=fake.word(),
        #     #     problem_type=problem_type,
        #     #     description=fake.paragraph(),
        #     #     editorial_description=fake.paragraph(),
        #     #     level=level,
        #     #     accepted_submissions=random.randint(0, 50),
        #     #     total_submissions=random.randint(50, 100),
        #     #     code_editor_template=fake.text(max_nb_chars=200),
        #     #     ideal_solution_code=fake.text(max_nb_chars=200),
        #     #     validation_testcases={
        #     #         "input": fake.word(),
        #     #         "expected_output": fake.word()
        #     #     },
        #     #     submission_testcases={
        #     #         "input": fake.word(),
        #     #         "expected_output": fake.word()
        #     #     }
        #     # )

        #     # # DatasetBasedProblem dummy
        #     # DatasetBasedProblem.objects.create(
        #     #     title=fake.word(),
        #     #     problem_type=problem_type,
        #     #     description=fake.paragraph(),
        #     #     editorial_description=fake.paragraph(),
        #     #     level=level,
        #     #     accepted_submissions=random.randint(0, 50),
        #     #     total_submissions=random.randint(50, 100),
        #     #     evaluation_metrics_dict={
        #     #         "accuracy": round(random.uniform(0.7, 0.99), 2),
        #     #         "f1_score": round(random.uniform(0.7, 0.99), 2)
        #     #     },
        #     #     test_data_file_path=f"/dummy/path/test_{fake.uuid4()}.csv",
        #     #     data_available_to_user_file_path=f"/dummy/path/data_{fake.uuid4()}.csv",
        #     #     ideal_metrics_json_file_path=f"/dummy/path/ideal_{fake.uuid4()}.json"
        #     # )
        #     concept = Concepts.objects.create(
        #         description=fake.paragraph(),
        #         one_liner_desc=fake.sentence(),
        #         level=level,
        #         preview_image_url=fake.image_url(),
        #         concept_type=concept_type,
        #         author=user,
        #         title=fake.word(),
        #     )

        # self.stdout.write(self.style.SUCCESS('Dummy ConceptBasedProblem and DatasetBasedProblem instances created!'))
        from datetime import date, timedelta

        # Ensure there are enough objects
        concepts = list(Concept.objects.all())
        concept_problems = list(ConceptBasedProblem.objects.all())
        dataset_problems = list(DatasetBasedProblem.objects.all())

        if not concepts or (not concept_problems and not dataset_problems):
            self.stdout.write(self.style.ERROR("Not enough data to seed DailyContent."))
            return

        start_date = date(2025, 6, 1)
        end_date = date(2025, 7, 31)
        current_date = start_date

        while current_date <= end_date:
            concept = random.choice(concepts)

            # Randomly choose one type of problem
            use_dataset = random.choice([True, False])
            problem = None

            if use_dataset and dataset_problems:
                problem = random.choice(dataset_problems)
            elif concept_problems:
                problem = random.choice(concept_problems)

            # Fallback logic if one type is empty
            if problem is None:
                if dataset_problems:
                    problem = random.choice(dataset_problems)
                elif concept_problems:
                    problem = random.choice(concept_problems)

            try:
                if problem:
                    _ = DailyContent.objects.create(
                        date=current_date,
                        content_type=ContentType.objects.get_for_model(problem),
                        object_id=problem.id,
                        concept=concept,
                    )
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Skipped {current_date}: {e}"))

            current_date += timedelta(days=1)

        self.stdout.write(
            self.style.SUCCESS("✅ DailyContent entries created for June & July 2025.")
        )
