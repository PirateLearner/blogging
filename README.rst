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

- `Python`_ 2.7.
- `Django`_ 1.5.x or 1.6.x.
- `Reversion`_ 1.7.x or 1.8.x.
- `Taggit`_ .
- `Ckeditor`_ 4.x.
- `Crispy Forms`_ .
- `mptt`_ 0.6.1.
- `django_select2`_

**Installation**

Use pip for installing the app:

    `pip install pi-blogging --pre`

or download zip file from github `here`_

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

The documentation may be found at `Read The Docs`_.

.. _Python: https://www.python.org/ 
.. _Django: https://www.djangoproject.com/
.. _Reversion: http://django-reversion.readthedocs.org/en/latest/
.. _Taggit: https://django-taggit.readthedocs.org/en/latest/
.. _Ckeditor: https://github.com/django-ckeditor/django-ckeditor/
.. _`Crispy Forms`:  http://django-crispy-forms.readthedocs.org/en/latest/
.. _mptt: http://django-mptt.github.io/django-mptt/
.. _django_select2: https://github.com/applegrew/django-select2
.. _here: https://github.com/PirateLearner/blogging/archive/master.zip
.. _`Read The Docs`: http://blogging.readthedocs.org/en/latest/ 
