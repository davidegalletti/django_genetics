#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.urls import re_path

from genetics import api

urlpatterns = [
    re_path( r'^sequence_variant/$', api.sequence_variant, name='sequence_variant'),
    re_path( r'^transcripts/$', api.transcripts, name='transcripts'),
    re_path( r'^gene/$', api.gene, name='gene'),
]
