from django.shortcuts import render
from .templatetags.menu_tags import draw_menu
from menu.models import Menu

def menus(request):
    mas = Menu.objects.all()
    mas = list(mas)
    for i in range(len(mas)):
        mas[i] = str(mas[i])
    context = {
        # например, можно передать название меню или другие параметры
        'menu_name': mas,

    }
    return render(request, 'menu/menus.html', context)
