from nicegui import app, ui
from nicegui.events import KeyEventArguments
import asyncio
from asyncio import Lock

from src.Model.Gemini import Gemini

from src.Gui.app import app

COUNTER = 0

@ui.page("/main")
def main_page():
    ui.page_title('Pursuit - Swipe into something better!')

        

    gem = Gemini()
    jc = app.jobs
    jc._load_model()
    

    # -------------------- CSS: Gradient, Flashes, Animations --------------------

    ui.add_head_html('''
        <style>
            body {
                margin: 0;
                background: linear-gradient(-45deg, #d7d2cc, #fcbad3, #a1c4fd, #c2b280, #e0c3fc);
                background-size: 600% 600%;
                animation: gradientMove 10s ease infinite;
                overflow-x: hidden;
            }

            @keyframes gradientMove {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }

            #flash-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                pointer-events: none;
                z-index: 9999;
                opacity: 0;
                transition: opacity 0.6s ease;
            }

            #flash-overlay.flash-green {
                background-color: rgba(0, 255, 100, 0.6);
            }

            #flash-overlay.flash-red {
                background-color: rgba(255, 0, 0, 0.6);
            }

            .fade-scale {
                opacity: 0;
                transform: scale(0.8);
                transition: transform 0.6s ease, opacity 0.6s ease;
            }
            .fade-scale.animate {
                opacity: 1;
                transform: scale(1);
            }

            .slide-up {
                opacity: 0;
                transform: translateY(30px);
                transition: transform 0.6s ease, opacity 0.6s ease;
            }
            .slide-up.animate {
                opacity: 1;
                transform: translateY(0);
            }

            .slide-down {
                opacity: 0;
                transform: translateY(-30px);
                transition: transform 0.6s ease, opacity 0.6s ease;
            }
            .slide-down.animate {
                opacity: 1;
                transform: translateY(0);
            }

            .bounce-in {
                opacity: 0;
                animation: bounceIn 0.8s ease-out forwards;
            }

            @keyframes bounceIn {
                0%   { transform: scale(0.3); opacity: 0; }
                50%  { transform: scale(1.05); opacity: 1; }
                70%  { transform: scale(0.95); }
                100% { transform: scale(1); }
            }
        </style>
    ''')

