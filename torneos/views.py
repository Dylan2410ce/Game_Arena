from django.db.models import Count, F, Q
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from jugadores.models import Jugador
from videojuegos.models import Videojuego

from .models import Inscripcion, Torneo
from .serializers import InscripcionSerializer, TorneoSerializer


@api_view(['GET', 'POST'])
def torneos_api(request):
    if request.method == 'GET':
        torneos = Torneo.objects.all().order_by('id')

        videojuego = request.GET.get('videojuego')
        if videojuego:
            torneos = torneos.filter(videojuego_id=videojuego)

        estado = request.GET.get('estado')
        if estado:
            torneos = torneos.filter(estado=estado.upper())

        con_espacios = request.GET.get('con_espacios')
        if con_espacios == 'true':
            torneos = torneos.annotate(
                participantes=Count(
                    'inscripciones',
                    filter=Q(inscripciones__estado='ACTIVA'),
                )
            ).filter(participantes__lt=F('cupo_maximo'))

        serializer = TorneoSerializer(torneos, many=True)
        return Response(serializer.data)

    if not request.user.is_authenticated:
        return Response(
            {'error': 'Debe autenticarse para crear torneos'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not request.user.is_staff:
        return Response(
            {'error': 'Solo un administrador puede crear torneos'},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = TorneoSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def torneo_detalle_api(request, pk):
    try:
        torneo = Torneo.objects.get(pk=pk)
    except Torneo.DoesNotExist:
        return Response(
            {'error': 'Torneo no encontrado'},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == 'GET':
        serializer = TorneoSerializer(torneo)
        return Response(serializer.data)

    if not request.user.is_authenticated:
        return Response(
            {'error': 'Debe autenticarse para modificar torneos'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not request.user.is_staff:
        return Response(
            {'error': 'Solo un administrador puede modificar torneos'},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.method in ['PUT', 'PATCH']:
        serializer = TorneoSerializer(
            torneo,
            data=request.data,
            partial=(request.method == 'PATCH'),
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    torneo.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def inscripciones_torneo_api(request, id):
    try:
        torneo = Torneo.objects.get(pk=id)
    except Torneo.DoesNotExist:
        return Response(
            {'error': 'Torneo no encontrado'},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == 'GET':
        inscripciones = torneo.inscripciones.all().order_by('fecha_inscripcion')
        serializer = InscripcionSerializer(inscripciones, many=True)
        return Response(serializer.data)

    if not request.user.is_authenticated:
        return Response(
            {'error': 'Debe autenticarse para inscribirse'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    datos = request.data.copy()
    datos['torneo'] = torneo.id
    serializer = InscripcionSerializer(data=datos)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def estadisticas_admin_api(request):
    videojuegos_activos = Videojuego.objects.filter(activo=True).count()
    jugadores_activos = Jugador.objects.filter(activo=True).count()
    torneos_abiertos = Torneo.objects.filter(estado='ABIERTO').count()
    inscripciones_activas = Inscripcion.objects.filter(estado='ACTIVA').count()

    torneo_destacado = Torneo.objects.annotate(
        participantes=Count(
            'inscripciones',
            filter=Q(inscripciones__estado='ACTIVA'),
        )
    ).order_by('-participantes', 'id').first()

    return Response({
        'videojuegos_activos': videojuegos_activos,
        'jugadores_activos': jugadores_activos,
        'torneos_abiertos': torneos_abiertos,
        'inscripciones_activas': inscripciones_activas,
        'torneo_con_mas_participantes': {
            'id': torneo_destacado.id,
            'nombre': torneo_destacado.nombre,
            'participantes': torneo_destacado.participantes,
        } if torneo_destacado else None,
    })
