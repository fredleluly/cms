from django.forms import widgets

class MediaLibraryWidget(widgets.TextInput):
    template_name = 'media/widgets/media_library.html'
    
    class Media:
        css = {
            'all': ('css/media-widget.css',)
        }
        js = ('js/media-widget.js',) 