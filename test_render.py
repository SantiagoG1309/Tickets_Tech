import requests
import time
import unittest
from datetime import datetime
import json

class PruebasRendimientoRender(unittest.TestCase):
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.base_url = "https://tickets-tech.onrender.com"
        self.session = requests.Session()
        
        # Credenciales de prueba
        self.credentials = {
            'username': 'Kevin',
            'password': 'julianpan123'
        }
        
    def medir_tiempo_respuesta(self, metodo, url, **kwargs):
        """Mide el tiempo de respuesta de una petición HTTP"""
        inicio = time.time()
        try:
            respuesta = metodo(url, **kwargs)
            tiempo = time.time() - inicio
            return {
                'tiempo': tiempo,
                'status_code': respuesta.status_code,
                'content_length': len(respuesta.content) if respuesta.content else 0,
                'headers': dict(respuesta.headers)
            }
        except requests.RequestException as e:
            return {
                'tiempo': time.time() - inicio,
                'error': str(e),
                'status_code': None
            }

    def guardar_resultados(self, nombre_prueba, resultados):
        """Guarda los resultados de las pruebas en un archivo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f'resultados_render_{timestamp}.json', 'a') as f:
            json.dump({
                'prueba': nombre_prueba,
                'timestamp': timestamp,
                'resultados': resultados
            }, f, indent=2)
            f.write('\n')

    def test_01_disponibilidad_sitio(self):
        """Verifica que el sitio esté disponible"""
        print("\n=== Prueba de Disponibilidad del Sitio ===")
        resultado = self.medir_tiempo_respuesta(self.session.get, self.base_url)
        
        print(f"Tiempo de respuesta: {resultado['tiempo']:.4f} segundos")
        print(f"Código de estado: {resultado['status_code']}")
        
        self.guardar_resultados('disponibilidad_sitio', resultado)
        self.assertIsNotNone(resultado['status_code'])
        self.assertEqual(resultado['status_code'], 200)

    def test_02_autenticacion(self):
        """Prueba el rendimiento de la autenticación"""
        print("\n=== Prueba de Autenticación ===")
        url = f"{self.base_url}/users/login/"  # Fixed URL path
        
        # Get CSRF token from the login page
        csrf_response = self.session.get(url)
        csrf_token = csrf_response.cookies.get('csrftoken')
        
        self.credentials.update({
            'csrfmiddlewaretoken': csrf_token,
        })
        
        headers = {
            'X-CSRFToken': csrf_token,
            'Referer': url
        }
        
        resultado = self.medir_tiempo_respuesta(
            self.session.post,
            url,
            data=self.credentials,
            headers=headers,
            allow_redirects=True
        )
        
        print(f"Tiempo de autenticación: {resultado['tiempo']:.4f} segundos")
        print(f"Código de estado: {resultado['status_code']}")
        
        self.guardar_resultados('autenticacion', resultado)
        self.assertTrue(resultado['status_code'] in [200, 302])

    def test_05_creacion_ticket(self):
        """Prueba la creación de un ticket"""
        print("\n=== Prueba de Creación de Ticket ===")
        url = f"{self.base_url}/tickets/new/"
        
        # Get CSRF token
        csrf_response = self.session.get(url)
        csrf_token = csrf_response.cookies.get('csrftoken')
        
        datos_ticket = {
            'title': 'Ticket de prueba rendimiento',
            'description': 'Descripción de prueba de rendimiento',
            'category': '1',
            'priority': 'MEDIUM',
            'csrfmiddlewaretoken': csrf_token
        }
        
        headers = {
            'X-CSRFToken': csrf_token,
            'Referer': url
        }
        
        resultado = self.medir_tiempo_respuesta(
            self.session.post,
            url,
            data=datos_ticket,
            headers=headers,
            allow_redirects=True
        )
        
        print(f"Tiempo de creación: {resultado['tiempo']:.4f} segundos")
        print(f"Código de estado: {resultado['status_code']}")
        
        self.guardar_resultados('creacion_ticket', resultado)
        self.assertTrue(resultado['status_code'] in [200, 302])

    def test_03_carga_dashboard(self):
        """Prueba el tiempo de carga del dashboard"""
        print("\n=== Prueba de Carga del Dashboard ===")
        url = f"{self.base_url}/dashboard/"
        
        resultado = self.medir_tiempo_respuesta(self.session.get, url)
        
        print(f"Tiempo de carga: {resultado['tiempo']:.4f} segundos")
        print(f"Código de estado: {resultado['status_code']}")
        
        self.guardar_resultados('carga_dashboard', resultado)
        self.assertEqual(resultado['status_code'], 200)

    def test_04_listado_tickets(self):
        """Prueba el rendimiento del listado de tickets"""
        print("\n=== Prueba de Listado de Tickets ===")
        url = f"{self.base_url}/tickets/"
        
        resultado = self.medir_tiempo_respuesta(self.session.get, url)
        
        print(f"Tiempo de carga: {resultado['tiempo']:.4f} segundos")
        print(f"Código de estado: {resultado['status_code']}")
        
        self.guardar_resultados('listado_tickets', resultado)
        self.assertEqual(resultado['status_code'], 200)

    def test_06_tiempo_carga_imagenes(self):
        """Prueba el tiempo de carga de recursos estáticos"""
        print("\n=== Prueba de Carga de Recursos Estáticos ===")
        urls_estaticas = [
            '/static/css/main.css',
            '/static/js/main.js',
            # Añade más URLs de recursos estáticos según sea necesario
        ]
        
        resultados = []
        for url in urls_estaticas:
            resultado = self.medir_tiempo_respuesta(
                self.session.get,
                f"{self.base_url}{url}"
            )
            resultados.append({
                'url': url,
                'tiempo': resultado['tiempo'],
                'status_code': resultado['status_code']
            })
            print(f"Recurso {url}:")
            print(f"  Tiempo de carga: {resultado['tiempo']:.4f} segundos")
            print(f"  Código de estado: {resultado['status_code']}")
        
        self.guardar_resultados('carga_recursos_estaticos', resultados)

    def tearDown(self):
        """Limpieza después de las pruebas"""
        self.session.close()

if __name__ == '__main__':
    unittest.main(verbosity=2)