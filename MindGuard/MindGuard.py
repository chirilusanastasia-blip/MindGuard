import flet as ft
import asyncio

PRIMARY = "#5B5FE6"
SECONDARY = "#FF7E5F"
ACCENT = "#26C6A0"
BG = "#F8FAFF"
CARD_BG = "#FFFFFF"
TEXT_PRIMARY = "#1E2140"
TEXT_SECONDARY = "#374151"
HIGH_CONTRAST_BG = "#000000"
HIGH_CONTRAST_TEXT = "#FFFF00"
HIGH_CONTRAST_CARD = "#333333"


class AppState:
    def __init__(self):
        self.current_screen = "welcome"
        self.selected_needs = {"visual": False, "hearing": False, "mobility": False, "speech": False, "none": False}
        self.mood_message = ft.Text("", size=16, text_align="center")
        self.high_contrast = False
        # răspunsuri chestionar
        self.q_anxiety = ""
        self.q_judged = ""
        self.q_helped = ""
        self.q_manage = ""
        # exercițiu activ
        self.active_exercise = None
        self.exercise_phase = "inhale"
        self.exercise_remaining = 0
        self.exercise_cycles = 0
        self.exercise_running = False
        self.exercise_timer_task = None
        # forum posts
        self.posts = [
            {"user": "Alex", "text": "I tried the balloon breathing and it really helped me calm down!", "likes": 3,
             "liked": False},
            {"user": "Maria", "text": "Feeling anxious today. Anyone else?", "likes": 5, "liked": False},
            {"user": "David", "text": "Remember: you are not alone! 💙", "likes": 7, "liked": False},
        ]


state = AppState()


def get_colors():
    if state.high_contrast:
        return {
            "bg": HIGH_CONTRAST_BG,
            "card": HIGH_CONTRAST_CARD,
            "text_primary": HIGH_CONTRAST_TEXT,
            "text_secondary": HIGH_CONTRAST_TEXT,
            "primary": "#FFFF00",
            "secondary": "#FFFF00",
            "accent": "#FFFF00",
            "border": "#FFFF00"
        }
    else:
        return {
            "bg": BG,
            "card": CARD_BG,
            "text_primary": TEXT_PRIMARY,
            "text_secondary": TEXT_SECONDARY,
            "primary": PRIMARY,
            "secondary": SECONDARY,
            "accent": ACCENT,
            "border": "#E5E7EB"
        }


