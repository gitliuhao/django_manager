import os
from PIL import Image
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


@csrf_exempt
@require_http_methods(['POST'])
def upload(request):
    upload_type = request.GET.get("upload_type")
    if upload_type in ['wangEditor', 'editormd']:
        path = "media/django_manager/{}/img".format(upload_type.lower())
        files = request.FILES
        uploadimg = files.get('editormd-image-file') or files.get('uploadFile')
        if not uploadimg:
            return HttpResponse('erorr')
        file_name = uploadimg.name
        file_url = '%s/%s' % (path, file_name)
        isExists = os.path.exists(path)
        if not isExists:
            os.makedirs(path)
        img = Image.open(uploadimg.file)
        img.save(file_url)
        http_url = "http://{}/{}".format(request.get_host(), file_url)
        if upload_type == "editormd":
            return JsonResponse({'success': 1, "url": http_url})
        return HttpResponse(http_url)
    return HttpResponse('')
