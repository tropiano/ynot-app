from django import forms
from mainapp.models.upload import Document
from django.forms import ClearableFileInput
from django.core.validators import FileExtensionValidator


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class DocumentForm(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    class Meta:
        model = Document
        fields = ("document",)

    def clean(self, data, initial=None):
        single_file_clean = super(DocumentForm, self).clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
            csv_val = ["csv" in r.name for r in result]
            if not all(csv_val):
                raise forms.ValidationError("Please upload only csv files")
        else:
            result = [single_file_clean(data, initial)]
            csv_file = "csv" in result.name
            if not csv_file:
                raise forms.ValidationError("Please upload only csv files")
        return result


class FileFieldForm(forms.Form):
    file_field = DocumentForm()
