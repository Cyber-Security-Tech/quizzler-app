class Question:
    """
    Represents a quiz question with text and its correct answer.
    
    Attributes:
        text (str): The question text.
        answer (str): The correct answer ("True" or "False").
    """
    def __init__(self, text: str, answer: str):
        self.text = text
        self.answer = answer

    def __repr__(self):
        return f"Question(text={self.text!r}, answer={self.answer!r})"
