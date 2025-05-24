from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Question, Score
from django.contrib.auth.models import User
from django.db.models import Max
import random

# Register a new user
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('main_menu')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

# Log in a user
def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('main_menu')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

# Log out a user
def user_logout(request):
    logout(request)
    return redirect('login')

# Main menu for the quiz
def main_menu(request):
    return render(request, 'main_menu.html')

# Start the quiz, reset the score, and question index
def start_quiz(request):
    questions = list(Question.objects.values_list('id', flat=True))
    random.shuffle(questions)
    request.session['question_ids'] = questions  # Save shuffled order
    request.session['score'] = 0
    request.session['question_index'] = 0
    return redirect('quiz_question')

# Show the current quiz question
def quiz_question(request):
    question_ids = request.session.get('question_ids', [])
    index = request.session.get('question_index', 0)

    if index >= len(question_ids):
        return redirect('quiz_results')

    question_id = question_ids[index]
    question = Question.objects.get(id=question_id)

    feedback = request.session.get('feedback', None)
    request.session['feedback'] = None  # Clear feedback

    return render(request, 'quiz.html', {
        'question': question,
        'feedback': feedback
    })

# Check the user's answer and update score
def check_answer(request):
    if request.method == "POST":
        user_answer = int(request.POST.get('answer'))
        question_id = int(request.POST.get('question_id'))
        question = Question.objects.get(id=question_id)

        correct_answer = question.correct_option

        if user_answer == correct_answer:
            request.session['score'] += 5
            feedback = "Correct!"
            feedback_color = "green"
        else:
            feedback = f"Incorrect! The correct answer is Option {correct_answer}."
            feedback_color = "red"

        request.session['feedback'] = {
            'feedback': feedback,
            'feedback_color': feedback_color,
            'correct_answer': correct_answer,
            'user_answer': user_answer
        }

        request.session['question_index'] += 1  # Move to the next question
        return redirect('quiz_question')

# Show the quiz results
def quiz_results(request):
    score = request.session.get('score', 0)
    user = request.user
    Score.objects.create(user=user, score=score)

    return render(request, 'results.html', {'score': score})

# Show the high scores
def high_scores(request):
    # Get highest score for each user
    user_high_scores = (
        Score.objects.values('user__username')  # Get unique users
        .annotate(max_score=Max('score'))  # Get max score for each user
        .order_by('-max_score')  # Order by highest score
    )

    return render(request, 'high_scores.html', {'user_high_scores': user_high_scores})

# Update a user's score if necessary
def update_score(user, new_score):
    # Check if the user already has a score entry
    existing_score = Score.objects.filter(user=user).order_by('-score').first()

    if existing_score:
        # If the new score is higher, update the existing record
        if new_score > existing_score.score:
            existing_score.score = new_score
            existing_score.save()
    else:
        # If there's no score yet, create a new one
        Score.objects.create(user=user, score=new_score)
