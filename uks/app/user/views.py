from django.shortcuts import render, redirect
from app.repository.forms import RepositoryForm
from django.contrib import messages
from app.repository.models import Repository


# Create your views here.
def dashboard(request):
    repositories = request.user.siteuser.repositories.all()
    context = {'repositories': repositories}
    return render(request, 'user/dashboard.html', context)


def profile(request):
    return render(request, 'user/profile.html')


def addRepository(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        form = RepositoryForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            print('Forma je validna')
            # form.save()
            repositories = request.user.siteuser.repositories.add(form.save())
            messages.success(request, 'Successfully')
            return redirect('dashboard')
        else:
            print('Forma nije validna')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = RepositoryForm()

    return render(request, 'user/dashboard.html', {'form': form})


def detail(request, id):
    repositories = request.user.siteuser.repositories.all()
    repository = Repository.objects.get(id=id)
    print(repository.name)
    context = {'repositories': repositories, 'repository': repository}
    return render(request, 'repoDetail.html', context)
