from django import forms


class LotteryTicketCsvImportForm(forms.Form):
    csv_file = forms.FileField(
        label='CSV file',
        help_text='Required columns: draw_date, number, bundle_size, quantity, price.',
    )
