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

- [Python](https://www.python.org/) - 2.7.
- [Django](https://www.djangoproject.com/) - 1.5.x or 1.6.x.
- [Reversion](http://django-reversion.readthedocs.org/en/latest/) - 1.7.x or 1.8.x.
- [Taggit](https://django-taggit.readthedocs.org/en/latest/) - latest version.
- [Ckeditor](https://github.com/django-ckeditor/django-ckeditor)- 4.x.
- [Crispy Forms](http://django-crispy-forms.readthedocs.org/en/latest/) - latest version.
- [mptt](http://django-mptt.github.io/django-mptt/) - (0, 6, 1).
- [django_select2](https://github.com/applegrew/django-select2)

**Installation**

Use pip for installing the app:

    `pip install pirate_blogging`

or download zip file from github - [here]_ 

.. _[here]:https://github.com/PirateLearner/blogging.git

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

## Usage

Basic Usage of the Blogging App is creating blog entries and navigate among them. App has three core entities :

- Content Type.
- Blog Parent.
- Blog Entries.

The documentation may be found at `Read The Docs`_

.. _'Read the Docs':(http://blogging.readthedocs.org/en/latest/)    

