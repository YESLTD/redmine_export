import csv
import redmine
from django.shortcuts import render, redirect, HttpResponse, render_to_response, RequestContext
from django.views.generic.edit import View
import django.forms as forms
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

import redmine
from . import settings as s

REDMINE_OBJECT = redmine.Redmine(s.REDMINE_SETTINGS['server'], username=s.REDMINE_SETTINGS['username'],
                                 password=s.REDMINE_SETTINGS['password'])

try:
    OUTPUT_CSV = s.OUTPUT_CSV
except:
    OUTPUT_CSV = 'rm_report.csv'

# Create your views here.


class ExportForm(forms.Form):
    def __init__(self, *args, rm=REDMINE_OBJECT, **kwargs):
        super(ExportForm, self).__init__(*args, **kwargs)
        projects = rm.project.all()
        self.fields['project'].choices = [(p.identifier, p.name) for p in projects]
    project = forms.ChoiceField(label='Проект')
    status = forms.ChoiceField(label='Статус', choices=(('open', 'Открытые'), ('closed', 'Закрытые'),
                                                               ('*', 'Все')))


def get_data(f, *, project_id, status_id, rm=REDMINE_OBJECT):
    fieldnames = ['#',
                  'Проект',
                  'Трекер',
                  'Родительская задача',
                  'Статус',
                  'Приоритет',
                  'Тема',
                  'Автор',
                  'Назначена',
                  'Обновлено',
                  'Категория',
                  'Версия',
                  'Начата',
                  'Дата выполнения',
                  'Оценка времени',
                  'Затраченное время',
                  'Готовность',
                  'Создано',
                  'Закрыта',
                  'Связанные задачи',
                  'Состояние закрытия',
                  'Частная',
                  'Описание']

    mapping = {'#': 'id',
               'Проект': 'project',
               'Трекер': 'tracker',
               'Родительская задача': 'parent',
               'Статус': 'status',
               'Приоритет': 'priority',
               'Тема': 'subject',
               'Автор': 'author',
               'Назначена': 'assigned_to',
               'Обновлено': 'updated_on',
               'Категория': 'category',
               'Версия': 'fixed_version',
               'Начата': 'start_date',
               'Дата выполнения': 'due_date',
               'Оценка времени': 'estimated_hours',
               'Затраченное время': '',
               'Готовность': 'done_ratio',
               'Создано': 'created_on',
               'Закрыта': 'closed_on',
               'Связанные задачи': '',
               'Состояние закрытия': '',
               'Частная': 'is_private',
               'Описание': 'description'}

    writer = csv.DictWriter(f, fieldnames=fieldnames, restval='', extrasaction='raise', dialect='excel', delimiter=';')
    # Шапка
    headings = {}
    for heading in fieldnames:
        headings[heading] = heading
    writer.writerow(headings)
    # Данные
    for resource in rm.issue.filter(project_id=project_id, status_id=status_id): #'*'):
        row = {}
        # Атрибуты задачи
        issue = rm.issue.get(resource.id, include='attachments,journals,changesets')
        for fname, attrname in mapping.items():
            try:
                # print('{} - {} - {}'.format(fname, attrname, issue[attrname]))
                row[fname] = issue[attrname]
            except KeyError:
                # print('{} - {} - {}'.format(fname, attrname, ''))
                row[fname] = ''
            except redmine.exceptions.ResourceAttrError:
                # print('{} - {} - {}'.format(fname, attrname, ''))
                row[fname] = ''
        writer.writerow(row)

        # Примечания к задаче - переписка
        # Записывается в колонку "Описание"

        for journal in issue.journals:
            try:
                if journal.notes:
                    comment = {}
                    for key in row.keys():
                        if key == '#':
                            comment[key] = row[key]
                        else:
                            comment[key] = ''
                    comment['Тема'] = 'Примечание # {}'.format(journal['id'])
                    # print('User: {}'.format(journal['user']))
                    comment['Автор'] = journal['user']
                    # print('Created on: {}'.format(journal.created_on))
                    comment['Создано'] = journal['created_on']
                    # print(journal.notes)
                    comment['Описание'] = journal['notes']
                    writer.writerow(comment)
            except redmine.exceptions.ResourceAttrError:
                pass


@method_decorator(login_required, name='dispatch')
class ExportCsv(View):
    template = 'form.html'

    def get(self, request, *args, **kwargs):
        form = ExportForm()
        return render_to_response(template_name=self.template, context={'form': form},
                                  context_instance=RequestContext(request, {}
                                                                  .update(csrf(request))))

    def post(self, request, *args, **kwargs):
        form = ExportForm(request.POST)
        if form.is_valid():
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(OUTPUT_CSV)
            get_data(response, project_id=form.cleaned_data['project'], status_id=form.cleaned_data['status'])
            return response
