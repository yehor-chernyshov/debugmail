from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, get_object_or_404
from mongoengine import DoesNotExist, NotUniqueError, ValidationError
from mongoengine.django.auth import User
from django.contrib.auth import login, logout
from handy.decorators import render_to
from project.models import Project
from debugmail.settings import PROJECT_PASSWORD_SALT
import hashlib


@render_to('project/project-list.html')
@login_required
def project_list(request):
    return {
        'projects': Project.objects.filter(user=request.user),
        'user': request.user
    }


@login_required
def add_project(request):
    return project_process(request, Project(), False)


@login_required
def edit_project(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
        if project.user != request.user:
            return Http404()
        return project_process(request, project, True)
    except DoesNotExist:
        return project_process(request, Project(), False)


@render_to('project/project-form.html')
def project_process(request, project, is_update):
    if request.method == 'POST':
        project_title = request.POST.get('title', '')
        try:
            project.title = project_title
            project.user = request.user
            project.save()
            if not is_update:
                m = hashlib.md5()
                m.update(PROJECT_PASSWORD_SALT + str(project.id))
                project.password = str(m.hexdigest())
                project.save()
            return redirect('edit_project', project_id=str(project.id))
        except ValidationError, e:
            return {
                'error': str(e),
                'title': project_title,
                'is_update': is_update,
                'project': project
            }
    else:
        return {
            'title': project.title if project.title else '',
            'is_update': is_update,
            'project': project
        }


@render_to('project/show_project.html')
@login_required()
def show_project(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
    except DoesNotExist:
        return Http404()
    if project.user != request.user:
        return Http404()
    return {
        'project': project
    }


@login_required()
def remove_project(request, project_id):
    try:
        project = Project.objects.get(id=project_id)
    except DoesNotExist:
        return Http404()
    if project.user != request.user:
        return Http404()
    project.delete()
    return redirect('project_list')