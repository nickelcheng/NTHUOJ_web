'''
    The MIT License (MIT)
    Copyright (c) 2014 NTHUOJ team
    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:
    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
    '''

from django import forms
from django.db.models import Q
from group.models import Group, Announce
from users.models import User

class GroupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        # access object through self.instance...
        self.fields['coowner'].queryset = User.objects.exclude(user_level=User.USER)
        self.fields['owner'].queryset = User.objects.exclude(user_level=User.USER)

    class Meta:
        model = Group
        fields = [
            'gname',
            'owner',
            'coowner',
            'member',
            'description',
            'trace_contest',
        ]

class GroupFormEdit(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(GroupFormEdit, self).__init__(*args, **kwargs)
        # access object through self.instance...
        self.fields['coowner'].queryset = User.objects.exclude(user_level=User.USER)
        #self.fields['member'].queryset = User.objects.exclude(self.fields['coowner'].queryset)
    class Meta:
        model = Group
        fields = [
            'gname',
            'coowner',
            'member',
            'description',
            'trace_contest',
        ]

class Co_GroupFormEdit(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(Co_GroupFormEdit, self).__init__(*args, **kwargs)
        # access object through self.instance...
        self.fields['coowner'].queryset = User.objects.exclude(user_level=User.USER)
    class Meta:
        model = Group
        fields = [
            'member',
            'description',
            'trace_contest',
        ]

class AnnounceForm(forms.ModelForm):
    class Meta:
        model = Announce
        fields = [
            'title',
            'content',
        ]
        widgets = {
            'title': forms.TextInput(),
            'content': forms.Textarea(),
        }
