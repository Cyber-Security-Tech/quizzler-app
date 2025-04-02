from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
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
    def __init__(self):
        self.window = Tk()
        self.window.title("Quizzler")
        self.window.config(padx=20, pady=20, bg=THEME_COLOR)

        self.quiz = None
        self.score_label = None
        self.canvas = None
        self.true_button = None
        self.false_button = None
        self.question_text = None
        self.difficulty_buttons = {}

        self.selected_difficulty = StringVar(value="easy")
        self.selected_category = StringVar(value="General Knowledge")

        self.setup_start_screen()

        self.window.mainloop()

    def setup_start_screen(self):
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

        Button(self.window, text="Start Quiz", width=20, command=self.start_quiz).pack(pady=20)

    def select_difficulty(self, level):
        self.selected_difficulty.set(level)
        self.highlight_selected_difficulty(level)

    def highlight_selected_difficulty(self, selected):
        for level, button in self.difficulty_buttons.items():
            if level == selected:
                button.config(bg="white", fg=THEME_COLOR, relief=SUNKEN)
            else:
                button.config(bg="SystemButtonFace", fg="black", relief=RAISED)

    def start_quiz(self):
        category_id = CATEGORY_MAP.get(self.selected_category.get(), 9)
        difficulty = self.selected_difficulty.get()

        try:
            question_data = get_questions(amount=10, difficulty=difficulty, category=category_id)

            if not question_data or len(question_data) == 0:
                self.show_error("No questions available or API error occurred.\nPlease try a different combination or check your connection.")
                return

            question_bank = [Question(q["question"], q["correct_answer"]) for q in question_data]
            self.quiz = QuizBrain(question_bank)
            self.setup_quiz_ui()
            self.get_next_question()

        except Exception:
            self.show_error("An unexpected error occurred.\nPlease try again.")

    def setup_quiz_ui(self):
        self.clear_window()

        self.score_label = Label(text="Score: 0", fg="white", bg=THEME_COLOR, font=("Arial", 12, "bold"))
        self.score_label.grid(row=0, column=1)

        self.canvas = Canvas(width=300, height=250, bg="white")
        self.question_text = self.canvas.create_text(
            150,
            125,
            width=280,
            text="Question",
            fill=THEME_COLOR,
            font=("Arial", 16, "italic")
        )
        self.canvas.grid(row=1, column=0, columnspan=2, pady=30)

        true_img_raw = Image.open("assets/true.png").resize((70, 70))
        false_img_raw = Image.open("assets/false.png").resize((70, 70))
        true_img = ImageTk.PhotoImage(true_img_raw)
        false_img = ImageTk.PhotoImage(false_img_raw)

        self.true_button = Button(image=true_img, highlightthickness=0, command=self.true_pressed)
        self.true_button.image = true_img
        self.true_button.grid(row=2, column=0)

        self.false_button = Button(image=false_img, highlightthickness=0, command=self.false_pressed)
        self.false_button.image = false_img
        self.false_button.grid(row=2, column=1)

    def clear_window(self):
        for widget in self.window.winfo_children():
            widget.destroy()

    def get_next_question(self):
        self.canvas.config(bg="white")
        if self.quiz.still_has_questions():
            self.score_label.config(text=f"Score: {self.quiz.score}")
            q_text = self.quiz.next_question()
            self.canvas.itemconfig(self.question_text, text=q_text)
        else:
            self.canvas.itemconfig(self.question_text, text="You’ve reached the end of the quiz.")
            self.true_button.config(state="disabled")
            self.false_button.config(state="disabled")

    def true_pressed(self):
        self.give_feedback(self.quiz.check_answer("True"))

    def false_pressed(self):
        self.give_feedback(self.quiz.check_answer("False"))

    def give_feedback(self, is_right):
        self.canvas.config(bg="green" if is_right else "red")
        self.window.after(1000, self.get_next_question)

    def show_error(self, message):
        self.clear_window()
        Label(self.window, text=message, fg="white", bg=THEME_COLOR, wraplength=280, font=("Arial", 14, "bold")).pack(pady=30)
        Button(self.window, text="Back to Start", command=self.setup_start_screen).pack(pady=10)
