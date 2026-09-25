from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from jugadores.models import Jugador
from videojuegos.models import Videojuego

from .models import Inscripcion
from .serializers import TorneoSerializer


class TorneoAPITest(APITestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(
            username='jugador_web',
            password='clave-segura-123',
        )
        self.administrador = User.objects.create_user(
            username='admin',
            password='clave-segura-123',
            is_staff=True,
        )
        self.videojuego = Videojuego.objects.create(
            nombre='Liga-Estelar',
            genero='Estrategia',
            plataforma='Mobile',
            activo=True,
        )
        self.jugador = Jugador.objects.create(
            nickname='nova',
            nombre='Nova',
            email='nova@gmail.com',
            pais='Alemania',
            nivel=10,
            activo=True,
        )
        self.torneo = self._crear_torneo()

    def _datos_torneo(self, **cambios):
        datos = {
            'nombre': 'Copa',
            'videojuego': self.videojuego.id,
            'fecha_inicio': '2026-10-10',
            'fecha_fin': '2026-10-10',
            'cupo_maximo': 2,
            'estado': 'ABIERTO',
            'premio': '5000.00',
            'activo': True,
        }
        datos.update(cambios)
        return datos

    def _crear_torneo(self, **cambios):
        datos = self._datos_torneo(**cambios)
        return self.videojuego.torneos.model.objects.create(
            nombre=datos['nombre'],
            videojuego=self.videojuego,
            fecha_inicio=datos['fecha_inicio'],
            fecha_fin=datos['fecha_fin'],
            cupo_maximo=datos['cupo_maximo'],
            estado=datos['estado'],
            premio=datos['premio'],
            activo=datos['activo'],
        )

    def test_torneo_con_cupo_menor_a_dos_es_invalido(self):
        serializer = TorneoSerializer(data=self._datos_torneo(cupo_maximo=1))

        self.assertFalse(serializer.is_valid())
        self.assertIn('cupo_maximo', serializer.errors)

    def test_torneo_con_fecha_final_anterior_es_invalido(self):
        serializer = TorneoSerializer(
            data=self._datos_torneo(
                fecha_inicio='2026-10-10',
                fecha_fin='2026-10-10',
            )
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('fecha_fin', serializer.errors)

    def test_no_permite_inscripcion_duplicada(self):
        self.client.force_authenticate(user=self.usuario)
        url = f'/api/torneos/{self.torneo.id}/inscripciones/'

        primera = self.client.post(url, {'jugador': self.jugador.id}, format='json')
        repetida = self.client.post(url, {'jugador': self.jugador.id}, format='json')

        self.assertEqual(primera.status_code, status.HTTP_201_CREATED)
        self.assertEqual(repetida.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_permite_superar_el_cupo_maximo(self):
        segundo = Jugador.objects.create(
            nickname='orion',
            nombre='Orion',
            email='orion@gmail.com',
            pais='Costa Rica',
        )
        tercero = Jugador.objects.create(
            nickname='luna',
            nombre='Luna',
            email='luna@gmail.com',
            pais='Costa Rica',
        )
        Inscripcion.objects.create(torneo=self.torneo, jugador=self.jugador)
        Inscripcion.objects.create(torneo=self.torneo, jugador=segundo)

        self.client.force_authenticate(user=self.usuario)
        respuesta = self.client.post(
            f'/api/torneos/{self.torneo.id}/inscripciones/',
            {'jugador': tercero.id},
            format='json',
        )

        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_anonimo_no_puede_inscribirse(self):
        respuesta = self.client.post(
            f'/api/torneos/{self.torneo.id}/inscripciones/',
            {'jugador': self.jugador.id},
            format='json',
        )

        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_usuario_regular_no_puede_ver_estadisticas(self):
        self.client.force_authenticate(user=self.usuario)
        respuesta = self.client.get('/api/admin/estadisticas/')

        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_administrador_puede_ver_estadisticas(self):
        self.client.force_authenticate(user=self.administrador)
        respuesta = self.client.get('/api/admin/estadisticas/')

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertIn('torneo_con_mas_participantes', respuesta.data)

    def test_torneo_inexistente_devuelve_404(self):
        respuesta = self.client.get('/api/torneos/99999/')

        self.assertEqual(respuesta.status_code, status.HTTP_404_NOT_FOUND)

    def test_filtro_combinado_de_torneos(self):
        respuesta = self.client.get(
            f'/api/torneos/?videojuego={self.videojuego.id}&estado=ABIERTO'
        )

        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(respuesta.data), 1)
