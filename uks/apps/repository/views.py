from django.shortcuts import render

from .models import Repository


# Create your views here.


def detail(request, id):
    repositories = request.user.siteuser.repositories.all()
    repository = Repository.objects.get(id=id)
    print(repository.name)
    context = {'repositories': repositories, 'repository': repository}
    return render(request, 'repoDetail.html', context)
