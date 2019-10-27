from flask import Blueprint, render_template, flash, request, redirect, url_for
from flask_login import login_user, logout_user, login_required

from flaskr.forms import LoginForm
from flaskr.models import db, User

from flaskr.controllers.main_controller import main


# from flask.ext.admin import Admin
# from flask.ext.admin.contrib.sqla import ModelView
