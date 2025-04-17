from django.shortcuts import render,redirect,HttpResponse
from .models import*
# Create your views here.
def index(request):
    return render(request,'index.html')

def logout(request):
    request.session.flush()
    return redirect('index')

def explore_trending(request):
    trending_movies = Movie.objects.all()
    trending_reviews = Review.objects.all()[:6]
    return render(request, 'explore_trending.html', {'trending_movies':trending_movies, 'trending_reviews':trending_reviews})

# User

def home(request):
    if 'email' in request.session:
        email = request.session['email']
        user = Register.objects.get(email=email)
        return render(request,'home.html', {'user':user})   
    return redirect('login')

from django.core.mail import send_mail
from django.conf import settings

def register(request):
    if request.method=='POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        password = request.POST['password']
        if Register.objects.filter(email=email).exists():
            alert="<script>alert('Email already exists');window.location.href='/register/'</script>"
            return HttpResponse(alert)
        else:
            register = Register(name=name, email=email, phone=phone, password=password)
            register.save()
            
            # Send confirmation email to the registered user
            subject = 'Welcome to Moview - Registration Confirmation'
            message = f'''Dear {name},

            Thank you for creating your account with Moview. Your registration has been successfully completed.

            You can now log in to access all our features and services.

            If you have any questions or need assistance, please don't hesitate to contact our support team.

            Best regards,
            The Moview Team'''

            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email]
                        
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            
            return redirect('login')
    return render(request,'register.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = Register.objects.get(email=email, password=password)
            request.session['email'] = user.email  
            return redirect('home')
        except Register.DoesNotExist:
            alert = "<script>alert('Invalid credentials');window.location.href='/login/';</script>"
            return HttpResponse(alert)
    return render(request, 'login.html')

def profile(request):
    if 'email' in request.session:
        email = request.session['email']
        user = Register.objects.get(email=email)
        return render(request,'profile.html', {'user':user})
    else:
        return redirect('login')
    
def edit_profile(request):
    if 'email' in request.session:
        email = request.session['email']
        user = Register.objects.get(email=email)
        if request.method=='POST':
            name = request.POST['name']
            phone = request.POST['phone']
            user.name = name
            user.phone = phone
            user.save()
            return redirect('profile')
        return render(request,'edit_profile.html', {'user':user})
    else:
        return redirect('login')
    
def delete_account(request,uid):
    Register.objects.get(id=uid).delete()
    alert = "<script>alert('Account deleted successfully');window.location.href='/'</script>"
    return HttpResponse(alert)
    return redirect('index')
    
def user_list_movies(request):
    movies = Movie.objects.all()
    return render(request,'user_list_movies.html', {'movies':movies})


def add_review(request, rid):
    if 'email' in request.session:
        email = request.session['email']
        user = Register.objects.get(email=email)
        movie = Movie.objects.get(id=rid)
        if request.method=='POST':
            rating = request.POST['rating']
            comment = request.POST['comment']
            if Review.objects.filter(user=user, movie=movie).exists():
                alert="<script>alert('You have already reviewed this movie');window.location.href='/user_list_movies/'</script>"
                return HttpResponse(alert)
            else:
                review = Review(user=user, movie=movie, rating=rating, comment=comment)
                review.save()
                alert="<script>alert('Review added successfully');window.location.href='/user_list_movies/'</script>"
                return HttpResponse(alert)
        return render(request,'add_review.html', {'movie':movie})
    else:
        return redirect('login')    


from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Review, ReviewLike, Register, Movie
from django.db.models import Count

def user_view_reviews(request, rid):
    review = Review.objects.filter(movie=rid)
    
    # Annotate reviews with like and dislike counts
    review = review.annotate(
        like_count=Count('reactions', filter=models.Q(reactions__reaction_type='like')),
        dislike_count=Count('reactions', filter=models.Q(reactions__reaction_type='dislike'))
    )
    
    return render(request, 'user_view_reviews.html', {'review': review})

def handle_review_reaction(request, review_id, reaction_type):
    if request.method == 'POST':
        review = get_object_or_404(Review, id=review_id)
        user_id = request.session.get('email')
        
        if not user_id:
            return JsonResponse({'error': 'User not logged in'}, status=401)
        
        user = get_object_or_404(Register, email=user_id)
        
        # Check if the user already has a reaction for this review
        try:
            existing_reaction = ReviewLike.objects.get(review=review, user=user)
            
            if existing_reaction.reaction_type == reaction_type:
                # If the same reaction, remove it (toggle off)
                existing_reaction.delete()
                action = 'removed'
            else:
                # If different reaction, update it
                existing_reaction.reaction_type = reaction_type
                existing_reaction.save()
                action = 'changed'
        except ReviewLike.DoesNotExist:
            # Create a new reaction
            ReviewLike.objects.create(
                review=review,
                user=user,
                reaction_type=reaction_type
            )
            action = 'added'
        
        # Get updated counts
        like_count = ReviewLike.objects.filter(review=review, reaction_type='like').count()
        dislike_count = ReviewLike.objects.filter(review=review, reaction_type='dislike').count()
        
        return JsonResponse({
            'success': True,
            'action': action,
            'like_count': like_count,
            'dislike_count': dislike_count
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def like_review(request, review_id):
    return handle_review_reaction(request, review_id, 'like')

def dislike_review(request, review_id):
    return handle_review_reaction(request, review_id, 'dislike')

def list_user_reviews(request):
    if 'email' in request.session:
        email = request.session['email']
        user = Register.objects.get(email=email)
        
        # Get all reviews by the user
        reviews = Review.objects.filter(user=user)
        
        # Annotate each review with like and dislike counts
        for review in reviews:
            # Count likes
            review.likes_count = review.reactions.filter(reaction_type='like').count()
            # Count dislikes
            review.dislikes_count = review.reactions.filter(reaction_type='dislike').count()
        
        return render(request, 'list_user_reviews.html', {'review': reviews})
    else:
        return redirect('login')
    
def delete_my_review(request, rid):
    rev=Review.objects.get(id=rid)
    rev.delete()
    alert="<script>alert('Review deleted successfully');window.location.href='/list_user_reviews/'</script>"
    return HttpResponse(alert)


from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
import random
import string
from .models import Register, OTPVerification

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def forgot_password(request):
    """Handle the initial forgot password request"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # Check if the email exists in the database
        try:
            user = Register.objects.get(email=email)
            
            # Generate OTP and save it
            otp = generate_otp()
            
            # Delete any existing OTP entries for this email
            OTPVerification.objects.filter(email=email).delete()
            
            # Create new OTP entry
            OTPVerification.objects.create(email=email, otp=otp)
            
            # Send OTP to the user's email
            send_mail(
                'Password Reset OTP',
                f'Your OTP for password reset is: {otp}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            # Redirect to OTP verification page
            return redirect('verify_otp', email=email)
        
        except Register.DoesNotExist:
            messages.error(request, "Email not found. Please check your email address.")
    
    return render(request, 'forgot_password.html')

def verify_otp(request, email):
    """Handle OTP verification"""
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        
        try:
            # Verify OTP
            otp_obj = OTPVerification.objects.get(email=email, otp=entered_otp)
            
            # OTP is correct, redirect to reset password page
            return redirect('reset_password', email=email, otp=entered_otp)
        
        except OTPVerification.DoesNotExist:
            messages.error(request, "Invalid OTP. Please try again.")
    
    return render(request, 'verify_otp.html', {'email': email})

def reset_password(request, email, otp):
    """Handle password reset"""
    # Verify the OTP again for security
    try:
        otp_obj = OTPVerification.objects.get(email=email, otp=otp)
    except OTPVerification.DoesNotExist:
        messages.error(request, "Invalid request. Please try again.")
        return redirect('forgot_password')
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'reset_password.html', {'email': email, 'otp': otp})
        
        # Update user's password
        try:
            user = Register.objects.get(email=email)
            user.password = new_password  # In a real app, hash this password
            user.save()
            
            # Clean up the OTP
            otp_obj.delete()
            
            messages.success(request, "Password has been reset successfully. You can now login with your new password.")
            return redirect('login')
        
        except Register.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('forgot_password')
    
    return render(request, 'reset_password.html', {'email': email, 'otp': otp})









# Admin
def adminhome(request):
    u=Register.objects.count()
    m=Movie.objects.count()
    r=Review.objects.count()
    # f=Feedback.objects.count()
    # n=News.objects.count()
    return render(request,'adminhome.html', {'u':u, 'm':m, 'r':r})

def adminlogin(request):
    if request.method=='POST':
        email = request.POST['email']
        password = request.POST['password']
        if email=='moviewteam469@gmail.com' and password=='admin':
            return redirect('adminhome')
        else:
            alert="<script>alert('Invalid credentials');window.location.href='/adminlogin/'</script>"
            return HttpResponse(alert)
    return render(request,'adminlogin.html')

def add_movie(request):
    if request.method=='POST':
        title = request.POST['title']
        director = request.POST['director']
        release_date = request.POST['release_date']
        duration = request.POST['duration']
        language = request.POST['language']
        genre = request.POST['genre']
        description = request.POST['description']
        trailer_link = request.POST['trailer_link']
        poster = request.FILES['poster']
        movie = Movie(title=title, director=director, release_date=release_date, duration=duration, language=language, genre=genre, description=description, trailer_link=trailer_link, poster=poster)
        movie.save()
        alert="<script>alert('Movie added successfully');window.location.href='/list_movies/'</script>"
        return HttpResponse(alert)
    return render(request,'add_movie.html')

def list_movies(request):
    movies = Movie.objects.all()
    return render(request,'list_movies.html', {'movies':movies})

def delete_movie(request, mid):
    movie = Movie.objects.get(id=mid)
    movie.delete()
    alert="<script>alert('Movie deleted successfully');window.location.href='/list_movies/'</script>"
    return HttpResponse(alert)

def edit_movie(request, mid):
    movie = Movie.objects.get(id=mid)
    if request.method=='POST':
        title = request.POST['title']
        director = request.POST['director']
        release_date = request.POST['release_date']
        duration = request.POST['duration']
        language = request.POST['language']
        genre = request.POST['genre']
        description = request.POST['description']
        trailer_link = request.POST['trailer_link']
        poster = request.FILES.get('poster')
        movie.title = title
        movie.director = director
        movie.release_date = release_date
        movie.duration = duration
        movie.language = language
        movie.genre = genre
        movie.description = description
        movie.trailer_link = trailer_link
        if poster:
            movie.poster = poster
        movie.save()
        alert="<script>alert('Movie updated successfully');window.location.href='/list_movies/'</script>"
        return HttpResponse(alert)
    return render(request,'edit_movie.html', {'movie':movie})

def user_list(request):
    users = Register.objects.all()
    return render(request,'user_list.html', {'users':users})

def delete_user(request, uid):
    user = Register.objects.get(id=uid)
    user.delete()
    alert="<script>alert('User deleted successfully');window.location.href='/user_list/'</script>"
    return HttpResponse(alert)

def view_reviews(request):
    reviews = Review.objects.all()
    return render(request,'view_reviews.html', {'reviews':reviews})

def view_review_reactions(request):
    reactions = ReviewLike.objects.all()
    return render(request,'view_review_reactions.html', {'reactions':reactions})