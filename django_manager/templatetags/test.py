from django.forms import BoundField
from django.template import Library

register = Library()

@register.simple_tag
def get_editormd_id(form, name):
    try:
        str_id = form._meta.widgets[name].attrs.get('id')
        if "wang_editor" in str_id:
            return ""
        return str_id
    except KeyError:
        return ""


@register.simple_tag
def test1(name):
    print(name, 'xxxxxxxxxxxx')
    return name