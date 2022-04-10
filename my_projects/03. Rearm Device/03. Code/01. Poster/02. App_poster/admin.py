from django.contrib import admin

from .models import Poster


class PosterInLine(admin.TabularInline):
    model = Poster
