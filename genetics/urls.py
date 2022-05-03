#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import url

from genetics import api

urlpatterns = [
    url( r'^sequence_variant/$', api.sequence_variant, name='sequence_variant'),
    url( r'^transcripts/$', api.transcripts, name='transcripts'),
    url( r'^gene/$', api.gene, name='gene'),
]
