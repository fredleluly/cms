from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import re
from apps.media.widgets import MediaLibraryWidget

class ContactForm(forms.Form):
    name = forms.CharField(
        validators=[
            RegexValidator(
                regex=r'^[\w\s-]+$',
                message='Name can only contain letters, numbers, spaces and hyphens'
            )
        ]
    )
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)
    honeypot = forms.CharField(required=False)  # Spam trap
    
    def clean_message(self):
        message = self.cleaned_data['message']
        # Block kata-kata spam umum
        spam_words = ['judi', 'poker', 'casino', 'slot', 'gacor', 'togel']
        
        if any(word in message.lower() for word in spam_words):
            raise ValidationError("Message contains prohibited content")
            
        # Cek link mencurigakan
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message)
        if len(urls) > 2:  # Batasi jumlah link
            raise ValidationError("Too many links in message")
            
        return message
        
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('honeypot'):  # Jika honeypot terisi, berarti bot
            raise ValidationError("Bot detected")
        return cleaned_data 

class ArticleForm(forms.ModelForm):
    featured_image = forms.CharField(widget=MediaLibraryWidget)
    
    class Meta:
        model = Article
        fields = ['title', 'content', 'featured_image'] 