from django.db import models
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.conf import settings
import os

class Tool(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50)
    description = models.TextField()
    template_name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.template_name:
            self.template_name = f"{self.name.lower().replace(' ', '_')}_tool"
        
        super().save(*args, **kwargs)

        # Create a custom template for the tool
        template_content = render_to_string('tools/tool_template.html', {'tool': self})
        template_path = os.path.join(settings.BASE_DIR, 'tools', 'templates', 'tools', f'{self.template_name}.html')
        
        with open(template_path, 'w') as f:
            f.write(template_content)

    def __str__(self):
        return self.name