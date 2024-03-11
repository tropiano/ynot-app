from django import forms
from mainapp.models.upload import Document
from django.core.validators import FileExtensionValidator


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ("document",)

    def clean(self):
        cleaned_data = super(DocumentForm, self).clean()
        file = cleaned_data.get("document")
        file_name = file.name
        if not "csv" in file_name:
            print("Non csv file")
            print(file_name)
            raise forms.ValidationError("Please upload a csv file")
