import html
from question_model import Question

class QuizBrain:
    """
    Controls the flow of the quiz:
    - Tracks question number, score, and current question.
    - Moves to the next question.
    - Validates answers.
    """

    def __init__(self, question_list: list[Question]):
        self.question_number = 0
        self.score = 0
        self.question_list = question_list
        self.current_question: Question | None = None

    def still_has_questions(self) -> bool:
        """
        Checks if there are more questions left in the quiz.
        """
        return self.question_number < len(self.question_list)

    def next_question(self) -> str:
        """
        Retrieves the next question and updates current state.

        Returns:
            str: The unescaped text of the next question.
        """
        self.current_question = self.question_list[self.question_number]
        self.question_number += 1
        return html.unescape(self.current_question.text)

    def check_answer(self, user_answer: str) -> bool:
        """
        Compares the user's answer to the correct one.

        Returns:
            bool: True if correct, False otherwise.
        """
        correct_answer = self.current_question.answer
        if user_answer == correct_answer:
            self.score += 1
            return True
        return False
