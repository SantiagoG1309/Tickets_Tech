from django import forms
from .models import Ticket, Comment

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'category', 'priority']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }
        labels = {
            'description': 'Descripción',
            'category': 'Categoría',
            'priority': 'Prioridad',
            'title': 'Título',
        }
class TicketUpdateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['status']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Añadir un comentario...'}),
        }
        labels = {
            'content': '',
        }