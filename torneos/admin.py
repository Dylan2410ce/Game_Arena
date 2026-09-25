from django.contrib import admin

from .models import Inscripcion, Torneo


@admin.register(Torneo)
class TorneoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'videojuego', 'fecha_inicio', 'cupo_maximo', 'estado')
    search_fields = ('nombre',)
    list_filter = ('estado', 'activo', 'videojuego')


@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ('torneo', 'jugador', 'estado', 'fecha_inscripcion')
    list_filter = ('estado',)
