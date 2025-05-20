from django import template
from django.urls import resolve, Resolver404
from ..models import Menu

register = template.Library()


@register.simple_tag(takes_context=True)
def draw_menu(context, menu_name):
    request = context['request']
    current_path = request.path
    try:
        menu = Menu.objects.prefetch_related('items__children').get(name=menu_name)
    except Menu.DoesNotExist:
        return ''

    # Построение дерева пунктов меню
    items = menu.items.all()

    # Создадим словарь для быстрого доступа к пунктам по id
    item_dict = {item.id: item for item in items}

    # Построение дерева в виде вложенных структур
    tree = []

    # Создаем список детей для каждого пункта
    children_map = {}
    for item in items:
        parent_id = item.parent_id
        children_map.setdefault(parent_id, []).append(item)

    # Рекурсивная функция для построения дерева с учетом активных элементов
    def build_tree(parent_id=None):
        subtree = []
        for item in children_map.get(parent_id, []):
            node = {
                'item': item,
                'children': build_tree(item.id),
                'active': True,
                'expanded': True,
            }
            subtree.append(node)
        return subtree

    menu_tree = build_tree()

    # Определение активных пунктов и развернутых узлов
    def mark_active(node_list):
        active_found = False
        for node in node_list:
            item_url = node['item'].get_url()
            if item_url == current_path:
                node['active'] = True
                node['expanded'] = True
                active_found = True
            elif mark_active(node['children']):
                node['active'] = True ###
                node['expanded'] = True
                active_found = True
            print(node["item"].title)
        return active_found

    mark_active(menu_tree)

    # Функция для рендеринга дерева в HTML (используем Bootstrap или свои стили)
    def render_nodes(nodes):
        html = '<ul>'
        for node in nodes:
            classes = []
            if node['active']:
                classes.append('active')
            if node['children']:
                classes.append('expanded' if node['expanded'] else 'collapsed')
            class_attr = f' class="{" ".join(classes)}"' if classes else ''
            html += f'<li{class_attr}>'
            html += f'<a href="{node["item"].get_url()}">{node["item"].title}</a>'
            if node['children'] and node['expanded']:
                html += render_nodes(node['children'])
            html += '</li>'
        html += '</ul>'
        return html

    return render_nodes(menu_tree)