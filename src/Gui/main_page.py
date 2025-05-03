from nicegui import app, ui
from nicegui.events import KeyEventArguments
import asyncio

from src.Model.Gemini import Gemini

@ui.page("/main")
def main_page():

    gem = Gemini()
    
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


    
    

    async def handle_left():
        ui.add_head_html('<style>body {background: linear-gradient(135deg, #ffffff, #53ff40);}</style>')
        await move_panel('right')
        await asyncio.sleep(0.5)
        ui.add_head_html('<style>body {background: linear-gradient(135deg, #ffffff, #9c9a9a);}</style>')

    async def handle_right():
        ui.add_head_html('<style>body {background: linear-gradient(135deg, #ffffff, #ff0303);}</style>')
        await move_panel('left')
        await asyncio.sleep(0.5)
        ui.add_head_html('<style>body {background: linear-gradient(135deg, #ffffff, #9c9a9a);}</style>')

    async def handle_key(event: KeyEventArguments):
        if event.key == 'ArrowLeft':
            await handle_right()
        elif event.key == 'ArrowRight':
            await handle_left()

    keyboard = ui.keyboard(on_key=handle_key)

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
            ui.button(icon='thumb_down', on_click=handle_right).props('icon-color: #F44336;')  # Left-aligned button
            ui.button(icon='thumb_up', on_click=handle_left).props('icon-color: #4CAF50;')  # Right-aligned button



    def chat_input_submitted(value: str):
        chat_messages = []

        #update gem with the newest job description
        #gem.update_job_description(value)

        chat_input = value
        resp = gem.generate_content(chat_input)  # Generate response
        chat_messages.append(f"Gemini: {resp}")
        chat_label.text = "\n".join(chat_messages)  # Update the chat label

    # Define a toggle function for the chat drawer
    def toggle_chat_drawer():
        if (drawer.value):
            drawer.toggle()
        else:
            chat_drawer.toggle()

    # Replace the chat card with a drawer
    # Replace the chat card with a larger drawer
    with ui.drawer(side='right', value=False).props('id=chat-drawer').style('width: 500px; height: 100%;') as chat_drawer:
        # Chat Title
        with ui.row():
            ui.icon('chat', color='primary').classes('text-4xl')
            ui.label('Gemini Chat').classes('text-3xl')
        ui.space()
        # Chat Messages
        with ui.scroll_area().style('width: 100%; height: 500px; border: 1px solid #ccc; padding: 10px;'):
            chat_label = ui.label("Chat messages will appear here... Ask gemini anything about the provided job!").style("height:100%").classes('text-lg')  # Label to display messages
        ui.space()
        # Chat Input
        with ui.column().style('justify-content: space-between; width: 100%; padding: 10px;'):
            chat_input = ui.input(placeholder='Type your message here...').props('outlined').style('flex: 1; margin-right: 10px; width: 100%; height: 100%;')
            ui.button('Send', on_click=lambda: chat_input_submitted(chat_input.value)).props('icon-color: #4CAF50;').style('width: 100%; height: 100%;')
        # Add a button to toggle the chat drawer



    def toggle_sidebar():
            if chat_drawer.value:
                chat_drawer.toggle()
            else:
                drawer.toggle()
            
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
        ui.button('Open Chat', on_click=toggle_chat_drawer)

        ui.button('Liked Jobs', on_click=toggle_sidebar)

    with ui.drawer(side='right', value=False) as drawer:
        ui.menu_item('Menu item 1')
        ui.menu_item('Menu item 2')
        ui.menu_item('Menu item 3')


    