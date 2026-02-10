from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import ChatRoom, Message
from .forms import SignUpForm, LoginForm

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'login.html', {'form': form, 'type': 'Signup'})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form, 'type': 'Login'})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def index(request):
    rooms = ChatRoom.objects.all()
    if request.method == "POST":
        room_name = request.POST.get("room_name")
        if room_name:
            ChatRoom.objects.get_or_create(name=room_name)
            return redirect('index')
    return render(request, 'index.html', {'rooms': rooms})

@login_required
def room(request, room_name):
    chat_room, created = ChatRoom.objects.get_or_create(name=room_name)
    # We will fetch history in the consumer or passing it here?
    # User requirement: "When a user joins a room, fetch the last 50 messages from the database and display them."
    # Usually this is easier done in the HTTP view for initial load, OR via WebSocket "fetch_history". 
    # The requirement says "History Logs: When a user joins a room..." 
    # If we do it in WebSocket on_connect, the page loads empty then fills.
    # If we do it in View, the page renders with messages.
    # Both are valid. Doing it in View is robust for SEO/noscript (not that it matters for a chat app). 
    # But usually "fetch from DB and display" implies passing context.
    # However, keeping it in consumer allows real-time updates to "history" if we wanted.
    # Let's do it in the View for simplicity of rendering `base.html` etc.
    # Wait, the encrypted messages need to be decrypted.
    # The Model has a property `decrypted_content`.
    
    messages = Message.objects.filter(room=chat_room).order_by('timestamp')[:50]
    
    return render(request, 'room.html', {
        'room_name': room_name,
        'messages': messages,
        'user': request.user
    })




