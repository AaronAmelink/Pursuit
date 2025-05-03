from nicegui import app, ui
from nicegui.events import KeyEventArguments
import asyncio


@ui.page("/main")
def main_page():
    ui.add_head_html('<style>body {background: linear-gradient(135deg, #ffffff, #9c9a9a);}</style>')

    async def on_up():
        ui.add_head_html('<style>body {background: linear-gradient(135deg, #ffffff, #53ff40);}</style>')
        await asyncio.sleep(1)
        ui.add_head_html('<style>body {background: linear-gradient(135deg, #ffffff, #9c9a9a);}</style>')

    async def on_down():
        ui.add_head_html('<style>body {background: linear-gradient(135deg, #ffffff, #ff0303);}</style>')
        await asyncio.sleep(1)
        ui.add_head_html('<style>body {background: linear-gradient(135deg, #ffffff, #9c9a9a);}</style>')

    panel = ui.card().classes('absolute-center')
    with panel.style('width: 480px; height: 600px;'):
        #Title
        with ui.row():
            ui.icon('work', color='primary').classes('text-4xl')
            ui.label('Title').classes('text-3xl')
        ui.space() 
        #Description
        with ui.row():
            ui.icon('description', color='primary').classes('text-4xl')
            ui.label('Description\n').classes('text-3xl')
            with ui.scroll_area().style('width: 460px; height: 200px;'):
                ui.label('...\n' * 400)
        ui.space() 
        #Company
        with ui.row():
            ui.icon('factory', color='primary').classes('text-4xl')
            ui.label('Company').classes('text-3xl')
        ui.space()  
        #Location
        with ui.row():
            ui.icon('emoji_transportation', color='primary').classes('text-4xl')
            ui.label('Location').classes('text-3xl')
        ui.space() 
    
    buttons = ui.card().style('position: absolute; bottom: 0; left: 50%; transform: translateX(-50%); width: 600px; height: 100px; background: none; box-shadow: none; border: none;')
    with buttons: #Add arrow functionality too
        with ui.row():
            ui.button(icon = 'thumb_down', on_click=on_down)
            for i in range(27):
                ui.space()
            ui.button(icon = 'thumb_up', on_click=on_up).props('icon-color: #4CAF50;') 

    with ui.row().classes('w-full items-center justify-between'): 
        with ui.button(icon='menu'):
            with ui.menu() as menu:
                ui.menu_item('Sign out', on_click=lambda: ui.navigate.to('/'))
                ui.menu_item('Reset') #Get Nich to make a reset function
                ui.menu_item('Exit', on_click=lambda: (ui.run_javascript("window.location.href = 'about:blank';"), app.shutdown()))
                ui.separator()
                ui.menu_item('Close', menu.close)

        with ui.button('Liked Jobs'):
            with ui.menu() as menu:
                ui.menu_item('Menu item 1')
                ui.menu_item('Menu item 2')
                ui.menu_item('Menu item 3')
                ui.separator()
                ui.menu_item('Close', menu.close)

