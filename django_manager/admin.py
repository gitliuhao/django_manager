import collections
import logging

from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.helpers import AdminField
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.db.utils import ProgrammingError
from django.http import HttpResponse
from django.utils.html import format_html, _strip_once, html_safe, escapejs, strip_tags

from .excel import get_excel_io, map_objects_to_value

# 过滤列
filter_list = [
    'DateTimeField', 'BooleanField', 'per_type', 'com_type', 'payment',
    'type', 'state', 'sex',
    ]
# 排除列
exclude_list = ['ForeignKey', 'OneToOneField']

WANG_EDITOR_JS = ("/django_manager/js/jquery-3.2.1.min.js",
                  "/django_manager/wangeditor/js/wangEditor.min.js",
                 # "/django_manager/wangeditor/js/js.js"
                  )

WANG_EDITOR_CSS = {"all": ("/django_manager/wangeditor/css/wangEditor.min.css",)}


EDITOR_MD_JS = ("/django_manager/js/jquery-3.2.1.min.js",
                "/django_manager/editormd/editormd.js",
               # "/django_manager/editormd/js/js.js"
                )

EDITOR_MD_CSS = {"all": ("/django_manager/editormd/css/editormd.css",)}


def excel_write(modeladmin, request, queryset):
    response = HttpResponse(content_type='application/vnd.ms-excel')
    model = queryset[0].__class__
    file_name = '{}_list'.format(model.__name__.lower())
    disposition = 'attachment;filename={}.xls'.format(file_name)
    response['Content-Disposition'] = disposition
    fields = model._meta.fields
    head_list = [field.verbose_name for field in fields]
    value_list = list(map(map_objects_to_value(fields), queryset))
    response = get_excel_io(response=response, head_list=head_list,
                            body_2list=value_list)
    return response


excel_write.short_description = "Excel 导出数据"


def get_field_tag(model_class, field):
    def img_tag(model_self):
        value = getattr(model_self, field.name)
        if value:
            return format_html('<a href="{}" target="_blank" ><img src="{}" style="height:60px;width:60px" /></a>',
                           *(getattr(model_self, field.name).url,) * 2)

    def forekey_tag(model_self):
        obj = getattr(model_self, field.name)
        if obj:
            return format_html('<a href="/admin/{}/{}/{}/change" target="_blank" >{}</a>',
                               obj._meta.app_label,
                               obj.__class__.__name__.lower(),
                               obj.pk,
                               str(obj))

    def many_to_many_tag(model_self):
        objects = getattr(model_self, field.name).all()
        print(objects, 'xxxxxxxxxxxxxxxx')
        html = ''
        for obj in objects:
            html += '<a href="/admin/{}/{}/{}/change" target="_blank" >{}</a></br>' \
                .format(obj._meta.app_label,
                        obj.__class__.__name__.lower(),
                        obj.pk,
                        str(obj))
        return html


    def char_tag(model_self):
        values = strip_tags('{}'.format(getattr(model_self, field.name)))
        if len(values) < 300:
            return values
        return '%s......<a href="/admin/%s/%s/%s/change" >%s</a>' % (values[:300],
                                                                               model_self._meta.app_label,
                                                                               model_self.__class__.__name__.lower(),
                                                                               model_self.pk,
                                                                               "查看更多")

    def choices_tag(model_self):
        return getattr(model_self, "get_%s_display" % field.name)()

    field_type = field.__class__.__name__
    if field_type in ["ImageField", 'ForeignKey', 'OneToOneField', 'ManyToManyField',
                      'CharField', 'TextField',]:
        if field_type == "ImageField":
            tag = img_tag
        elif field_type in ['CharField', 'TextField']:
            tag = char_tag if not field.choices else choices_tag
        elif field_type == 'ManyToManyField':
            tag = many_to_many_tag
        else:
            tag = forekey_tag
        tag.short_description = field.verbose_name
        tag.allow_tags = True
        field_tag_name = "%s_tag" % field.name
        setattr(model_class, field_tag_name, tag)
        return field_tag_name
    return field.name


