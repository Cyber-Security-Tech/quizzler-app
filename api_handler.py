import requests

def get_questions(amount=10, type="boolean", difficulty=None, category=None):
    """
    Fetches quiz questions from the Open Trivia Database API.

    Parameters:
        amount (int): Number of questions to fetch.
        type (str): Type of questions ("boolean" or "multiple").
        difficulty (str): Optional difficulty level ("easy", "medium", "hard").
        category (int): Optional category ID from the OpenTDB API.

    Returns:
        list: A list of question dictionaries or an empty list if an error occurs or no questions are found.
    """
    url = f"https://opentdb.com/api.php?amount={amount}&type={type}"

    if difficulty:
        url += f"&difficulty={difficulty.lower()}"
    if category:
        url += f"&category={category}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # API response_code 0 = Success; other values = no results or error
        if data["response_code"] != 0:
            return []

        return data["results"]

    except requests.exceptions.RequestException:
        # Could log the error in a real app
        return []
