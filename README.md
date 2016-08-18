# redmine_export
A simple django app to get detailed report on tickets in Redmine.
Currently available in russian.

## Requirements
App tested with Redmine 2.5.2.
In order to get it working don't forget to swich on Redmine's REST web-service on Settings page, authentication tab.

Django Application tested on Python 3.5.2 + Django 1.9, but shoud work on Python 2.7.x and 3.3.x.

## Installation
1. Copy `rm_export` folder into any appropriate Django project with user auth installed.
2. Configure local application's settings.py as necessary.
3. In projects main settings.py:
  1. Update INSTALLED_APPS: 
  '''
  INSTALLED_APPS = [
    ...,
    'rm_export',
  ]
  '''
  2. Add an entry into project's root urlconf like this:
  '''
  ...
  from rm_export import views as rm_views
  ...
  urlpatterns = [
    ...,
    url('^rmexport/$', rm_views.ExportCsv.as_view()),
  ]
  '''
4. Restart your django web-project as appropriate.
