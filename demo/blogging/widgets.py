#widgets.py
from django import forms
from django.template.loader import render_to_string

class SelectWithPopUp(forms.Select):
    model = None

    def __init__(self, model=None):
        self.model = model
        super(SelectWithPopUp, self).__init__()

    def render(self, name, *args, **kwargs):
        html = super(SelectWithPopUp, self).render(name, *args, **kwargs)

        if not self.model:
            self.model = name

        popupplus = render_to_string("blogging/formpopup.html", {'field': name, 'model': self.model})
        return html+popupplus