# -------------------- HTML Overlay for Color Flashes --------------------
    ui.add_body_html('''
        <div id="flash-overlay"></div>
    ''')

    # -------------------- Trigger Animations on Load --------------------
    ui.run_javascript('''
        setTimeout(() => document.getElementById('top-bar')?.classList.add('animate'), 100);
        setTimeout(() => document.getElementById('logo')?.classList.add('bounce-in'), 300);
        setTimeout(() => document.getElementById('swipe-card')?.classList.add('animate'), 500);
        setTimeout(() => document.getElementById('action-buttons')?.classList.add('animate'), 700);
    ''')

    # -------------------- Flash & Swipe Handlers --------------------
    async def handle_left():
        ui.run_javascript('''
            const overlay = document.getElementById('flash-overlay');
            overlay.className = 'flash-green';
            overlay.style.opacity = '1';
            setTimeout(() => overlay.style.opacity = '0', 600);
        ''')

    async def handle_right():
        ui.run_javascript('''
            const overlay = document.getElementById('flash-overlay');
            overlay.className = 'flash-red';
            overlay.style.opacity = '1';
            setTimeout(() => overlay.style.opacity = '0', 600);
        ''')

    key_handling_lock = Lock()
    async def handle_key(event: KeyEventArguments):
        global COUNTER
        async with key_handling_lock:  # Ensure only one key event is processed at a time
            COUNTER += 1

            if COUNTER == 2:
                jc.record_like(
                    event.key == 'ArrowRight',
                    jc.model.current_job.job_title,
                    jc.model.current_job.job_employer,
                    jc.model.current_job.job_location,
                    jc.model.current_job.job_url
                )
                COUNTER = 0
                if event.key == 'ArrowLeft':
                    new_job_task = asyncio.create_task(asyncio.to_thread(jc.get_job))
                    await handle_right()
                    await move_panel('left', new_job_task)
                elif event.key == 'ArrowRight':
                    new_job_task = asyncio.create_task(asyncio.to_thread(jc.get_job))
                    await handle_left()
                    await move_panel('right', new_job_task)

    async def handle_left_button():
        async with key_handling_lock:  # Ensure only one key event is processed at a time
                jc.record_like(
                    False,
                    jc.model.current_job.job_title,
                    jc.model.current_job.job_employer,
                    jc.model.current_job.job_location,
                    jc.model.current_job.job_url
                )
                new_job_task = asyncio.create_task(asyncio.to_thread(jc.get_job))
                await handle_right()
                await move_panel('left', new_job_task)

    async def handle_right_button():
        async with key_handling_lock:
            jc.record_like(
                True,
                jc.model.current_job.job_title,
                jc.model.current_job.job_employer,
                jc.model.current_job.job_location,
                jc.model.current_job.job_url
            )
            new_job_task = asyncio.create_task(asyncio.to_thread(jc.get_job))
            await handle_left()
            await move_panel('right', new_job_task)


    ui.keyboard(on_key=handle_key)

    async def move_panel(direction, new_job_task=None):
        try:
            # Set animation parameters
            offset = '+ 500px' if direction == 'right' else '- 500px'
            rotate = '30deg' if direction == 'right' else '-30deg'

            # Trigger swipe animation
            await ui.run_javascript(f"""
                const panel = document.getElementById('swipe-card');
                // Start animation
                panel.style.transform = 'translate(calc(-50% {offset}), -50%) rotate({rotate})';
                panel.style.opacity = '0';
            """)

            # Record the swipe action while animation is happening


            # Get new job data while animation runs (parallel operation)

            # Wait for animation to visually complete
            await asyncio.sleep(0.5)

            # Reset panel position (instantly)
            await ui.run_javascript("""
                const panel = document.getElementById('swipe-card');
                panel.style.transition = 'none';
                panel.style.transform = 'translate(-50%, -50%) scale(1)';
                panel.style.opacity = '0';  // Start hidden
                // Restore transition after a frame
                requestAnimationFrame(() => {
                    panel.style.transition = 'transform 0.5s ease, opacity 0.5s ease';
                    panel.style.opacity = '1';
                });
            """)

            # Wait for new job data to be ready
            new_job = await new_job_task
            
            # Update UI with new job data
            unwrap_job(new_job)
            gem.update_job_description(new_job.job_description)

        except Exception as e:
            print(f"Error in move_panel: {e}")
            # Fallback reset if something went wrong
            await ui.run_javascript("""
                const panel = document.getElementById('swipe-card');
                panel.style.transition = 'transform 0.5s ease, opacity 0.5s ease';
                panel.style.transform = 'translate(-50%, -50%) scale(1)';
                panel.style.opacity = '1';
            """)

    def open_chat():
        if (liked_drawer.value):
            liked_drawer.toggle()
        else:
            chat_drawer.toggle()
    def open_liked_jobs():
        if (chat_drawer.value):
            chat_drawer.toggle()
        else:
            load_liked_jobs()
            liked_drawer.toggle()
            

    # -------------------- Top Navigation Bar --------------------
    with ui.row().classes('w-full border items-center justify-between slide-down').props('id=top-bar').style('border: none;'):
        with ui.button(icon='menu'):
            with ui.menu() as menu:
                ui.menu_item('Sign out', on_click=lambda: ui.navigate.to('/'))
                ui.menu_item('Exit', on_click=lambda: (ui.run_javascript("window.location.href = 'about:blank';"), app.shutdown()))
        ui.image('./src/Gui/icons/logo.png').props('id=logo').style('width: 90px; height: 30px;')
        ui.space()
        ui.button('Open Chat', on_click=open_chat)
        ui.button('Liked Jobs', on_click=open_liked_jobs)

    


    # -------------------- Main Swipe Card --------------------
    with ui.card().props('id=swipe-card').style('position: absolute; left: 50%; top: 45%; transform: translate(-50%, -50%); width: 480px; height: 600px; border-radius: 40px; background-color: white; box-shadow: 0 10px 25px rgba(0,0,0,0.2);'):
        with ui.row():
            ui.icon('work', color='primary').classes('text-4xl')
            title = ui.label('Title').classes('text-3xl')
        ui.space()
        with ui.row():
            ui.icon('description', color='primary').classes('text-4xl')
            ui.label('Description\n').classes('text-3xl')
            with ui.scroll_area().style('width: 460px; height: 200px;'):
                description = ui.label('...\n' * 400)
        ui.space()
        with ui.row():
            ui.icon('factory', color='primary').classes('text-4xl')
            company = ui.label('Company').classes('text-3xl')
        ui.space()
        with ui.row():
            ui.icon('emoji_transportation', color='primary').classes('text-4xl')
            location = ui.label('Location').classes('text-3xl')
        ui.space()

    def unwrap_job(job):
        title.text = job.job_title
        description.text = job.job_description
        company.text = job.job_employer
        location.text = job.job_location

    init_job = jc.get_job()
    unwrap_job(init_job)
    gem.update_job_description(init_job.job_description)
    
    # -------------------- Like/Dislike Buttons --------------------
    buttons = ui.card().classes('slide-up').props('id=action-buttons').style(
        'position: absolute; bottom: 30px; left: 50%; transform: translateX(-50%); '
        'width: 550px; height: 100px; background: none; box-shadow: none; border: none;'
    )
        

    with buttons:
        with ui.row().style('margin: 0 auto; justify-content: center; gap: 15vw;'):
            ui.button(icon='thumb_down', on_click=handle_left_button).props('color=red icon-color=white round size=xl')
            ui.button(icon='thumb_up', on_click=handle_right_button).props('color=green icon-color=white round size=xl')



    # -------------------- Liked Jobs Drawer --------------------
    with ui.drawer(side='right', value=False).props('id=liked-jobs-drawer').style('width: 500px; height: 100%;') as liked_drawer:
        # Header
        with ui.row():
            ui.icon('favorite', color='red').classes('text-4xl')
            ui.label('Liked Jobs').classes('text-3xl')
        ui.space()

        # Scrollable container with consistent-sized cards
        with ui.scroll_area().style('width: 100%; height: 500px; border: 1px solid #ccc; padding: 10px;'):
            liked_jobs_column = ui.column().style('gap: 10px;')

        ui.space()

        # Optional refresh button
        with ui.column().style('width: 100%; padding: 10px;'):
            ui.button('Refresh List', on_click=lambda: load_liked_jobs()).props('icon=refresh').style('width: 100%;')

    # -------------------- Function to Load Liked Jobs --------------------
    def load_liked_jobs():
        liked_jobs_column.clear()
        for job in jc.get_liked():
            with liked_jobs_column:
                with ui.card().style('padding: 10px; height: 20vh; width: 100%; box-sizing: border-box; display: flex; flex-direction: column; justify-content: space-between;'):
                    ui.label(f"🔹 {job['job_title']}").classes('text-xl font-bold')
                    ui.label(f"🏢 {job['job_employer']}").classes('text-md')
                    ui.label(f"📍 {job['job_location']}").classes('text-md')
                    ui.link('🔗 View Posting', job['job_url']).classes('text-blue-500 underline')


     # -------------------- Gemini Chat Drawer --------------------
    with ui.drawer(side='right', value=False).props('id=chat-drawer').style('width: 500px; height: 100%;') as chat_drawer:
        with ui.row():
            ui.icon('chat', color='primary').classes('text-4xl')
            ui.label('Gemini Chat').classes('text-3xl')
        ui.space()
        with ui.scroll_area().style('width: 100%; height: 500px; border: 1px solid #ccc; padding: 10px;'):
            chat_label = ui.label("Chat messages will appear here...").classes('text-lg')
        ui.space()
        with ui.column().style('width: 100%; padding: 10px;'):
            chat_input = ui.input(placeholder='Type your message...').props('outlined').style('width: 100%;')
            ui.button('Send', on_click=lambda: chat_label.set_text("Gemini:\n" + chat_input.value)).props('icon-color: #4CAF50;').style('width: 100%;')


    def chat_input_submitted(value: str):
        chat_messages = []

        #update gem with the newest job description
        #gem.update_job_description(value)

        chat_input = value
        resp = gem.generate_content(chat_input)  # Generate response
        chat_messages.append(f"Gemini: {resp}")
        chat_label.text = "\n".join(chat_messages)  # Update the chat label

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



    