from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['just_title'] = 'Страница об авторе'
        context['just_text'] = 'Коротко о себе'
        return context


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['just_title'] = 'Страница о технологиях'
        context['just_text'] = 'Не судите строго'
        return context
