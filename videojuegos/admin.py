from django.contrib import admin

from .models import Videojuego


@admin.register(Videojuego)
class VideojuegoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'genero', 'plataforma', 'activo')
    search_fields = ('nombre', 'genero', 'plataforma')
    list_filter = ('activo', 'plataforma')
