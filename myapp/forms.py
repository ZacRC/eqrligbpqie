from django import forms
from .models import ForumPost, ForumReply
from django import forms
from .models import Listing

class ForumPostForm(forms.ModelForm):
    class Meta:
        model = ForumPost
        fields = ['title', 'content', 'category']

class ForumReplyForm(forms.ModelForm):
    class Meta:
        model = ForumReply
        fields = ['content']

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'platform', 'followers', 'niche', 'price', 'tiktok_shop', 'creative_fund', 'youtube_monetization', 'escrow_type', 'escrow_details']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'escrow_details': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tiktok_shop'].widget = forms.CheckboxInput()
        self.fields['creative_fund'].widget = forms.CheckboxInput()
        self.fields['youtube_monetization'].widget = forms.CheckboxInput()
        self.fields['escrow_type'].widget = forms.RadioSelect(choices=[('locked', 'Locked'), ('unlocked', 'Unlocked')])

class ListingEditForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }