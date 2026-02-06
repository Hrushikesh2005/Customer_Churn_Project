from django.db import models
from django.contrib.auth.models import User

class ChurnAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='churn_analyses')
    input_file = models.FileField(upload_to='uploads/input/', null=True, blank=True)
    output_file = models.FileField(upload_to='uploads/output/')
    filename = models.CharField(max_length=255)
    churn_rate = models.FloatField()
    accuracy = models.FloatField(null=True, blank=True)
    has_churn_column = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.filename} ({self.created_at.strftime('%Y-%m-%d')})"
