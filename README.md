# django-manager

#### 项目介绍
django admin管理工具，适用于慵懒者。admin默认的动态注册所有表。默认给它添加了一些基础属性，display_list, list_filter, search_list, actions, verbose_name_list。 并对ForeignKey, OnToOneField, ImagField等字段进行了处理以及优化。自带excel数据导出，而且还支持在admin使用富文本编辑器。

### 环境
Pyhton3

#### 使用说明

1. 引入django_manager包。

2. 根目录settings.py加app:
```
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_manager',
    'myapp',
]
```
3. 在任意app的admin.py执行以下代码:
```
from django_admin import admin as adm

adm.registers()
```

#### admin使用富文本编辑器
1. 根目录url.py文件添加url:
```
from django.conf.urls import url, include
from django.contrib import admin
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^django_manager/', include('django_manager.urls', namespace='django_manager')),
]
```
2. 任意app的admin.py添加一下代码:
```
from django_manager import admin as adm
wang_editor_fields = ("my_wang_editor_field",)  // 添加表中采用富文本编辑器的字段名
adm.registers(wang_editor_fields)

```