def main(page: ft.Page):
    page.title = "MindGuard"
    page.padding = 20
    page.bgcolor = BG
    page.window_width = 400
    page.window_height = 700
    page.scroll = ft.ScrollMode.ADAPTIVE

    def go_to(screen):
        if screen == "home" and state.current_screen == "active_exercise":
            if state.exercise_timer_task:
                state.exercise_timer_task.cancel()
                state.exercise_timer_task = None
            state.exercise_running = False
        state.current_screen = screen
        update_page()

    def back():
        if state.current_screen == "accessibility":
            state.current_screen = "welcome"
        elif state.current_screen == "questionnaire":
            state.current_screen = "accessibility"
        elif state.current_screen == "home":
            state.current_screen = "questionnaire"
        elif state.current_screen == "active_exercise":
            if state.exercise_timer_task:
                state.exercise_timer_task.cancel()
                state.exercise_timer_task = None
            state.exercise_running = False
            state.current_screen = "breathing"
        elif state.current_screen in ["breathing", "emotions", "sos", "expert", "progress", "about", "community"]:
            state.current_screen = "home"
        else:
            state.current_screen = "welcome"
        update_page()

    def toggle_need(key):
        if key == "none":
            for k in state.selected_needs:
                state.selected_needs[k] = False
            state.selected_needs["none"] = True
        else:
            state.selected_needs["none"] = False
            state.selected_needs[key] = not state.selected_needs[key]
        state.high_contrast = state.selected_needs.get("visual", False)
        update_page()

    def create_mood_row():
        moods = [
            (5, "😊", "#10B981", "Happy"),
            (4, "😌", ACCENT, "Calm"),
            (3, "😐", "#F59E0B", "Okay"),
            (2, "😟", SECONDARY, "Worried"),
            (1, "😢", "#EF4444", "Sad"),
        ]

        def on_mood(e, value, mood_name):
            messages = {
                5: "Wonderful! Keep spreading that positive energy! 🌟",
                4: "Great to hear you're feeling calm and peaceful! 😌",
                3: "That's perfectly okay! Every day is different. 💙",
                2: "It's brave to recognize when you're worried. You're not alone. 🤗",
                1: "Thank you for sharing. Sad feelings are valid and temporary. 💜"
            }
            state.mood_message.value = messages.get(value, "")
            page.update()

        return ft.Row([
            ft.Container(
                content=ft.Text(emoji, size=32),
                bgcolor=color,
                border_radius=30,
                padding=10,
                on_click=lambda e, v=val, n=name: on_mood(e, v, n),
            ) for val, emoji, color, name in moods
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=15)

    def create_action_grid():
        actions = [
            ("Breathe", "🫁", ACCENT, "breathing"),
            ("Learn", "🧠", PRIMARY, "emotions"),
            ("SOS Help", "🆘", "#EF4444", "sos"),
            ("My Progress", "📊", "#F59E0B", "progress"),
            ("Expert Connect", "👨‍⚕️", PRIMARY, "expert"),
            ("About", "ℹ️", "#6B7280", "about"),
            ("Community", "💬", ACCENT, "community"),
        ]
        grid = ft.GridView(runs_count=2, max_extent=150, spacing=12, run_spacing=12, child_aspect_ratio=1.0)
        for title, emoji, color, screen in actions:
            grid.controls.append(
                ft.Container(
                    content=ft.Column([ft.Text(emoji, size=32), ft.Text(title, size=14, weight="bold", color="white")],
                                      alignment=ft.MainAxisAlignment.CENTER,
                                      horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    bgcolor=color,
                    border_radius=20,
                    on_click=lambda e, s=screen: go_to(s),
                )
            )
        return grid

    def show_emotion_detail(emoji, title):
        emotions_data = {
            "Anxiety": (
                "Anxiety is your body's natural alarm system. It's trying to protect you! Sometimes the alarm rings too loud, but that's okay.",
                ["Fast heartbeat", "Sweaty hands", "Butterflies in stomach", "Hard to breathe", "Feeling restless"],
                ["Take slow, deep breaths", "Count to 10",
                 "Communicate with a trusted adult (by writing or sign language)", "Use breathing exercises",
                 "Remember: this feeling will pass"]),
            "Anger": (
                "Anger is a normal emotion that tells us something isn't right. It's okay to feel angry, but we need to express it safely.",
                ["Hot face", "Tight muscles", "Clenched fists", "Fast heartbeat", "Feeling like yelling"],
                ["Count to 10 slowly", "Take deep breaths", "Go to a quiet place", "Draw your feelings",
                 "Write or sign what made you angry"]),
            "Sadness": (
                "Sadness is a natural response when we lose something or someone important. It's healthy to cry and feel sad sometimes.",
                ["Want to cry", "Low energy", "Heavy feeling in chest", "Don't want to play", "Hard to smile"],
                ["It's okay to cry", "Hug someone you trust", "Do something you enjoy",
                 "Express your feelings (by writing, drawing, or sign language)", "Remember happy memories"]),
            "Fear": (
                "Fear helps keep us safe from danger. Sometimes we feel scared of things that aren't really dangerous, and that's normal too.",
                ["Shaking or trembling", "Fast heartbeat", "Want to hide", "Hard to think clearly", "Sweating"],
                ["Take slow breaths", "Tell yourself 'I am safe'", "Seek help (via text, sign language, or gesture)",
                 "Face fears step by step", "Remember you are brave"]),
            "Overwhelmed": (
                "Feeling overwhelmed happens when too many things feel like too much at once. Your brain is trying to handle everything, and it needs a little break.",
                ["Head feels full", "Hard to focus", "Feeling stuck", "Want to shut down", "Easily upset"],
                ["Take a break", "Do one small thing at a time", "Take deep breaths", "Ask for help",
                 "Make a simple plan"]),
            "Frustration": (
                "Frustration happens when things don't go the way you expect. It's okay to feel this way when something is hard or unfair.",
                ["Tense body", "Sighing a lot", "Clenched jaw", "Feeling stuck", "Want to give up"],
                ["Take a short break", "Try again slowly", "Ask for help", "Stretch your body",
                 "Remind yourself it's okay to make mistakes"]),
            "Lonely": (
                "Feeling lonely means you wish you had more connection or someone to be with. Everyone feels lonely sometimes, and it can pass.",
                ["Heavy feeling in chest", "Low energy", "Want to be with someone", "Feeling left out", "Quiet mood"],
                ["Talk to someone you trust", "Spend time with family or friends", "Write or draw your feelings",
                 "Play with a pet", "Join an activity you enjoy"]),
            "Hopeful": (
                "Hopeful means you believe things can get better. Even small hope can help you feel stronger and keep going.",
                ["Light feeling in chest", "Small smile", "More energy", "Feeling calm", "Looking forward to things"],
                ["Think about good things ahead", "Set a small goal", "Celebrate small wins",
                 "Spend time with positive people", "Remind yourself things can improve"]),
        }
        what, signs, tips = emotions_data.get(title, ("", [], []))

        def back_to_emotions():
            state.current_screen = "emotions"
            update_page()

        colors = get_colors()
        detail_view = ft.Column([
            ft.Row([ft.TextButton("← Back", on_click=lambda e: back_to_emotions())]),
            ft.Text(emoji, size=48),
            ft.Text(title, size=28, weight="bold", color=colors["text_primary"]),
            ft.Container(content=ft.Column(
                [ft.Text("What is it?", weight="bold"), ft.Text(what, size=14, color=colors["text_secondary"])]),
                         bgcolor=colors["card"], border_radius=20, padding=15),
            ft.Container(content=ft.Column([ft.Text("Signs in your body", weight="bold")] + [
                ft.Text(f"• {s}", size=14, color=colors["text_secondary"]) for s in signs]), bgcolor=colors["card"],
                         border_radius=20, padding=15),
            ft.Container(content=ft.Column([ft.Text("What you can do", weight="bold")] + [
                ft.Text(f"✅ {t}", size=14, color=colors["text_secondary"]) for t in tips]), bgcolor=colors["card"],
                         border_radius=20, padding=15),
        ], spacing=15, scroll=ft.ScrollMode.ADAPTIVE)
        page.controls.clear()
        page.add(detail_view)
        page.update()

    async def start_exercise_timer():
        if not state.active_exercise:
            return
        title, inhale, hold, exhale = state.active_exercise
        state.exercise_phase = "inhale"
        state.exercise_remaining = inhale
        state.exercise_cycles = 0
        state.exercise_running = True
        while state.exercise_running:
            await asyncio.sleep(1)
            if not state.exercise_running:
                break
            if state.exercise_remaining <= 1:
                if state.exercise_phase == "inhale":
                    state.exercise_phase = "hold"
                    state.exercise_remaining = hold
                elif state.exercise_phase == "hold":
                    state.exercise_phase = "exhale"
                    state.exercise_remaining = exhale
                else:  # exhale
                    state.exercise_phase = "inhale"
                    state.exercise_remaining = inhale
                    state.exercise_cycles += 1
            else:
                state.exercise_remaining -= 1
            update_page()
        state.exercise_timer_task = None

    def start_exercise(title, inhale, hold, exhale):
        if state.exercise_timer_task:
            state.exercise_timer_task.cancel()
        state.active_exercise = (title, inhale, hold, exhale)
        state.exercise_phase = "inhale"
        state.exercise_remaining = inhale
        state.exercise_cycles = 0
        state.exercise_running = True
        state.current_screen = "active_exercise"
        update_page()

        async def run():
            await start_exercise_timer()

        state.exercise_timer_task = asyncio.create_task(run())

    def stop_exercise():
        if state.exercise_timer_task:
            state.exercise_timer_task.cancel()
            state.exercise_timer_task = None
        state.exercise_running = False
        state.active_exercise = None
        go_to("breathing")

    def add_post(e, text_input):
        if text_input.value.strip():
            state.posts.insert(0, {"user": "You", "text": text_input.value.strip(), "likes": 0, "liked": False})
            text_input.value = ""
            update_page()
        else:
            text_input.error_text = "Please write something"
            page.update()

    def toggle_like(index):
        if not state.posts[index]["liked"]:
            state.posts[index]["likes"] += 1
            state.posts[index]["liked"] = True
        else:
            state.posts[index]["likes"] -= 1
            state.posts[index]["liked"] = False
        update_page()

    def update_page():
        colors = get_colors()
        page.bgcolor = colors["bg"]
        page.controls.clear()
        if state.current_screen == "welcome":
            page.add(
                ft.Container(
                    expand=True,
                    bgcolor=PRIMARY,
                    content=ft.Column(
                        [
                            ft.Text("🛡️", size=80),
                            ft.Text("MindGuard", size=36, weight="bold", color="white"),
                            ft.Text("Your everyday anxiety support companion", size=18, color="white",
                                    text_align="center"),
                            ft.Text("Helping children with disabilities understand, manage, and prevent anxiety",
                                    size=16, color="white", text_align="center"),
                            ft.ElevatedButton("Get Started", on_click=lambda e: go_to("accessibility"), bgcolor="white",
                                              color=PRIMARY),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=20,
                    ),
                )
            )
        elif state.current_screen == "accessibility":
            options = [
                ("visual", "👁️", "I have trouble seeing", "Audio instructions, text descriptions, high contrast"),
                ("hearing", "👂", "I am deaf or hard of hearing",
                 "Visual alerts, captions, Romanian Sign Language (LSR)"),
                ("mobility", "🙌", "I have trouble with movement", "Large buttons, simplified navigation"),
                ("speech", "💬", "I am non-verbal or have speech difficulties", "Tap-to-express, visual communication"),
                ("none", "✨", "No specific needs", "Standard experience"),
            ]
            cards = ft.Column(spacing=16)
            for key, emoji, title, desc in options:
                is_sel = state.selected_needs[key]
                card = ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(emoji, size=28),
                            ft.Text("✅", size=20, color=colors["primary"]) if is_sel else ft.Container(width=20,
                                                                                                       height=20)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text(title, size=18, weight="bold", color=colors["text_primary"]),
                        ft.Text(desc, size=14, color=colors["text_secondary"]),
                    ], spacing=8),
                    bgcolor=colors["card"] if not is_sel else (
                        HIGH_CONTRAST_CARD if state.high_contrast else "#E8EAF6"),
                    border_radius=20,
                    padding=20,
                    border=ft.border.all(2, colors["primary"] if is_sel else "#E5E7EB"),
                    on_click=lambda e, k=key: toggle_need(k),
                )
                cards.controls.append(card)
            page.add(
                ft.Column([
                    ft.Text("Let's make MindGuard perfect for you", size=24, weight="bold",
                            color=colors["text_primary"]),
                    cards,
                    ft.ElevatedButton("Continue", on_click=lambda e: go_to("questionnaire"), bgcolor=colors["primary"],
                                      color="white"),
                ], scroll=ft.ScrollMode.ADAPTIVE, spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            )
        elif state.current_screen == "questionnaire":
            q1_options = ["Never", "Sometimes", "Often", "Always"]
            q2_options = ["Never", "Rarely", "Sometimes", "Often"]
            q3_options = ["Not at all", "A little", "Somewhat", "Very much"]
            q4_options = ["Very poorly", "Poorly", "OK", "Well", "Very well"]

            def on_q1_change(e):
                state.q_anxiety = e.control.value

            def on_q2_change(e):
                state.q_judged = e.control.value

            def on_q3_change(e):
                state.q_helped = e.control.value

            def on_q4_change(e):
                state.q_manage = e.control.value

            def submit(e):
                go_to("home")

            content = ft.Column([
                ft.Row([ft.TextButton("← Back", on_click=lambda e: back())]),
                ft.Text("Let's understand you better", size=24, weight="bold", color=colors["text_primary"]),
                ft.Text("These questions help us personalize your experience.", size=14,
                        color=colors["text_secondary"]),
                ft.Container(
                    content=ft.Column([
                        ft.Text("1. How often do you feel anxious, and do you think it's related to your disability?",
                                size=14, color=colors["text_primary"]),
                        ft.RadioGroup(
                            content=ft.Column([ft.Radio(value=opt, label=opt) for opt in q1_options], spacing=5),
                            on_change=on_q1_change),
                        ft.Divider(height=10, color="transparent"),
                        ft.Text("2. Have you ever felt judged because of your disability?", size=14,
                                color=colors["text_primary"]),
                        ft.RadioGroup(
                            content=ft.Column([ft.Radio(value=opt, label=opt) for opt in q2_options], spacing=5),
                            on_change=on_q2_change),
                        ft.Divider(height=10, color="transparent"),
                        ft.Text("3. How willing are you to let others help you?", size=14,
                                color=colors["text_primary"]),
                        ft.RadioGroup(
                            content=ft.Column([ft.Radio(value=opt, label=opt) for opt in q3_options], spacing=5),
                            on_change=on_q3_change),
                        ft.Divider(height=10, color="transparent"),
                        ft.Text("4. How well do you think you manage your anxiety in public?", size=14,
                                color=colors["text_primary"]),
                        ft.RadioGroup(
                            content=ft.Column([ft.Radio(value=opt, label=opt) for opt in q4_options], spacing=5),
                            on_change=on_q4_change),
                    ], spacing=15),
                    bgcolor=colors["card"],
                    border_radius=20,
                    padding=20,
                ),
                ft.ElevatedButton("Continue to MindGuard", on_click=submit, bgcolor=colors["primary"], color="white"),
            ], spacing=20, scroll=ft.ScrollMode.ADAPTIVE)
            page.add(content)
        elif state.current_screen == "home":
            mood_row = create_mood_row()
            action_grid = create_action_grid()
            tip = ft.Container(
                content=ft.Row([
                    ft.Text("💡", size=24),
                    ft.Text(
                        "Anxiety is your body's natural alarm system. It's not something to fear — it's something to understand and manage.",
                        size=14, color=colors["text_primary"], expand=True),
                ], spacing=10),
                bgcolor=colors["card"],
                border_radius=20,
                padding=15,
            )
            header = ft.Container(
                content=ft.Row([
                    ft.Text("Welcome back!", size=24, weight="bold", color="white"),
                    ft.Container(ft.Text("🔥 1 day streak", size=14, weight="bold", color=colors["primary"]),
                                 bgcolor="white", border_radius=16, padding=ft.padding.symmetric(10, 5)),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor=PRIMARY,
                padding=20,
                border_radius=ft.border_radius.only(bottom_left=20, bottom_right=20),
            )
            page.add(
                ft.Column([
                    header,
                    ft.Container(
                        content=ft.Column([
                            ft.Text("How are you feeling today?", size=18, weight="bold", color=colors["text_primary"]),
                            mood_row,
                            state.mood_message,
                        ], spacing=15),
                        bgcolor=colors["card"],
                        border_radius=20,
                        padding=20,
                        margin=ft.margin.all(20),
                    ),
                    ft.Container(padding=ft.padding.symmetric(horizontal=20), content=action_grid),
                    tip,
                ], scroll=ft.ScrollMode.ADAPTIVE)
            )
        elif state.current_screen == "breathing":
            exercises = [
                ("🎈", "Balloon Breathing", "Imagine inflating a balloon slowly", 4, 4, 6),
                ("🌊", "Ocean Waves", "Breathe like gentle ocean waves", 4, 2, 6),
                ("⭐", "Star Breathing", "Trace a star as you breathe", 5, 3, 5),
                ("🦋", "Butterfly Hug", "Cross arms and tap shoulders gently", 3, 2, 4),
            ]
            cards = ft.Column(spacing=16)
            for emoji, title, desc, inhale, hold, exhale in exercises:
                cards.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text(emoji, size=40),
                            ft.Column([
                                ft.Text(title, size=18, weight="bold", color=colors["text_primary"]),
                                ft.Text(desc, size=14, color=colors["text_secondary"]),
                                ft.Text(f"In:{inhale}s Hold:{hold}s Out:{exhale}s", size=12, color=colors["primary"]),
                            ], spacing=5, expand=True),
                        ], spacing=15),
                        bgcolor=colors["card"],
                        border_radius=20,
                        padding=15,
                        on_click=lambda e, name=title, i=inhale, h=hold, o=exhale: start_exercise(name, i, h, o),
                    )
                )
            page.add(
                ft.Column([
                    ft.Row([ft.TextButton("← Back", on_click=lambda e: back())]),
                    ft.Text("Breathing & Mindfulness", size=24, weight="bold", color=colors["text_primary"]),
                    ft.Text("These exercises help calm your body. Anxiety is natural — these tools help you manage it.",
                            size=14, color=colors["text_secondary"]),
                    cards,
                ], spacing=20, scroll=ft.ScrollMode.ADAPTIVE)
            )
        elif state.current_screen == "active_exercise" and state.active_exercise:
            title, inhale, hold, exhale = state.active_exercise
            phase_text = ""
            if state.exercise_phase == "inhale":
                phase_text = "Breathe In..."
                circle_color = ACCENT
            elif state.exercise_phase == "hold":
                phase_text = "Hold..."
                circle_color = PRIMARY
            else:
                phase_text = "Breathe Out..."
                circle_color = SECONDARY
            scale = 1.5 if state.exercise_phase == "inhale" else (1.5 if state.exercise_phase == "hold" else 0.8)
            circle = ft.Container(
                width=150, height=150,
                bgcolor=circle_color,
                border_radius=75,
                content=ft.Column(
                    [ft.Text(str(state.exercise_remaining), size=48, weight="bold", color="white")],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True
                ),
                scale=scale,
            )
            page.add(
                ft.Column([
                    ft.Row([ft.TextButton("← Back", on_click=lambda e: stop_exercise())]),
                    ft.Text(title, size=24, weight="bold", color=colors["text_primary"]),
                    ft.Text(f"Cycles: {state.exercise_cycles}", size=16),
                    ft.Container(
                        expand=True,
                        content=ft.Column(
                            [circle],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            alignment=ft.MainAxisAlignment.CENTER,
                            expand=True
                        ),
                    ),
                    ft.Text(phase_text, size=28, weight="bold", color=colors["text_primary"]),
                    ft.ElevatedButton("Stop", on_click=lambda e: stop_exercise(), bgcolor="#EF4444", color="white"),
                ], spacing=30, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)
            )
        elif state.current_screen == "emotions":
            emotions = [
                ("😟", "Anxiety", SECONDARY),
                ("😠", "Anger", "#EF4444"),
                ("😢", "Sadness", "#3B82F6"),
                ("😨", "Fear", "#8B5CF6"),
                ("😵", "Overwhelmed", "#F59E0B"),
                ("😤", "Frustration", "#F97316"),
                ("🥺", "Lonely", "#6366F1"),
                ("🌈", "Hopeful", "#10B981"),
            ]
            grid = ft.GridView(runs_count=2, max_extent=150, spacing=16, run_spacing=16, child_aspect_ratio=1)
            for emoji, title, color in emotions:
                grid.controls.append(
                    ft.Container(
                        content=ft.Column(
                            [ft.Text(emoji, size=48), ft.Text(title, size=16, weight="bold", color="white")],
                            alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor=color,
                        border_radius=20,
                        on_click=lambda e, em=emoji, t=title: show_emotion_detail(em, t),
                    )
                )
            page.add(
                ft.Column([
                    ft.Row([ft.TextButton("← Back", on_click=lambda e: back())]),
                    ft.Text("Understand Your Emotions", size=24, weight="bold", color=colors["text_primary"]),
                    ft.Text("Emotions are natural — even difficult ones. Tap to learn about each one.", size=14,
                            color=colors["text_secondary"]),
                    grid,
                ], spacing=20, scroll=ft.ScrollMode.ADAPTIVE)
            )
        elif state.current_screen == "sos":
            steps = [
                "✋ STOP - Pause everything. You are safe right now.",
                "💨 BREATHE - Take 3 slow, deep breaths with me.",
                "💭 NAME IT - What feeling do you have? It's okay to feel it.",
                "⭐ CHOOSE - Pick one thing to help: breathing, music, or a hug.",
                "🤝 ASK FOR HELP - Tell a trusted adult, parent, or use Expert Connect.",
            ]
            page.add(
                ft.Column([
                    ft.Row([ft.TextButton("← Back", on_click=lambda e: back())]),
                    ft.Text("🆘 SOS - Emergency Calming Guide", size=28, weight="bold", color="#EF4444"),
                    ft.Text("Follow these steps if you feel overwhelmed:", size=16, color=colors["text_secondary"]),
                    ft.Column([ft.Text(step, size=14, color=colors["text_secondary"]) for step in steps], spacing=10),
                    ft.Text("If it's an emergency, tell a parent, teacher, or trusted adult immediately.", size=14,
                            color=colors["text_secondary"], italic=True),
                ], spacing=20, scroll=ft.ScrollMode.ADAPTIVE)
            )
        elif state.current_screen == "expert":
            cards = [
                ("👨‍👩‍👧", "Parent/Guardian Portal",
                 "Parents can view your progress and find recommended specialists nearby."),
                ("🏫", "School Counselor Link", "Connect with your school counselor for in-person support."),
                ("📞", "Helpline Directory", "Quick access to child mental health helplines, available 24/7."),
                ("📋", "Session Notes", "Share your MindGuard mood data with your psychologist."),
            ]
            list_cards = ft.Column(spacing=16)
            for emoji, title, desc in cards:
                list_cards.controls.append(
                    ft.Container(
                        content=ft.Row([ft.Text(emoji, size=32), ft.Column(
                            [ft.Text(title, size=18, weight="bold", color=colors["text_primary"]),
                             ft.Text(desc, size=14, color=colors["text_secondary"])], expand=True, spacing=5)],
                                       spacing=15),
                        bgcolor=colors["card"],
                        border_radius=20,
                        padding=15,
                    )
                )
            warning = ft.Container(
                content=ft.Row([ft.Text("⚠️", size=24), ft.Text(
                    "Important: MindGuard is a support tool — it does not replace professional therapy or medical care. If you are in crisis, contact emergency services or a trusted adult immediately.",
                    size=14, color=colors["text_primary"], expand=True)], spacing=10),
                bgcolor="#FFF3E0" if not state.high_contrast else HIGH_CONTRAST_CARD,
                border_radius=20,
                padding=16,
            )
            page.add(
                ft.Column([
                    ft.Row([ft.TextButton("← Back", on_click=lambda e: back())]),
                    ft.Text("Expert Connect", size=28, weight="bold", color=colors["text_primary"]),
                    ft.Row([ft.Text("🤝", size=40), ft.Text("You Don't Have to Do This Alone", size=20, weight="bold",
                                                           color=colors["text_primary"])], spacing=10),
                    ft.Text(
                        "MindGuard helps you every day, but sometimes talking to a professional makes all the difference.",
                        size=14, color=colors["text_secondary"]),
                    list_cards,
                    warning,
                ], spacing=20, scroll=ft.ScrollMode.ADAPTIVE)
            )
        elif state.current_screen == "progress":
            page.add(
                ft.Column([
                    ft.Row([ft.TextButton("← Back", on_click=lambda e: back())]),
                    ft.Text("My Progress", size=28, weight="bold", color=colors["text_primary"]),
                    ft.Row([
                        ft.Container(content=ft.Column([ft.Text("😊", size=24), ft.Text("3.5", size=20, weight="bold",
                                                                                       color=colors["text_primary"]),
                                                        ft.Text("Avg Mood", size=12, color=colors["text_secondary"])]),
                                     expand=True),
                        ft.Container(content=ft.Column(
                            [ft.Text("🫁", size=24), ft.Text("2", size=20, weight="bold", color=colors["text_primary"]),
                             ft.Text("Exercises", size=12, color=colors["text_secondary"])]), expand=True),
                        ft.Container(content=ft.Column(
                            [ft.Text("🔥", size=24), ft.Text("1", size=20, weight="bold", color=colors["text_primary"]),
                             ft.Text("Day Streak", size=12, color=colors["text_secondary"])]), expand=True),
                    ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                    ft.Text("This Week's Mood", size=18, weight="bold", color=colors["text_primary"]),
                    ft.Row([ft.Container(height=40, width=30, bgcolor="#10B981", border_radius=5) for _ in range(7)],
                           alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                    ft.Text("Achievements", size=18, weight="bold", color=colors["text_primary"]),
                    ft.Column([
                        ft.Text("⭐ First Check-in ✅", color=colors["text_secondary"]),
                        ft.Text("🎈 Breathing Pro 🔒", color=colors["text_secondary"]),
                        ft.Text("🔥 7-Day Streak 🔒", color=colors["text_secondary"]),
                    ]),
                ], spacing=20, scroll=ft.ScrollMode.ADAPTIVE)
            )
        elif state.current_screen == "about":
            partners = ["Liceul Tehnologic Special nr.3", "Liceul Special pentru Deficienti de Auz Sfanta Maria",
                        "Scoala Gimnaziala Speciala pentru Surzi nr.1", "Fundatia CODA Farmecul Tacerii",
                        "ANSR Asociatia Nationala a Surzilor din Romania", "Liceul Tehnologic Special Regina Elisabeta"]
            page.add(
                ft.Column([
                    ft.Row([ft.TextButton("← Back", on_click=lambda e: back())]),
                    ft.Row(
                        [ft.Text("🛡️", size=48), ft.Text("MindGuard", size=32, weight="bold", color=colors["primary"])],
                        spacing=10),
                    ft.Text("Your everyday anxiety support companion", size=14, color=colors["text_secondary"]),
                    ft.Container(
                        ft.Text("Social Enterprise", size=12, weight="bold", color="white", text_align="center"),
                        bgcolor=ACCENT, border_radius=20, padding=ft.padding.symmetric(8, 16)),
                    ft.Container(content=ft.Column([ft.Text("Our Mission", weight="bold", color=colors["text_primary"]),
                                                    ft.Text(
                                                        "MindGuard is a social enterprise helping children aged 8-14 with disabilities understand, manage, and prevent anxiety. We believe anxiety is a natural response — not something to suppress or fear.",
                                                        size=12, color=colors["text_secondary"])]),
                                 bgcolor=colors["card"], border_radius=20, padding=15),
                    ft.Container(content=ft.Column(
                        [ft.Text("Accessibility First", weight="bold", color=colors["text_primary"]), ft.Text(
                            "• Visual impairments: audio instructions, high contrast\n• Deaf/hearing: Romanian Sign Language LSR, captions\n• Non-verbal/speech: tap-to-express, visual communication\n• Mobility: large targets, simplified navigation",
                            size=12, color=colors["text_secondary"])]), bgcolor=colors["card"], border_radius=20,
                                 padding=15),
                    ft.Container(content=ft.Column(
                        [ft.Text("Built with Expert Guidance", weight="bold", color=colors["text_primary"]), ft.Text(
                            "Developed with feedback from a school counselor at Colegiul National Mihai Viteazul specialized in children with disabilities, and a psychology master's student focusing on child psychology. MindGuard complements but does not replace professional therapy.",
                            size=12, color=colors["text_secondary"])]), bgcolor=colors["card"], border_radius=20,
                                 padding=15),
                    ft.Container(content=ft.Column(
                        [ft.Text("Early Adopters", weight="bold", color=colors["text_primary"])] + [
                            ft.Text(f"• {p}", size=12, color=colors["text_secondary"]) for p in partners]),
                                 bgcolor=colors["card"], border_radius=20, padding=15),
                    ft.Container(content=ft.Column(
                        [ft.Text("Sustainability", weight="bold", color=colors["text_primary"]), ft.Text(
                            "All revenue from grants, donations, and partnerships is reinvested into improving the app. MindGuard will always remain accessible to children who need it most.",
                            size=12, color=colors["text_secondary"])]), bgcolor=colors["card"], border_radius=20,
                                 padding=15),
                    ft.Text("Follow us: @mindguard on Instagram & TikTok", size=12, italic=True,
                            color=colors["text_secondary"]),
                ], spacing=15, scroll=ft.ScrollMode.ADAPTIVE)
            )
        elif state.current_screen == "community":
            colors = get_colors()
            new_post_input = ft.TextField(
                hint_text="Share something with the community...",
                multiline=True,
                min_lines=2,
                max_lines=5,
                expand=True,
                border_radius=20,
                bgcolor=colors["card"],
                color=colors["text_primary"],
                hint_style=ft.TextStyle(color=colors["text_secondary"]),
            )

            def on_add_post(e):
                add_post(e, new_post_input)

            posts_list = ft.Column(spacing=12, scroll=ft.ScrollMode.ADAPTIVE)
            for idx, post in enumerate(state.posts):
                posts_list.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(post["user"], size=14, weight="bold", color=colors["text_primary"]),
                                ft.Text(f"❤️ {post['likes']}", size=12, color=colors["text_secondary"]),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Text(post["text"], size=14, color=colors["text_primary"]),
                            ft.Row([
                                ft.TextButton(
                                    "Like" if not post["liked"] else "Unlike",
                                    on_click=lambda e, idx=idx: toggle_like(idx),
                                    style=ft.ButtonStyle(color=colors["primary"])
                                ),
                            ], alignment=ft.MainAxisAlignment.END),
                        ], spacing=8),
                        bgcolor=colors["card"],
                        border_radius=20,
                        padding=12,
                    )
                )
            content = ft.Column([
                ft.Row([ft.TextButton("← Back", on_click=lambda e: back())]),
                ft.Text("Community Forum", size=28, weight="bold", color=colors["text_primary"]),
                ft.Text("Share your thoughts and support each other.", size=14, color=colors["text_secondary"]),
                ft.Row([
                    new_post_input,
                    ft.ElevatedButton("Post", on_click=on_add_post, bgcolor=colors["primary"], color="white"),
                ], spacing=10),
                ft.Text("Recent posts:", size=18, weight="bold", color=colors["text_primary"]),
                posts_list,
            ], spacing=20, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
            page.add(content)
        page.update()

    update_page()


ft.app(target=main)