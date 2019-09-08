import os

from celery import current_app

from django import forms
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from thumbnailer.tasks import make_thumbnails


class FileUploadForm(forms.Form):
    """Class for the file upload form"""

    image_file = forms.ImageField(required=True)


class HomeView(View):
    """Main home view on get will render main home.html file and post will handle uploading image form"""
    def get(self, request):
        """Get request will return home.html template"""

        form = FileUploadForm()
        return render(request, 'thumbnailer/home.html', {'form': form})

    def post(self, request):
        """Post method will accept image upload form with possible image."""

        form = FileUploadForm(request.POST, request.FILES)
        context = {}

        if form.is_valid():
            file_path = os.path.join(settings.IMAGES_DIR,
                                     request.FILES['image_file'].name)

            with open(file_path, 'wb+') as fp:
                for chunk in request.FILES['image_file']:
                    fp.write(chunk)

            task = make_thumbnails.delay(file_path, thumbnails=[(128, 128)])

            context['task_id'] = task.id
            context['task_status'] = task.status

            return render(request, 'thumbnailer/home.html', context)

        context['form'] = form

        return render(request, 'thumbnailer/home.html', context)


class TaskView(View):
    """Used to check status of task, when completed return task completion details with image URL"""
    def get(self, request, task_id):
        """Accepts the task_id and checks to see if image has been transformed to thumbnail and responds with answer"""

        task = current_app.AsyncResult(task_id)
        response_data = {'task_status': task.status, 'task_id': task.id}

        if task.status == 'SUCCESS':
            response_data['results'] = task.get()

        return JsonResponse(response_data)
