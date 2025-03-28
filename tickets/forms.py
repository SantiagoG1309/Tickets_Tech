from django import forms
from .models import Ticket, Comment, Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'priority']
        labels = {
            'name': 'Nombre',
            'priority': 'Prioridad'
        }

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'category']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }
        labels = {
            'description': 'Descripción',
            'category': 'Categoría',
            'title': 'Título',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
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