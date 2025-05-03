from nicegui import ui
from nicegui.events import KeyEventArguments

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.Gui.app import app
from src.Controller.UserController import UserController


# -------------------- LANDING PAGE --------------------
@ui.page('/')
def first():
    ui.page_title('Pursuit - Swipe into something better!')
    ui.add_head_html('<style>body {background: linear-gradient(135deg, #ffffff, #9c9a9a);}</style>')

    def to_login():
        ui.navigate.to('/login')
    def to_singin():
        ui.navigate.to('/signin')

    with ui.column().classes('absolute-center shadow-lg rounded-2xl p-6').style('background-color: white;'):
        ui.image('./src/Gui/icons/logo.png').style('width: 120vph; height: 40vph;')
        ui.label('"Swipe Into Something Better."').style('font-size: 20px; font-weight: bold; font-style: italic;')
        with ui.row().style('gap: 20px;'):
            ui.button('Log in', on_click=to_login).style('font-size: 20px; padding: 15px 30px;')
            ui.button('Sign Up', on_click=to_singin).style('font-size: 20px; padding: 15px 30px;')


# -------------------- LOGIN PAGE --------------------
@ui.page('/login')
def login():
    ui.page_title('Pursuit - Swipe into something better!')
    ui.add_head_html('<style>body {background: linear-gradient(135deg, #ffffff, #9c9a9a);}</style>')

    def check_login():
        check = app.auth.login(username.value, password.value)
        if check:
            ui.navigate.to('/main')
        else:
            ui.notify('Incorrect username or password', color='negative')

    with ui.card().classes('absolute-center shadow-lg rounded-2xl p-6').style('background-color: white; width: 400px;'):
        username = ui.input('Username')
        password = ui.input('Password', password=True, password_toggle_button=True)
        ui.button('Log in', on_click=check_login)


# -------------------- SIGNUP PAGE --------------------
@ui.page('/signin')
def signin():
    ui.page_title('Pursuit - Swipe into something better!')
    ui.add_head_html('<style>body {background: linear-gradient(135deg, #ffffff, #9c9a9a);}</style>')

    def check_signin():
        resp = app.auth.signup(username.value, password.value)
        if resp:
            ui.navigate.to('/main')
            app.auth.set_preferences(title.value, location.value)
        else:
            ui.notify('Username in use', color='negative')

    with ui.stepper().props('vertical').classes('absolute-center shadow-lg rounded-2xl p-6').style('background-color: white; width: 480px; height: 480px;') as stepper:
        with ui.step('Title'):
            ui.label('Please enter preferred title:')
            title = ui.input('Title')
            with ui.stepper_navigation():
                ui.button('Next', on_click=stepper.next)
        with ui.step('Location'):
            ui.label('Please enter the location where you are looking:')
            location = ui.input('Location')
            with ui.stepper_navigation():
                ui.button('Next', on_click=stepper.next)
                ui.button('Back', on_click=stepper.previous).props('flat')
        with ui.step('Credentials'):
            ui.label('Please enter your future credentials')
            username = ui.input('Username')
            password = ui.input('Password', password=True, password_toggle_button=True)
            with ui.stepper_navigation():
                ui.button('Sign in', on_click=check_signin)
                ui.button('Back', on_click=stepper.previous).props('flat')


ui.run()
