# -*- encoding: utf-8 -*-
"""
Copyright (c) 2024 - present Wilson635
"""

from apps.members import blueprint
from flask import render_template, redirect, url_for


@blueprint.route('/support-members')
def route_default():
    return render_template('./home/support.html')