class RegisterModel(object):
    def __init__(self, content_type, css=None, js=None, wang_editor_fields=None, editor_md_fields=None):
        self.wang_editor_fields = wang_editor_fields if isinstance(wang_editor_fields, collections.Iterable
                                                              ) else ()
        self._js = js or ("/django_manager/js/jquery-3.2.1.min.js",)
        self._css = css or {}
        self.content_type = content_type
        self.model_class = content_type.model_class()
        self._meta = self.model_class._meta
        self.fields = self._meta.fields + self._meta.many_to_many
        self.app_name = content_type.model

        self.wang_editor_fields = wang_editor_fields if isinstance(wang_editor_fields, collections.Iterable) else ()
        self.editor_md_fields = editor_md_fields if isinstance(editor_md_fields, collections.Iterable) else ()
        self.change_form_template = None

    def get_dispaly_field(self, field):
        return get_field_tag(self.model_class, field)

    def get_search_field(self, field):
        type_name = field.__class__.__name__
        if type_name not in ['ForeignKey',
                             'OneToOneField',
                             'ManyToManyField',
                             'DateTimeField']:
            return field.name

    def get_filter_field(self, field):
        type_name = field.__class__.__name__
        if type_name not in ['ForeignKey', 'OneToOneField']:
            if type_name in filter_list or field.name in filter_list or getattr(field, 'choice', None):
                return field.name

    def get_verbose_name(self, field):
        if not self.get_filter_field(field):
            return field.model._meta.verbose_name

    def get_editormd(self):
        return EDITOR_MD_CSS, EDITOR_MD_JS

    def get_wang_editor(self):
        return WANG_EDITOR_CSS, WANG_EDITOR_JS

    def get_form(self):
        widgets = {}
        editor_md_fields, wang_editor_fields = [], []
        for field in self.fields:
            if field.name in self.wang_editor_fields or field.name in self.editor_md_fields:
                if field.name in self.editor_md_fields:
                    # attr_id = "%s_%s" % ('editor_md', field.name)
                    attrs={
                            'id': "%s_%s" % ('editor_md', field.name),
                           "style": "display:none;"
                    }
                    editor_md_fields.append(field.name)
                else:
                    # attr_id = "%s_%s" % ('wang_editor', field.name)
                    attrs={'id': "%s_%s" % ('wang_editor', field.name)}
                    wang_editor_fields.append(field.name)
                widgets[field.name] = forms.Textarea(attrs=attrs)
        self.editor_md_fields, self.wang_editor_fields = editor_md_fields, wang_editor_fields
        if not widgets:
            return forms.ModelForm
        self.change_form_template = "django_manager/admin/change_form.html"
        self.widgets = widgets
        class Meta:
            model = self.model_class
            fields = '__all__'
            # fields = [field.name for field in self.fields if field.editable]
            widgets = self.widgets
        new_form = type("New{}ModelForm".format(self.model_class.__class__.__name__),
                        (forms.ModelForm,),
                        {'Meta': Meta})
        return new_form

    def get_media(self):
        class Media:
            js= self._js
            css = self._css
        return Media

    def get_attr(self):
        list_display, search_fields, list_filter, verbose_name_list = [], [], [], []
        for field in self.fields:
            display_field = self.get_dispaly_field(field)
            if display_field:
                list_display.append(display_field)
            search_field = self.get_search_field(field)
            if search_field:
                search_fields.append(search_field)
            filter_field = self.get_filter_field(field)
            if filter_field:
                list_filter.append(filter_field)
            verbose_name = self.get_verbose_name(field)
            if verbose_name:
                verbose_name_list.append(verbose_name)
        actions = [excel_write]
        attr = {
            'list_display': list_display,
            'search_fields': search_fields,
            'list_filter': list_filter,
            'verbose_name_list': verbose_name_list,
            'actions': actions,
            'form': self.get_form(),
            'Media': self.get_media(),
        }

        attr['change_form_template'] = self.change_form_template

        attr['editor_md_fields'] = self.editor_md_fields
        attr['wang_editor_fields'] = self.wang_editor_fields
        attr['get_editormd_cj'] = self.get_editormd()
        attr['get_wang_editor_cj'] = self.get_wang_editor()
        return attr

    def _new_model_admin(self):
        attr = self.get_attr()
        attr['form'] = self.get_form()
        new = type('New' + self.model_class.__class__.__name__, (admin.ModelAdmin,), attr)
        return new

    def register(self):
        try:
            admin.register(self.model_class)(self._new_model_admin())
        except admin.sites.AlreadyRegistered:
            pass


def registers(wang_editor_fields=None, editor_md_fields=None, js=None, css=None):
    excludes = ['contenttype', 'group', 'permission', 'session', 'user', 'person']
    try:
        content_type_list = ContentType.objects.exclude(model__in=excludes)
        for content_type in content_type_list:
            RegisterModel(content_type, js=js, css=css, wang_editor_fields=wang_editor_fields, editor_md_fields=editor_md_fields).register()
        admin.site.site_header = getattr(settings, 'SITE_HEADE', admin.site.site_header)
        admin.site.site_title =  getattr(settings, 'SITE_TITLE', admin.site.site_title)
        admin.site.index_title = getattr(settings, 'INDEX_TITLE', admin.site.index_title)
    except ProgrammingError:
        pass


# registers()




