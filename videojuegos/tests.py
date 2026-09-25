from rest_framework import status
from rest_framework.test import APITestCase

from .models import Videojuego


class UltimoVideojuegoTest(APITestCase):
    def test_guarda_el_ultimo_videojuego_consultado_en_sesion(self):
        videojuego = Videojuego.objects.create(
            nombre='Clash Royale',
            genero='Estrategia',
            plataforma='Mobile',
        )

        detalle = self.client.get(f'/api/videojuegos/{videojuego.id}/')
        ultimo = self.client.get('/api/videojuegos/ultimo-visitado/')

        self.assertEqual(detalle.status_code, status.HTTP_200_OK)
        self.assertEqual(ultimo.status_code, status.HTTP_200_OK)
        self.assertEqual(ultimo.data['id'], videojuego.id)
