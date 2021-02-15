from django.db import models


class Commit(models.Model):
    url = models.URLField(verbose_name='URL to commit')
    sha = models.TextField()
    author = models.CharField(max_length=60)
    date = models.DateTimeField()
    message = models.TextField()
    parents = models.ManyToManyField('self', symmetrical=False)

    def __str__(self):
        return '{author} committed {hash} at {date}'.format(author=self.author, hash=self.sha, date=self.date)

    def get_absolute_url(self):
        from django.shortcuts import redirect
        return redirect(self.url)
