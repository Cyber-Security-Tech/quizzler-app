from question_model import Question
from quiz_brain import QuizBrain
from ui import QuizInterface
from api_handler import get_questions

question_data = get_questions()

question_bank = [Question(q["question"], q["correct_answer"]) for q in question_data]

quiz = QuizBrain(question_bank)
ui = QuizInterface(quiz)
