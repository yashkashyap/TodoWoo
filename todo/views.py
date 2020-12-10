from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .forms import TodoForm
from .models import Todo
import re

LOGGED_IN = False

def home(request):
    return render(request, 'todo/home.html', {'title':'TodoWoo'})

def signupuser(request):
    global LOGGED_IN

    if LOGGED_IN == False:
        if request.method == 'GET':
            return render(request, 'todo/signupuser.html', {'title':'Signup'})
        else:
            uname = request.POST['username']
            passw = request.POST['password']
            cpassw = request.POST['cpassword']
            if uname == '' or passw == '' or cpassw =='':
                return render(request, 'todo/signupuser.html', {'error':'Please fill in all the fields.', 'title':'Signup'})

            elif len(re.findall(r'[a-zA-Z0-9_]+', uname)) > 1:
                return render(request, 'todo/signupuser.html', {'unameerror':'Username must contain only numbers, alphabets and underscore(_).', 'title':'Signup'})

            if passw == cpassw:
                try:
                    user = User.objects.create_user(username=uname, password=passw)
                    user.save()
                    login(request, user)
                    LOGGED_IN = True
                    return redirect('currenttodos')
                except IntegrityError:
                    return render(request, 'todo/signupuser.html', {'error':'That username has already been taken.', 'title':'Signup'})

            else:
                return render(request, 'todo/signupuser.html', {'passerror':'Passwords do not match.', 'title':'Signup'})

def loginuser(request):
    global LOGGED_IN

    if LOGGED_IN == False:
        if request.method == 'GET':
            return render(request, 'todo/loginuser.html')
        else:
            uname = request.POST['username']
            passw = request.POST['password']
            user = authenticate(request, username=uname, password=passw)
            if user is None:
                if uname == '' or passw == '':
                    return render(request, 'todo/loginuser.html', {'error':'Please fill in all the fields.', 'title':'Login'})
                else:
                    return render(request, 'todo/loginuser.html', {'error':'Wrong Username or Password.', 'title':'Login'})
            else:
                login(request, user)
                LOGGED_IN = True
                return redirect('currenttodos')

@login_required
def logoutuser(request):
    global LOGGED_IN

    if request.method == 'POST':
        LOGGED_IN = False
        logout(request)
        return redirect('home')

@login_required
def createtodo(request):
    if request.method == 'GET':
        return render(request, 'todo/createtodo.html', {'form':TodoForm(), 'title':'TodoWoo'})
    else:
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/createtodo.html', {'form':TodoForm(), 'error':'Invalid Input passed in.', 'title':'TodoWoo'})

@login_required
def currenttodos(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'todo/currenttodos.html', {'todos':todos, 'length':todos.__len__(), 'title':'TodoWoo'})

@login_required
def completedtodos(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'todo/completedtodos.html', {'todos':todos, 'title':'TodoWoo', 'length':todos.__len__()})

@login_required
def viewtodo(request, todo_pk):
    todos = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance=todos)
        return render(request, 'todo/viewtodo.html', {'todos':todos, 'form':form, 'title':todos.title})
    else:
        try:
            form = TodoForm(request.POST, instance=todos)
            form.save()
            return redirect('currenttodos')

        except ValueError:
            return render(request, 'todo/viewtodo.html', {'form':TodoForm(), 'error':'Bad Info.', 'title':todos.title})

@login_required
def completetodo(request, todo_pk):
    todos = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todos.datecompleted = timezone.now()
        todos.save()
        return redirect('currenttodos')

@login_required
def deletetodo(request, todo_pk):
    todos = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        if todos.datecompleted != None:
            todos.delete()
            return redirect('completedtodos')
        else:
            todos.delete()
            return redirect('currenttodos')

@login_required
def renewtodo(request, todo_pk):
    todos = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        newtodo = Todo()
        newtodo.title = todos.title
        newtodo.memo = todos.memo
        newtodo.user = todos.user
        newtodo.important = todos.important
        newtodo.save()
        todos.delete()
        return redirect('completedtodos')
