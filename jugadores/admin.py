from django.contrib import admin

from .models import Jugador


@admin.register(Jugador)
class JugadorAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'nombre', 'email', 'pais', 'nivel', 'activo')
    search_fields = ('nickname', 'nombre', 'email')
    list_filter = ('activo', 'pais')
