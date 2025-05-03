from nicegui import ui

import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))


import main_page

from src.Gui.app import app
# Add the root directory to the Python module search path

from src.Controller.UserController import UserController



@ui.page('/')
def first():
    ui.page_title('Pursuit - Swipe into something better!')
    ui.add_head_html('<style>body {background: linear-gradient(135deg, #ffffff, #9c9a9a);}</style>')
    

    def to_login():
        ui.navigate.to('/login')
    def to_singin():
        ui.navigate.to('/signup')

    with ui.column().classes('absolute-center'):
        ui.image('./src/Gui/icons/logo.png').style('width: 120vph; height: 40vph;')  # Increased size
        ui.label('"Swipe Into Something Better."').style('font-size: 20px; font-weight: bold; font-style: italic;')  # Increased font size
        with ui.row().style('gap: 20px;'):  # Added spacing between buttons
            ui.button('Log in', on_click=to_login).style('font-size: 20px; padding: 15px 30px;')  # Increased button size
            ui.button('Sign Up', on_click=to_singin).style('font-size: 20px; padding: 15px 30px;')  # Increased button size
    

@ui.page('/login')
def login():
    ui.page_title('Pursuit - Swipe into something better!')
    ui.add_head_html('<style>body {background: linear-gradient(135deg, #ffffff, #9c9a9a);}</style>')

    def check_login():
        check = app.auth.login(username.value, password.value)
        if check:
            ui.navigate.to('/main')
        else:
            ui.notify('Invalid username or password', color='red')
    
    with ui.card().classes('absolute-center'):
        username = ui.input('Username')
        password = ui.input('Password', password=True, password_toggle_button=True)
        ui.button('Log in', on_click=check_login)

@ui.page('/signup')
def signin():
    ui.page_title('Pursuit - Swipe into something better!')
    ui.add_head_html('<style>body {background: linear-gradient(135deg, #ffffff, #9c9a9a);}</style>')

    def check_signin():
        resp = app.auth.signup(username.value, password.value)
        if resp:
            app.auth.set_preferences(title.value, location.value)
            ui.navigate.to('/main')
        else:
            with ui.dialog() as dialogue, ui.card():
                ui.label("Username already exists or invalid input")
                ui.button('Close', on_click=dialogue.close)
                username.value = ''
                password.value = ''
    
    with ui.stepper().props('vertical').classes('w-full').style('width: 480px; height: 480px;').classes('absolute-center') as stepper:
        with ui.step('Title'):
            ui.label('Please enter prefered title:')
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