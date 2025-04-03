import time
import unittest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db import connection, reset_queries
from django.conf import settings
from users.models import Employee, Admin, SystemAdmin, Technician
from tickets.models import Ticket, Category, Comment, TicketHistory, Report

class PruebasRendimiento(TestCase):
    def setUp(self):
        # Configuración inicial para medir consultas a la base de datos
        settings.DEBUG = True
        self.client = Client()
        
        # Crear usuarios de prueba
        self.usuario = get_user_model().objects.create_user(
            username='usuario_test',
            password='contraseña123',
            email='test@test.com',
            role='CLIENT'
        )
        
        self.tecnico = get_user_model().objects.create_user(
            username='tecnico_test',
            password='contraseña123',
            role='TECHNICIAN'
        )
        Technician.objects.create(user=self.tecnico)
        
        # Crear categoría de prueba
        self.categoria = Category.objects.create(name='Test', priority='MEDIUM')
        
    def medir_tiempo(self, funcion, *args, **kwargs):
        """Mide el tiempo de ejecución de una función"""
        inicio = time.time()
        resultado = funcion(*args, **kwargs)
        fin = time.time()
        return resultado, fin - inicio
    
    def medir_consultas_db(self, funcion, *args, **kwargs):
        """Mide el número de consultas a la base de datos y su tiempo"""
        reset_queries()
        inicio = time.time()
        resultado = funcion(*args, **kwargs)
        fin = time.time()
        num_consultas = len(connection.queries)
        tiempo_total_db = sum(float(q['time']) for q in connection.queries)
        return resultado, {
            'tiempo_total': fin - inicio,
            'num_consultas': num_consultas,
            'tiempo_db': tiempo_total_db
        }
    
    def test_autenticacion(self):
        """Prueba el rendimiento de la autenticación"""
        print('\n=== Prueba de Rendimiento: Autenticación ===')
        
        def login():
            return self.client.login(username='usuario_test', password='contraseña123')
        
        resultado, metricas = self.medir_consultas_db(login)
        print(f"Tiempo total de login: {metricas['tiempo_total']:.4f} segundos")
        print(f"Número de consultas DB: {metricas['num_consultas']}")
        print(f"Tiempo en DB: {metricas['tiempo_db']:.4f} segundos")
    
    def test_creacion_ticket(self):
        """Prueba el rendimiento de la creación de tickets"""
        print('\n=== Prueba de Rendimiento: Creación de Ticket ===')
        self.client.login(username='usuario_test', password='contraseña123')
        
        def crear_ticket():
            return Ticket.objects.create(
                title='Ticket de prueba',
                description='Descripción de prueba',
                category=self.categoria,
                created_by=self.usuario
            )
        
        resultado, metricas = self.medir_consultas_db(crear_ticket)
        print(f"Tiempo total de creación: {metricas['tiempo_total']:.4f} segundos")
        print(f"Número de consultas DB: {metricas['num_consultas']}")
        print(f"Tiempo en DB: {metricas['tiempo_db']:.4f} segundos")
    
    def test_listado_tickets(self):
        """Prueba el rendimiento del listado de tickets"""
        print('\n=== Prueba de Rendimiento: Listado de Tickets ===')
        self.client.login(username='usuario_test', password='contraseña123')
        
        # Crear varios tickets para la prueba
        for i in range(10):
            Ticket.objects.create(
                title=f'Ticket {i}',
                description=f'Descripción {i}',
                category=self.categoria,
                created_by=self.usuario
            )
        
        def obtener_tickets():
            return Ticket.objects.all().select_related('category', 'created_by')
        
        resultado, metricas = self.medir_consultas_db(obtener_tickets)
        print(f"Tiempo total de listado: {metricas['tiempo_total']:.4f} segundos")
        print(f"Número de consultas DB: {metricas['num_consultas']}")
        print(f"Tiempo en DB: {metricas['tiempo_db']:.4f} segundos")
    
    def test_actualizacion_ticket(self):
        """Prueba el rendimiento de la actualización de tickets"""
        print('\n=== Prueba de Rendimiento: Actualización de Ticket ===')
        ticket = Ticket.objects.create(
            title='Ticket para actualizar',
            description='Descripción inicial',
            category=self.categoria,
            created_by=self.usuario
        )
        
        def actualizar_ticket():
            ticket.status = 'IN_PROGRESS'
            ticket.save()
            TicketHistory.objects.create(
                ticket=ticket,
                changed_by=self.tecnico,
                old_status='OPEN',
                new_status='IN_PROGRESS',
                changed_at=ticket.updated_at
            )
        
        resultado, metricas = self.medir_consultas_db(actualizar_ticket)
        print(f"Tiempo total de actualización: {metricas['tiempo_total']:.4f} segundos")
        print(f"Número de consultas DB: {metricas['num_consultas']}")
        print(f"Tiempo en DB: {metricas['tiempo_db']:.4f} segundos")
    
    def test_comentarios(self):
        """Prueba el rendimiento de la gestión de comentarios"""
        print('\n=== Prueba de Rendimiento: Gestión de Comentarios ===')
        ticket = Ticket.objects.create(
            title='Ticket con comentarios',
            description='Descripción',
            category=self.categoria,
            created_by=self.usuario
        )
        
        def crear_comentario():
            return Comment.objects.create(
                ticket=ticket,
                user=self.usuario,
                content='Comentario de prueba'
            )
        
        resultado, metricas = self.medir_consultas_db(crear_comentario)
        print(f"Tiempo total de creación de comentario: {metricas['tiempo_total']:.4f} segundos")
        print(f"Número de consultas DB: {metricas['num_consultas']}")
        print(f"Tiempo en DB: {metricas['tiempo_db']:.4f} segundos")
    
    def test_generacion_reportes(self):
        """Prueba el rendimiento de la generación de reportes"""
        print('\n=== Prueba de Rendimiento: Generación de Reportes ===')
        
        # Crear algunos tickets de prueba con diferentes estados y fechas
        for i in range(5):
            ticket = Ticket.objects.create(
                title=f'Ticket {i}',
                description=f'Descripción {i}',
                category=self.categoria,
                created_by=self.usuario,
                status='CLOSED' if i < 3 else 'OPEN'
            )
        
        def crear_reporte():
            return Report.objects.create(
                generated_by=self.usuario,
                report_type='RESOLUTION_TIME',
                data={
                    'total_tickets': 5,
                    'tickets_cerrados': 3,
                    'tickets_abiertos': 2,
                    'tiempo_promedio_resolucion': '48 horas',
                    'distribucion_estados': {
                        'OPEN': 2,
                        'CLOSED': 3
                    }
                }
            )
        
        resultado, metricas = self.medir_consultas_db(crear_reporte)
        print(f"Tiempo total de generación de reporte: {metricas['tiempo_total']:.4f} segundos")
        print(f"Número de consultas DB: {metricas['num_consultas']}")
        print(f"Tiempo en DB: {metricas['tiempo_db']:.4f} segundos")

if __name__ == '__main__':
    unittest.main()