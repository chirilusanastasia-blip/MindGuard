"""
MindGuard - Aplicație mobilă accesibilă pentru gestionarea anxietății la copii cu dizabilități.

Acest modul implementează interfața completă a aplicației MindGuard folosind framework-ul
Flet (cross-platform UI bazat pe Flutter). Aplicația oferă:
    - Onboarding personalizat în funcție de tipul de dizabilitate al utilizatorului
    - Exerciții de respirație ghidate cu animații vizuale și temporizare prin asyncio
    - Chestionar de auto-evaluare a stării emoționale
    - Forum comunitar pentru schimb de experiențe
    - Mod de contrast înalt pentru utilizatori cu deficiențe vizuale severe

Arhitectura aplicației urmează un model  simplu:
    1. Toată starea este centralizată în clasa AppState (Single Source of Truth)
    2. Acțiunile utilizatorului declanșează modificări ale stării
    3. Modificările de stare declanșează re-randarea componentelor afectate
    4. Sistemul de teme (get_colors) returnează paleta activă în funcție de mod
Acest model este similar cu paradigma reactivă folosită în React sau Flutter.

Autori:
    - Chirilus Anastasia (Project Manager & UX Designer)
    - Vatamaniuc Karina (Lead Developer & Content Creator)

Concurs: InfoEducația 2026, Secțiunea Software Utilitar
Licență: MIT
Repository: https://github.com/chirilusanastasia-blip/MindGuard
"""

import flet as ft
import asyncio

# === PALETA DE CULORI ===
# Culorile principale pentru modul normal (interfață prietenoasă pentru copii)
PRIMARY = "#5B5FE6"        # Mov-albastru — culoarea principală a brand-ului
SECONDARY = "#FF7E5F"      # Portocaliu cald — folosit pentru accente și CTA-uri
ACCENT = "#26C6A0"         # Verde-turcoaz — pentru elemente pozitive (success, ok)
BG = "#F8FAFF"             # Fundal foarte deschis — odihnitor pentru ochi
CARD_BG = "#FFFFFF"        # Cardurile sunt albe pentru contrast bun cu fundalul
TEXT_PRIMARY = "#1E2140"   # Text principal — închis dar nu negru pur (mai prietenos)
TEXT_SECONDARY = "#374151" # Text secundar — gri închis pentru subtitluri și descrieri

# Culorile pentru modul de contrast înalt (utilizatori cu deficiențe vizuale severe)
# Standard recunoscut: fundal negru + text galben = contrast maxim
HIGH_CONTRAST_BG = "#000000"
HIGH_CONTRAST_TEXT = "#FFFF00"
HIGH_CONTRAST_CARD = "#333333"


