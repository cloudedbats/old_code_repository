#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Project: http://cloudedbats.org
# Copyright (c) 2016 Arnold Andreasson 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
from __future__ import unicode_literals

from django.conf.urls import url
from djangoapp_wurb_setup import views

urlpatterns = [
        url(r'^$', views.update_settings),
        url(r'^settings/', views.update_settings),
    ]
