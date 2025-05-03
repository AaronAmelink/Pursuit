from nicegui import app, ui
from nicegui.events import KeyEventArguments
import asyncio


@ui.page("/main")
def main_page():
    ui.add_head_html('''
        <style>
            body {background: linear-gradient(135deg, #ffffff, #9c9a9a);}
            .swipe-card {
                position: absolute;
                left: 50%;
                top: 50%;
                transform: translate(-50%, -50%);
                width: 480px;
                height: 700px;
                transition: transform 0.5s ease-in-out, opacity 0.5s ease-in-out;
            }
        </style>
    ''')

    async def on_up():
        ui.add_head_html('<style>body {background: linear-gradient(135deg, #ffffff, #53ff40);}</style>')
        await move_panel('right')
        await asyncio.sleep(0.5)
        ui.add_head_html('<style>body {background: linear-gradient(135deg, #ffffff, #9c9a9a);}</style>')

    async def on_down():
        ui.add_head_html('<style>body {background: linear-gradient(135deg, #ffffff, #ff0303);}</style>')
        await move_panel('left')
        await asyncio.sleep(0.5)
        ui.add_head_html('<style>body {background: linear-gradient(135deg, #ffffff, #9c9a9a);}</style>')

    async def move_panel(direction):
        if direction == 'left':
            ui.run_javascript(f"""
                const panel = document.getElementById('swipe-card');
                panel.style.transform = 'translate(calc(-50% - 500px), -50%) rotate(-30deg)';
                panel.style.opacity = '0';
                
                setTimeout(() => {{
                    panel.style.transition = 'none';
                    panel.style.transform = 'translate(-50%, -50%)';
                    panel.style.opacity = '1';
                    setTimeout(() => {{ panel.style.transition = 'transform 0.5s ease-in-out, opacity 0.5s ease-in-out'; }}, 10);
                }}, 500);
            """)
        elif direction == 'right':
            ui.run_javascript(f"""
                const panel = document.getElementById('swipe-card');
                panel.style.transform = 'translate(calc(-50% + 500px), -50%) rotate(30deg)';
                panel.style.opacity = '0';
                
                setTimeout(() => {{
                    panel.style.transition = 'none';
                    panel.style.transform = 'translate(-50%, -50%)';
                    panel.style.opacity = '1';
                    setTimeout(() => {{ panel.style.transition = 'transform 0.5s ease-in-out, opacity 0.5s ease-in-out'; }}, 10);
                }}, 500);
            """)
            

    with ui.card().classes('swipe-card').props('id=swipe-card'):
        # Title
        with ui.row():
            ui.icon('work', color='primary').classes('text-4xl')
            ui.label('Title').classes('text-3xl')
        ui.space() 
        # Description
        with ui.row():
            ui.icon('description', color='primary').classes('text-4xl')
            ui.label('Description\n').classes('text-3xl')
            with ui.scroll_area().style('width: 460px; height: 200px;'):
                ui.label('...\n' * 400)
        ui.space() 
        # Company
        with ui.row():
            ui.icon('factory', color='primary').classes('text-4xl')
            ui.label('Company').classes('text-3xl')
        ui.space()  
        # Location
        with ui.row():
            ui.icon('emoji_transportation', color='primary').classes('text-4xl')
            ui.label('Location').classes('text-3xl')
        ui.space() 
    
    buttons = ui.card().style(
        'position: absolute; bottom: 0; left: 50%; transform: translateX(-50%); width: 550px; height: 100px; background: none; box-shadow: none; border: none;'
    )
    with buttons:
        with ui.row().style('justify-content: space-between; width: 100%; padding: 0 20px;'):
            ui.button(icon='thumb_down', on_click=on_down).props('icon-color: #F44336;')  # Left-aligned button
            ui.button(icon='thumb_up', on_click=on_up).props('icon-color: #4CAF50;')  # Right-aligned button
            
    with ui.row().classes('w-full border items-center justify-between').style('background: none; box-shadow: none; border: none;'): 
        with ui.button(icon='menu'):
            with ui.menu() as menu:
                ui.menu_item('Sign out', on_click=lambda: ui.navigate.to('/'))
                ui.menu_item('Reset', lambda: ui.run_javascript("""
                    const panel = document.getElementById('swipe-card');
                    panel.style.transition = 'none';
                    panel.style.transform = 'translate(-50%, -50%)';
                    panel.style.opacity = '1';
                    setTimeout(() => { panel.style.transition = 'transform 0.5s ease-in-out, opacity 0.5s ease-in-out'; }, 10);
                """))
                ui.menu_item('Exit', on_click=lambda: (ui.run_javascript("window.location.href = 'about:blank';"), app.shutdown()))
                ui.separator()
                ui.menu_item('Close', menu.close)
        ui.image('./src/Gui/icons/logo.png').style('width: 90px; height: 30px;')

        ui.space()

        with ui.button('Liked Jobs'):
            with ui.menu() as menu:
                ui.menu_item('Menu item 1')
                ui.menu_item('Menu item 2')
                ui.menu_item('Menu item 3')
                ui.separator()
                ui.menu_item('Close', menu.close)