class AppState:
    """
    Stare centralizată a aplicației MindGuard (Single Source of Truth).

    Această clasă încapsulează toate datele necesare pentru funcționarea aplicației:
    ecranul curent, preferințele utilizatorului (nevoi specifice, contrast înalt),
    răspunsurile la chestionar, starea exercițiilor active și conținutul forumului.

    Folosirea unei stări centralizate simplifică gestionarea datelor și permite
    actualizarea coerentă a interfeței la fiecare schimbare. Acest pattern este
    similar cu cel folosit în React (useState) sau în Redux/MobX.

    Attributes:
        current_screen (str): Ecranul afișat curent. Valori posibile:
            "welcome", "accessibility", "questionnaire", "home", "breathing",
            "active_exercise", "emotions", "sos", "expert", "progress",
            "about", "community", "emotion_detail".
        selected_needs (dict): Tipurile de dizabilități selectate de utilizator
            (visual, hearing, mobility, speech, none). Determină adaptările UI.
        mood_message (ft.Text): Componenta Flet care afișează mesajul personalizat
            după selectarea stării emoționale curente.
        high_contrast (bool): Dacă modul de contrast înalt este activ.
            Afectează întreaga paletă vizuală prin funcția get_colors().
        q_anxiety, q_judged, q_helped, q_manage (str): Răspunsurile utilizatorului
            la cele 4 întrebări ale chestionarului de auto-evaluare.
        active_exercise (tuple | None): Datele exercițiului de respirație în desfășurare
            (title, inhale, hold, exhale), sau None dacă niciun exercițiu nu este activ.
        exercise_phase (str): Faza curentă a exercițiului — "inhale", "hold", "exhale".
        exercise_remaining (int): Secunde rămase din faza curentă.
        exercise_cycles (int): Numărul de cicluri complete efectuate.
        exercise_running (bool): Indicator dacă temporizatorul rulează.
        exercise_timer_task (asyncio.Task | None): Referință la task-ul asyncio care
            gestionează temporizarea. CRITIC: trebuie anulat la părăsirea ecranului
            pentru a evita memory leaks.
        posts (list[dict]): Lista postărilor din forumul comunitar. Fiecare post conține:
            user (str), text (str), likes (int), liked (bool).
    """

    def __init__(self):
        """Inițializează starea cu valorile implicite la prima deschidere a aplicației."""
        # Ecranul de început este întotdeauna "welcome" (intro pentru utilizatori noi)
        self.current_screen = "welcome"
        # Nicio nevoie specifică nu este selectată implicit
        self.selected_needs = {"visual": False, "hearing": False, "mobility": False, "speech": False, "none": False}
        # Componenta Flet pentru afișarea mesajului personalizat (se actualizează dinamic)
        self.mood_message = ft.Text("", size=16, text_align="center")
        # Modul de contrast normal la prima utilizare
        self.high_contrast = False
        # răspunsuri chestionar (rămân goale până la completare)
        self.q_anxiety = ""
        self.q_judged = ""
        self.q_helped = ""
        self.q_manage = ""
        # exercițiu activ (niciunul la pornire)
        self.active_exercise = None
        self.exercise_phase = "inhale"
        self.exercise_remaining = 0
        self.exercise_cycles = 0
        self.exercise_running = False
        self.exercise_timer_task = None
        # forum posts — date demo pentru a popula forumul la prima utilizare
        self.posts = [
            {"user": "Alex", "text": "I tried the balloon breathing and it really helped me calm down!", "likes": 3,
             "liked": False},
            {"user": "Maria", "text": "Feeling anxious today. Anyone else?", "likes": 5, "liked": False},
            {"user": "David", "text": "Remember: you are not alone! 💙", "likes": 7, "liked": False},
        ]


# Instanța globală a stării — accesată din toate funcțiile aplicației
state = AppState()


