from rest_framework import status
from rest_framework.test import APITestCase

from .models import Jugador


class JugadorAPITest(APITestCase):
    def test_crear_y_filtrar_jugador(self):
        respuesta = self.client.post(
            '/api/jugadores/',
            {
                'nickname': 'poxel.ioo',
                'nombre': 'Leo Messi',
                'email': 'leo@gmail.com',
                'pais': 'Costa Rica',
                'nivel': 8,
                'activo': True,
            },
            format='json',
        )

        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Jugador.objects.count(), 1)

        respuesta = self.client.get('/api/jugadores/?pais=Costa%20Rica&activo=true')
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(respuesta.data), 1)
