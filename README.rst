=====================================
PirateLearner Blogging App
=====================================

A Simple Blogging App that enables you to:

- Create/Decide Layout of the post.
- Arrange them in hierarchy.
- Write taggeble blog articles.

Apart from these stand-alone features this app can be used as Django-CMS apps also providing various plugins e.g.:

- Latest Entries Plugin (with Various view options).
- Section Views Plugin.
- Contact Page Plugin.
- Filter Entries based of Tags.

**Requirements**

- `Python 2.7<https://www.python.org/>`_ .
- `Django 1.5.x or 1.6.x<https://www.djangoproject.com/>'_.
- `Reversion 1.7.x or 1.8.x<http://django-reversion.readthedocs.org/en/latest/>`_.
- `Taggit <https://django-taggit.readthedocs.org/en/latest/>'_.
- `Ckeditor 4.x<https://github.com/django-ckeditor/django-ckeditor>`_ .
- `Crispy Forms <http://django-crispy-forms.readthedocs.org/en/latest/>`_.
- `mptt 0.6.1 <http://django-mptt.github.io/django-mptt/>`_.
- `django_select2 <https://github.com/applegrew/django-select2>`_

**Installation**

Use pip for installing the app:

    `pip install pl_blogging`

or download zip file from github -`here<https://github.com/PirateLearner/blogging.git>`_

after installation, add blogging to your installed apps and also make sure that requirements are also installed -

      |  INSTALLED_APPS = (
      |  ...
      |  'reversion',
      |  'crispy_forms',
      |  'blogging',
      |  'taggit',
      |  'ckeditor',
      |  'django_select2',
      |  ...
      |  )

Also add blogging urls in your projects urls.py -

      |  urlpatterns = i18n_patterns('',
      |  ...
      |  url(r'^', include('blogging.urls',namespace='blogging')),
      |  ...
      |  )

after this just run ``python manage.py syncdb`` for creation of database tables.

**Usage**

Basic Usage of the Blogging App is creating blog entries and navigate among them. App has three core entities :

- Content Type.
- Blog Parent.
- Blog Entries.

The documentation may be found at `Read The Docs<http://blogging.readthedocs.org/en/latest/>'_    

