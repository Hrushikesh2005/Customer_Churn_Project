from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField()
from django import forms

#NEW PART
class UploadFileForm(forms.Form):
    file = forms.FileField(label='Select a CSV file')
    has_churn_column = forms.ChoiceField(choices=[('no', 'No'),('yes', 'Yes'), ], label="Does the dataset have a churn column?")
