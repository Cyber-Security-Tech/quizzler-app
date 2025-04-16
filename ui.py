from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from typing import Optional

from question_model import Question
from quiz_brain import QuizBrain
from api_handler import get_questions

THEME_COLOR = "#375362"

CATEGORY_MAP = {
    "General Knowledge": 9,
    "Books": 10,
    "Film": 11,
    "Music": 12,
    "Science & Nature": 17,
    "Computers": 18,
    "Mathematics": 19,
    "Mythology": 20,
    "Sports": 21,
    "History": 23,
    "Politics": 24,
    "Animals": 27,
}


class QuizInterface:
    """
    Graphical user interface for the Quizzler App using Tkinter.

    Features:
    - Start screen with category and difficulty selection
    - Quiz screen with animated questions and image-based answer buttons
    - Progress bar and score tracker
    - Final result screen with restart/quit options
    - Error handling for API issues
    """

    def __init__(self) -> None:
        self.window = Tk()
        self.window.title("Quizzler")
        self.window.config(padx=20, pady=20, bg=THEME_COLOR)

        # Quiz logic and state
        self.quiz: Optional[QuizBrain] = None

        # UI elements
        self.score_label: Optional[Label] = None
        self.canvas: Optional[Canvas] = None
        self.true_button: Optional[Button] = None
        self.false_button: Optional[Button] = None
        self.question_text: Optional[int] = None
        self.difficulty_buttons: dict[str, Button] = {}

        # Progress UI
        self.progress_canvas: Optional[Canvas] = None
        self.progress_fill: Optional[int] = None
        self.progress_label: Optional[Label] = None

        # User selections
        self.selected_difficulty = StringVar(value="easy")
        self.selected_category = StringVar(value="General Knowledge")

        self.setup_start_screen()
        self.window.mainloop()

    def setup_start_screen(self) -> None:
        """Initial start menu UI with difficulty and category options."""
        self.clear_window()

        Label(self.window, text="Select Difficulty:", fg="white", bg=THEME_COLOR, font=("Arial", 14, "bold")).pack(pady=10)

        button_frame = Frame(self.window, bg=THEME_COLOR)
        button_frame.pack()

        for level in ["easy", "medium", "hard"]:
            btn = Button(button_frame, text=level.title(), width=10, command=lambda l=level: self.select_difficulty(l))
            btn.pack(side=LEFT, padx=5, pady=5)
            self.difficulty_buttons[level] = btn

        self.highlight_selected_difficulty("easy")

        Label(self.window, text="Select Category:", fg="white", bg=THEME_COLOR, font=("Arial", 14, "bold")).pack(pady=10)

        category_dropdown = ttk.Combobox(self.window, values=list(CATEGORY_MAP.keys()), textvariable=self.selected_category, state="readonly")
        category_dropdown.pack(pady=5)

        Button(self.window, text="Start Quiz", width=20, command=self.start_quiz, cursor="hand2").pack(pady=20)

    def select_difficulty(self, level: str) -> None:
        """Set the selected difficulty and update button styles."""
        self.selected_difficulty.set(level)
        self.highlight_selected_difficulty(level)

    def highlight_selected_difficulty(self, selected: str) -> None:
        """Highlight the selected difficulty button."""
        for level, button in self.difficulty_buttons.items():
            if level == selected:
                button.config(bg="white", fg=THEME_COLOR, relief=SUNKEN)
            else:
                button.config(bg="SystemButtonFace", fg="black", relief=RAISED)

    def start_quiz(self) -> None:
        """Fetch questions and launch the quiz interface."""
        category_id = CATEGORY_MAP.get(self.selected_category.get(), 9)
        difficulty = self.selected_difficulty.get()

        try:
            question_data = get_questions(amount=10, difficulty=difficulty, category=category_id)

            if not question_data:
                self.show_error("No questions available or API error occurred.\nPlease try a different combination or check your connection.")
                return

            question_bank = [Question(q["question"], q["correct_answer"]) for q in question_data]
            self.quiz = QuizBrain(question_bank)
            self.setup_quiz_ui()
            self.get_next_question()

        except Exception:
            self.show_error("An unexpected error occurred.\nPlease try again.")

    def setup_quiz_ui(self) -> None:
        """Render the quiz UI: canvas, buttons, progress bar, etc."""
        self.clear_window()

        self.score_label = Label(text="Score: 0", fg="white", bg=THEME_COLOR, font=("Arial", 12, "bold"))
        self.score_label.grid(row=0, column=1)

        self.progress_label = Label(text="Progress: 0 / 10", fg="white", bg=THEME_COLOR, font=("Arial", 10, "bold"))
        self.progress_label.grid(row=1, column=0, columnspan=2)

        self.progress_canvas = Canvas(width=300, height=20, bg="white", highlightthickness=0)
        self.progress_fill = self.progress_canvas.create_rectangle(0, 0, 0, 20, fill="#4CAF50", width=0)
        self.progress_canvas.grid(row=2, column=0, columnspan=2, pady=(0, 20))

        self.canvas = Canvas(width=300, height=250, bg="white")
        self.question_text = self.canvas.create_text(
            150,
            125,
            width=280,
            text="Question",
            fill=THEME_COLOR,
            font=("Arial", 16, "italic")
        )
        self.canvas.grid(row=3, column=0, columnspan=2, pady=30)

        true_img_raw = Image.open("assets/true.png").resize((70, 70))
        false_img_raw = Image.open("assets/false.png").resize((70, 70))
        true_img = ImageTk.PhotoImage(true_img_raw)
        false_img = ImageTk.PhotoImage(false_img_raw)

        self.true_button = Button(image=true_img, highlightthickness=0, command=self.true_pressed, cursor="hand2")
        self.true_button.image = true_img
        self.true_button.grid(row=4, column=0)

        self.false_button = Button(image=false_img, highlightthickness=0, command=self.false_pressed, cursor="hand2")
        self.false_button.image = false_img
        self.false_button.grid(row=4, column=1)

        # Hover Effects
        self.true_button.bind("<Enter>", lambda e: self.true_button.config(bg="#e0ffe0"))
        self.true_button.bind("<Leave>", lambda e: self.true_button.config(bg="SystemButtonFace"))

        self.false_button.bind("<Enter>", lambda e: self.false_button.config(bg="#ffe0e0"))
        self.false_button.bind("<Leave>", lambda e: self.false_button.config(bg="SystemButtonFace"))

    def clear_window(self) -> None:
        """Clear all widgets from the window."""
        for widget in self.window.winfo_children():
            widget.destroy()

    def get_next_question(self) -> None:
        """Display the next quiz question or end the quiz if finished."""
        self.canvas.config(bg="white")
        if self.quiz.still_has_questions():
            self.score_label.config(text=f"Score: {self.quiz.score}")
            q_text = self.quiz.next_question()
            self.animate_question(q_text)
            self.update_progress_bar()
        else:
            self.show_final_screen()

    def animate_question(self, text: str, index: int = 0) -> None:
        """Simulate a typing animation effect for each question."""
        if index == 0:
            self.canvas.itemconfig(self.question_text, text="")

        if index < len(text):
            current = self.canvas.itemcget(self.question_text, "text")
            self.canvas.itemconfig(self.question_text, text=current + text[index])
            self.window.after(10, lambda: self.animate_question(text, index + 1))

    def update_progress_bar(self) -> None:
        """Update the progress bar and label based on current question number."""
        current = self.quiz.question_number
        total = len(self.quiz.question_list)

        self.progress_label.config(text=f"Progress: {current} / {total}")
        bar_width = int((current / total) * 300)
        self.progress_canvas.coords(self.progress_fill, 0, 0, bar_width, 20)

    def show_final_screen(self) -> None:
        """Display the final score and end-of-quiz options."""
        self.clear_window()
        final_score_text = f"You scored {self.quiz.score} out of {len(self.quiz.question_list)}!"
        Label(self.window, text=final_score_text, fg="white", bg=THEME_COLOR, font=("Arial", 16, "bold")).pack(pady=40)

        Button(self.window, text="Restart Quiz", width=15, command=self.setup_start_screen, cursor="hand2").pack(pady=10)
        Button(self.window, text="Quit", width=15, command=self.window.quit, cursor="hand2").pack(pady=5)

    def true_pressed(self) -> None:
        """Handle when the user clicks the True button."""
        self.give_feedback(self.quiz.check_answer("True"))

    def false_pressed(self) -> None:
        """Handle when the user clicks the False button."""
        self.give_feedback(self.quiz.check_answer("False"))

    def give_feedback(self, is_right: bool) -> None:
        """Show feedback color based on whether the answer was correct."""
        self.canvas.config(bg="green" if is_right else "red")
        self.window.after(1000, self.get_next_question)

    def show_error(self, message: str) -> None:
        """Show an error screen if questions can't be loaded."""
        self.clear_window()
        Label(self.window, text=message, fg="white", bg=THEME_COLOR, wraplength=280, font=("Arial", 14, "bold")).pack(pady=30)
        Button(self.window, text="Back to Start", command=self.setup_start_screen, cursor="hand2").pack(pady=10)
