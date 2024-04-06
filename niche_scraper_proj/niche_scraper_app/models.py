from django.db import models


# Create your models here.
class School(models.Model):
    title = models.CharField(max_length=255)
    images = models.JSONField(default=list)
    badge = models.CharField(max_length=255)
    facts = models.JSONField(default=list)
    ratings = models.CharField(max_length=255)
    num_reviews = models.CharField(max_length=255)
    report_card = models.JSONField(default=dict)
    editorial = models.TextField()
    about = models.JSONField(default=dict)
    rankings = models.JSONField(default=list)
    admissions = models.JSONField(default=dict)
    cost = models.JSONField(default=dict)
    academics = models.JSONField(default=dict)
    majors = models.JSONField(default=dict)
    online = models.JSONField(default=dict)
    students = models.JSONField(default=dict)
    campus_life = models.JSONField(default=dict)
    after_college = models.JSONField(default=dict)

    def __str__(self):
        return self.title


class Review(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="reviews")
    rating = models.CharField(max_length=255)
    text = models.TextField()

    def __str__(self):
        return f"{self.school} - {self.rating}"


class Scholarship(models.Model):
    title = models.CharField(max_length=200)
    deadline = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    offered_by = models.CharField(max_length=200)
    state = models.CharField(max_length=100)
    description = models.TextField()
    major = models.CharField(max_length=200)
    type = models.CharField(max_length=100)

    def __str__(self):
        return self.title
