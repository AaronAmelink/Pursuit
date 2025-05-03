from nicegui import app, ui
from nicegui.events import KeyEventArguments

import main_page

@ui.page('/')
def first():
    ui.add_head_html('<style>body {background: linear-gradient(135deg, #ffffff, #9c9a9a);}</style>')
    

    

    def to_login():
        ui.navigate.to('/login')
    def to_singin():
        ui.navigate.to('/signin')

    with ui.column().classes('absolute-center'):
        ui.image('./src/Gui/icons/logo.png').style('width: 120vph; height: 40vph;')  # Increased size
        with ui.row().style('gap: 20px;'):  # Added spacing between buttons
            ui.button('Log in', on_click=to_login).style('font-size: 20px; padding: 15px 30px;')  # Increased button size
            ui.button('Sign in', on_click=to_singin).style('font-size: 20px; padding: 15px 30px;')  # Increased button size
    

@ui.page('/login')
def login():
    ui.add_head_html('<style>body {background: linear-gradient(135deg, #ffffff, #9c9a9a);}</style>')

    def check_login():
        #tbd
        ui.navigate.to('/main')
    
    with ui.card().classes('absolute-center'):
        ui.input('Username')
        ui.input('Password', password=True, password_toggle_button=True)
        ui.button('Log in', on_click=check_login)

@ui.page('/signin')
def signin():
    ui.add_head_html('<style>body {background: linear-gradient(135deg, #ffffff, #9c9a9a);}</style>')

    def check_signin():
        #tbd
        ui.navigate.to('/main')
    
    with ui.stepper().props('vertical').classes('w-full').style('width: 480px; height: 480px;').classes('absolute-center') as stepper:
        with ui.step('Title'):
            ui.label('Please enter prefered title:')
            ui.input('Title')
            with ui.stepper_navigation():
                ui.button('Next', on_click=stepper.next)
        with ui.step('Location'):
            ui.label('Please enter the location where you are looking:')
            ui.input('Location')
            with ui.stepper_navigation():
                ui.button('Next', on_click=stepper.next)
                ui.button('Back', on_click=stepper.previous).props('flat')

        with ui.step('Credentials'):
            ui.label('Please enter your future credentials')
            ui.input('Username')
            ui.input('Password', password=True, password_toggle_button=True)
            with ui.stepper_navigation():
                ui.button('Sign in', on_click=check_signin)
                ui.button('Back', on_click=stepper.previous).props('flat')

ui.run()