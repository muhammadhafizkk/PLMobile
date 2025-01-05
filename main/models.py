from django import models

class User(models.Model):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255)
    # You might not need to store the password since authentication
    # is handled by Project B, but you can decide based on your requirements
    password = models.CharField(max_length=255)
    # Additional fields you might want to store
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

    class Meta:
        # Define the collection name in MongoDB
        db_table = 'user'