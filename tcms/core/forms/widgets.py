# -*- coding: utf-8 -*-
# 
# Nitrate is copyright 2010 Red Hat, Inc.
# 
# Nitrate is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version. This program is distributed in
# the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranties of TITLE, NON-INFRINGEMENT,
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# 
# The GPL text is available in the file COPYING that accompanies this
# distribution and at <http://www.gnu.org/licenses>.
# 
# Authors:
#   Xuqing Kuang <xkuang@redhat.com>

import datetime, time

from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import StrAndUnicode, force_unicode
from django.utils.safestring import mark_safe
from django.forms.util import flatatt

from django.utils.encoding import force_unicode
from django.conf import settings
from django.utils.safestring import mark_safe
from tcms.core.lib.djangotinymce.tinymce.widgets import TinyMCE

SECONDS_PER_MIN = 60
SECONDS_PER_HOUR = 3600 #SECONDS_PER_MIN * 60
SECONDS_PER_DAY = 86400 #SECONDS_PER_HOUR * 24

class TimedeltaWidget(forms.Widget):
    INPUTS=['days', 'hours', 'minutes', 'seconds']
    MULTIPLY=[SECONDS_PER_DAY, SECONDS_PER_HOUR, SECONDS_PER_MIN, 1]
    
    ESTIMATED_DAYS_CHOICE = [(x, x) for x in range(0, 10)]
    ESTIMATED_HOURS_CHOICE = [(x, x) for x in range(0, 24)]
    ESTIMATED_MINUTES_CHOICE = [(x, x) for x in range(0, 60)]
    ESTIMATED_SECONDS_CHOICE = [(x, x) for x in range(0, 60)]
    
    def __init__(self, attrs=None):
        self.widgets=[]
        if not attrs:
            attrs={}
        inputs=attrs.get('inputs', self.INPUTS)
        multiply=[]
        for input in inputs:
            assert input in self.INPUTS, (input, self.INPUT)
            self.widgets.append(forms.Select(attrs=attrs, choices=getattr(self, 'ESTIMATED_' + input.upper() + '_CHOICE')))
            multiply.append(self.MULTIPLY[self.INPUTS.index(input)])
        self.inputs=inputs
        self.multiply=multiply
        super(TimedeltaWidget, self).__init__(attrs)
    
    def render(self, name, value, attrs):
        if value is None:
            values=[0 for i in self.inputs]
        elif isinstance(value, datetime.timedelta):
            values=split_seconds(value.days*SECONDS_PER_DAY+value.seconds, self.inputs, self.multiply)
        elif isinstance(value, int):
            # initial data from model
            values=split_seconds(value, self.inputs, self.multiply)
        else:
            assert isinstance(value, tuple), (value, type(value))
            assert len(value)==len(self.inputs), (value, self.inputs)
            values=value
        id=attrs.pop('id')
        assert not attrs, attrs
        rendered=[]
        for input, widget, val in zip(self.inputs, self.widgets, values):
            rendered.append(u'%s %s' % (widget.render('%s_%s' % (name, input), val), _(input)))
        return mark_safe('<div id="%s">%s</div>' % (id, ' '.join(rendered)))
    
    def value_from_datadict(self, data, files, name):
        # Don't throw ValidationError here, just return a tuple of strings.
        ret=[]
        for input, multi in zip(self.inputs, self.multiply):
            ret.append(data.get('%s_%s' % (name, input), 0))
        return tuple(ret)
    
    def _has_changed(self, initial_value, data_value):
        # data_value comes from value_from_datadict(): A tuple of strings.
        assert isinstance(initial_value, datetime.timedelta), initial_value
        initial=tuple([unicode(i) for i in split_seconds(initial_value.days*SECONDS_PER_DAY+initial_value.seconds, self.inputs, self.multiply)])
        assert len(initial)==len(data_value)
        #assert False, (initial, data_value)
        return bool(initial!=data_value)

def split_seconds(secs, inputs=TimedeltaWidget.INPUTS, multiply=TimedeltaWidget.MULTIPLY):
    ret=[]
    for input, multi in zip(inputs, multiply):
        count, secs = divmod(secs, multi)
        ret.append(count)
    return ret

TinyMCEWidget = TinyMCE(mce_attrs = {
    'mode': "textareas",
    'theme': "advanced",
    'language': "en",
    'skin': "o2k7",
    #'skin': "grappelli",
    'browsers': "gecko",
    'dialog_type': "modal",
    'object_resizing': 'true',
    'cleanup_on_startup': 'true',
    'forced_root_block': "p",
    'remove_trailing_nbsp': 'true',
    'theme_advanced_toolbar_location': "top",
    'theme_advanced_toolbar_align': "left",
    'theme_advanced_statusbar_location': "none",
    'theme_advanced_buttons1': "formatselect,bold,italic,underline,bullist,numlist,link,unlink,image,search,|,outdent,indent,hr,fullscreen,|,help",
    'theme_advanced_buttons2':"tablecontrols",
    'theme_advanced_buttons3':"",
    #'theme_advanced_buttons1': 'formatselect,styleselect,|,bold,italic,underline,|,bullist,numlist,blockquote,|,undo,redo,|,link,unlink,|,image,|,fullscreen,|,grappelli_adv',
    #'theme_advanced_buttons2': 'search,|,pasteword,template,media,charmap,|,code,|,table,cleanup,grappelli_documentstructure',
    #'theme_advanced_buttons3': '',
    'theme_advanced_path': 'false',
    'theme_advanced_blockformats': "p,h2,h3,h4,div,code,pre",
    'theme_advanced_styles': "[all] clearfix=clearfix;[p] summary=summary;[div] code=code;[img] img_left=img_left;[img] img_left_nospacetop=img_left_nospacetop;[img] img_right=img_right;[img] img_right_nospacetop=img_right_nospacetop;[img] img_block=img_block;[img] img_block_nospacetop=img_block_nospacetop;[div] column span-2=column span-2;[div] column span-4=column span-4;[div] column span-8=column span-8",
    'height': '300',
    'width': '100%',
    'urlconverter_callback' : 'myCustomURLConverter',
    #'content_css' : '/media/style/base.css',
    'plugins': "table,safari,advimage,advlink,fullscreen,visualchars,paste,media,template,searchreplace,emotions,linkautodetect",
    'table_styles' : "Header 1=header1;Header 2=header2;Header 3=header3",
    'table_cell_styles' : "Header 1=header1;Header 2=header2;Header 3=header3;Table Cell=tableCel1",
    'table_row_styles' : "Header 1=header1;Header 2=header2;Header 3=header3;Table Row=tableRow1",
})
