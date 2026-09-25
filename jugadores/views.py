from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Jugador
from .serializers import JugadorSerializer


@api_view(['GET', 'POST'])
def jugadores_api(request):
    if request.method == 'GET':
        jugadores = Jugador.objects.filter(activo=True).order_by('nickname')

        pais = request.GET.get('pais')
        if pais:
            jugadores = jugadores.filter(pais__iexact=pais)

        activo = request.GET.get('activo')
        if activo == 'false':
            jugadores = Jugador.objects.filter(activo=False).order_by('nickname')

        buscar = request.GET.get('buscar')
        if buscar:
            jugadores = jugadores.filter(nickname__icontains=buscar)

        serializer = JugadorSerializer(jugadores, many=True)
        return Response(serializer.data)

    serializer = JugadorSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH'])
def jugador_detalle_api(request, pk):
    try:
        jugador = Jugador.objects.get(pk=pk)
    except Jugador.DoesNotExist:
        return Response(
            {'error': 'Jugador no encontrado'},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == 'GET':
        serializer = JugadorSerializer(jugador)
        return Response(serializer.data)

    serializer = JugadorSerializer(jugador, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def perfil_api(request):
    return Response({
        'id': request.user.id,
        'username': request.user.username,
        'email': request.user.email,
    })
