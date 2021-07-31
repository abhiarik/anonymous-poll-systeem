from flask import Blueprint
from flask import render_template, request, redirect, url_for, g

from . import db

bp = Blueprint("form", "form", url_prefix="/form")
