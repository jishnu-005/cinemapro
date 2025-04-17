from django.db import models

# Create your models here.
class Register(models.Model):
    name=models.CharField(max_length=30)
    email=models.EmailField(unique=True)
    phone=models.IntegerField()
    password=models.CharField(max_length=50)

class OTPVerification(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - {self.otp}"

class Movie(models.Model):
    title=models.CharField(max_length=100)
    director=models.CharField(max_length=50)
    release_date=models.DateField()
    duration=models.CharField(max_length=80)
    language=models.CharField(max_length=200)
    genre=models.CharField(max_length=50)
    description=models.TextField()
    trailer_link=models.URLField()
    poster=models.ImageField(upload_to='movie_posters/')

class Review(models.Model):
    movie=models.ForeignKey(Movie, on_delete=models.CASCADE)
    user=models.ForeignKey(Register, on_delete=models.CASCADE)
    rating=models.IntegerField()
    comment=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)

class ReviewLike(models.Model):
    LIKE = 'like'
    DISLIKE = 'dislike'
    REACTION_CHOICES = [
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike'),
    ]
    
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(Register, on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=10, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Ensure a user can only have one reaction per review
        unique_together = ['review', 'user']