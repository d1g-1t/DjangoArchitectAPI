"""
Views для статичных страниц.
"""

from django.views.generic import TemplateView


class AboutView(TemplateView):
    """Страница 'О проекте'."""
    template_name = 'pages/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'О проекте'
        return context


class RulesView(TemplateView):
    """Страница 'Правила'."""
    template_name = 'pages/rules.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Наши правила'
        return context