def get_colors():
    """
    Returnează paleta de culori activă în funcție de modul de contrast.

    Această funcție centralizează tema vizuală a aplicației. Când modul de contrast
    înalt este activ (state.high_contrast = True), se returnează o paletă cu fundal
    negru și text galben — standard recunoscut pentru utilizatorii cu deficiențe
    vizuale severe. Altfel, se returnează paleta normală.

    Avantajul acestei abordări: schimbarea modului de contrast este instantanee
    pentru întreaga interfață, fără a fi nevoie de logică separată în fiecare ecran.

    Returns:
        dict: Dicționar cu chei (bg, card, text_primary, text_secondary, primary,
              secondary, accent, border) și valorile lor în format hexazecimal.
    """
    if state.high_contrast:
        # Paletă de contrast înalt — folosită pentru utilizatori cu deficiențe vizuale
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
        # Paleta normală — interfață prietenoasă pentru toți ceilalți utilizatori
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
    """
    Punct de intrare al aplicației MindGuard.

    Funcția este apelată automat de Flet la pornirea aplicației și configurează
    pagina principală. Definește toate funcțiile interne (callback-uri pentru
    interacțiunile utilizatorului) și logica de randare a ecranelor.

    Folosirea closure-urilor (funcții definite în interiorul lui main) permite
    accesul direct la obiectul `page` fără a fi nevoie să-l transmitem explicit
    fiecărei funcții — design pattern comun în aplicațiile Flet.

    Args:
        page (ft.Page): Obiectul Flet care reprezintă fereastra aplicației.
    """
    # Configurarea inițială a paginii
    page.title = "MindGuard"
    page.padding = 20
    page.bgcolor = BG
    page.window_width = 400   # Dimensiune optimă pentru mobile (portrait)
    page.window_height = 700
    page.scroll = ft.ScrollMode.ADAPTIVE  # Scroll activat când conținutul depășește înălțimea

    def go_to(screen):
        """
        Schimbă ecranul curent al aplicației.

        Dacă utilizatorul părăsește un exercițiu activ, oprește task-ul asyncio
        de temporizare pentru a evita memory leaks și utilizare inutilă a CPU-ului.

        Args:
            screen (str): Numele ecranului destinație.
        """
        # Curățare task asyncio dacă părăsim un exercițiu de respirație
        if screen == "home" and state.current_screen == "active_exercise":
            if state.exercise_timer_task:
                state.exercise_timer_task.cancel()
                state.exercise_timer_task = None
            state.exercise_running = False
        state.current_screen = screen
        update_page()

    def back():
        """
        Implementează butonul "Back" — navigare înapoi în fluxul aplicației.

        Logica de navigare urmează ordinea naturală: welcome → accessibility →
        questionnaire → home → diversele ecrane. La revenirea din ecranele
        secundare (breathing, emotions, sos, etc.) se merge înapoi la home.

        Special: la părăsirea unui exercițiu activ, task-ul asyncio este oprit
        pentru a elibera resursele sistemului.
        """
        if state.current_screen == "accessibility":
            state.current_screen = "welcome"
        elif state.current_screen == "questionnaire":
            state.current_screen = "accessibility"
        elif state.current_screen == "home":
            state.current_screen = "questionnaire"
        elif state.current_screen == "active_exercise":
            # Anulare task asyncio pentru a evita memory leaks
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
        """
        Gestionează selecția/deselecția tipurilor de nevoi specifice.

        Logică specială:
            - Dacă utilizatorul selectează "none" (fără nevoi specifice), toate
              celelalte opțiuni sunt deselectate automat (sunt mutuale).
            - Dacă selectează orice altă opțiune, "none" este automat deselectat.
            - Selectarea opțiunii "visual" activează automat modul de contrast înalt.

        Args:
            key (str): Cheia opțiunii (visual, hearing, mobility, speech, none).
        """
        if key == "none":
            # "Fără nevoi specifice" este exclusivă cu celelalte opțiuni
            for k in state.selected_needs:
                state.selected_needs[k] = False
            state.selected_needs["none"] = True
        else:
            # Orice altă selecție anulează "none" și togglează opțiunea
            state.selected_needs["none"] = False
            state.selected_needs[key] = not state.selected_needs[key]
        # Auto-activare mod contrast înalt pentru deficiențe vizuale
        state.high_contrast = state.selected_needs.get("visual", False)
        update_page()

    def create_mood_row():
        """
        Creează rândul de selecție a stării emoționale curente (mood).

        Afișează 5 emoji-uri colorate corespunzătoare unor stări emoționale
        (de la fericit la trist). La click pe oricare dintre ele, afișează
        un mesaj personalizat de încurajare. Aceasta este una dintre primele
        interacțiuni pe care utilizatorul le are pe ecranul "home".

        Returns:
            ft.Row: Componenta Flet care conține cele 5 butoane-emoji.
        """
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
        """
        Creează grila principală de acțiuni de pe ecranul "home".

        Grila conține 7 butoane mari, prietenoase, care duc la principalele
        funcționalități ale aplicației: exerciții de respirație, învățare
        despre emoții, SOS, progres, conectare cu experți, despre, comunitate.

        Returns:
            ft.GridView: Grila cu butoanele de acțiuni.
        """
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
        """
        Afișează ecranul de detalii pentru o emoție specifică.

        Pentru fiecare emoție (Anxiety, Anger, Sadness, Fear, Overwhelmed,
        Frustration, Lonely, Hopeful) afișează:
            - O descriere prietenoasă a emoției
            - Semnele fizice/comportamentale ale acelei emoții
            - Sfaturi practice de gestionare adaptate pentru copii cu dizabilități

        Args:
            emoji (str): Emoticonul care reprezintă emoția.
            title (str): Numele emoției (ex: "Anxiety", "Anger").
        """
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
        """
        Corutina asyncio care gestionează temporizarea unui exercițiu de respirație.

        Funcționează pe baza unui ciclu de 3 faze: inhale → hold → exhale.
        Fiecare secundă verifică dacă faza curentă s-a încheiat și trece la
        următoarea. La sfârșitul fiecărui ciclu complet, incrementează contorul
        de cicluri și actualizează UI-ul.

        Folosirea asyncio (în loc de threading) permite temporizarea fără a
        bloca interfața utilizator, integrându-se natural cu loop-ul Flet.
        Bucla se oprește când state.exercise_running devine False (la stop sau back).
        """
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
        """
        Inițializează și pornește un exercițiu nou de respirație.

        Dacă există deja un exercițiu activ, îl oprește pentru a evita conflicte.
        Apoi setează datele exercițiului nou, navighează la ecranul "active_exercise"
        și creează task-ul asyncio pentru temporizare.

        Args:
            title (str): Numele exercițiului (afișat pe ecran).
            inhale (int): Durata fazei de inspirație, în secunde.
            hold (int): Durata fazei de reținere, în secunde.
            exhale (int): Durata fazei de expirație, în secunde.
        """
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
        """
        Oprește exercițiul de respirație curent și revine la lista exercițiilor.

        Anulează task-ul asyncio pentru a elibera resursele și resetează starea
        exercițiului. Este apelată când utilizatorul apasă butonul "Stop".
        """
        if state.exercise_timer_task:
            state.exercise_timer_task.cancel()
            state.exercise_timer_task = None
        state.exercise_running = False
        state.active_exercise = None
        go_to("breathing")

    def add_post(e, text_input):
        """
        Adaugă o postare nouă în forumul comunitar.

        Validează că textul nu este gol (după trim), apoi inserează postarea
        la începutul listei (most recent first). Postarea aparține "You" — fiindcă
        aplicația rulează local fără sistem de cont.

        Args:
            e: Evenimentul Flet care a declanșat funcția (de obicei click pe Post).
            text_input: Componenta Flet de input care conține textul postării.
        """
        # Validare: textul nu trebuie să fie gol
        if text_input.value.strip():
            state.posts.insert(0, {"user": "You", "text": text_input.value.strip(), "likes": 0, "liked": False})
            text_input.value = ""
            update_page()
        else:
            text_input.error_text = "Please write something"
            page.update()

    def toggle_like(index):
        """
        Schimbă starea like-ului pentru o postare (toggle).

        Dacă postarea nu era apreciată, incrementează numărul de like-uri și
        marchează ca apreciată. Dacă era deja apreciată, decrementează și
        anulează marcarea.

        Args:
            index (int): Indexul postării în lista state.posts.
        """
        if not state.posts[index]["liked"]:
            state.posts[index]["likes"] += 1
            state.posts[index]["liked"] = True
        else:
            state.posts[index]["likes"] -= 1
            state.posts[index]["liked"] = False
        update_page()

    def update_page():
        """
        Re-randează întreaga interfață în funcție de starea curentă.

        Este funcția centrală a aplicației — apelată de fiecare dată când
        starea se schimbă (navigare, toggle, exercițiu, postare nouă etc.).
        Verifică valoarea state.current_screen și construiește componentele
        Flet corespunzătoare ecranului respectiv.

        Această abordare (clear + add) este simplă și sigură pentru o aplicație
        de dimensiunea aceasta. Pentru aplicații mai mari, s-ar putea optimiza
        cu diff-uri (actualizare doar a componentelor afectate).
        """
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
                    border=ft.Border.all(2, colors["primary"] if is_sel else "#E5E7EB"),
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
                                 bgcolor="white", border_radius=16, padding=ft.Padding.symmetric(vertical=10, horizontal=5)),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor=PRIMARY,
                padding=20,
                border_radius=ft.BorderRadius.only(bottom_left=20, bottom_right=20),
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
                        margin=ft.Margin.all(20),
                    ),
                    ft.Container(padding=ft.Padding.symmetric(horizontal=20), content=action_grid),
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
                        bgcolor=ACCENT, border_radius=20, padding=ft.Padding.symmetric(vertical=8, horizontal=16)),
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
