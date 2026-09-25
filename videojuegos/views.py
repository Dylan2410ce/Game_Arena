from django.db.models.deletion import ProtectedError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Videojuego
from .serializers import VideoJuegoSerializer


@api_view(['GET', 'POST'])
def videojuegos_api(request):
    if request.method == 'GET':
        videojuegos = Videojuego.objects.filter(activo=True).order_by('nombre')

        plataforma = request.GET.get('plataforma')
        if plataforma:
            videojuegos = videojuegos.filter(plataforma__iexact=plataforma)

        serializer = VideoJuegoSerializer(videojuegos, many=True)
        return Response(serializer.data)

    serializer = VideoJuegoSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def videojuego_detalle_api(request, id):
    try:
        videojuego = Videojuego.objects.get(pk=id)
    except Videojuego.DoesNotExist:
        return Response(
            {'error': 'Videojuego no encontrado'},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == 'GET':
        request.session['ultimo_videojuego'] = videojuego.id

        serializer = VideoJuegoSerializer(videojuego)
        return Response(serializer.data)

    if request.method in ['PUT', 'PATCH']:
        serializer = VideoJuegoSerializer(
            videojuego,
            data=request.data,
            partial=(request.method == 'PATCH'),
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        videojuego.delete()
    except ProtectedError:
        return Response(
            {'error': 'No se puede eliminar un videojuego con torneos asociados'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def ultimo_videojuego_api(request):
    videojuego_id = request.session.get('ultimo_videojuego')

    if not videojuego_id:
        return Response({'ultimo_videojuego': None})

    try:
        videojuego = Videojuego.objects.get(pk=videojuego_id)
    except Videojuego.DoesNotExist:
        return Response({'ultimo_videojuego': None})

    return Response({
        'id': videojuego.id,
        'nombre': videojuego.nombre,
    })
