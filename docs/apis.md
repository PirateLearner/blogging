# APIs and Template tags

APIs and template tags are used for extending the functionality in the template and to change the post display.

## API

Following apis can be used in the templates specified in [templates section](../latest/templates/):

* get_title (returns the title of the object).
* get_summary (returns the summary of blog post or blog parent).
* get_absolute_url (returns the absolute url of the post).
* get_image_url (returns the url of image, if exist).
* get_parent (returns the parent of blog post or blog parent).

## Template Tags

Currently only the contact plugin can be used as a template tag to drop in a contact form where ever you want.
To use this, 

1. Load the template tags:

```python
    {% load blogging_tags %}
```

2. Call the template tag where required:

```python
  {% render_contact_form %}
```

We plan to provide template tags for most of the Django-CMS plugins for use in standalone projects.
