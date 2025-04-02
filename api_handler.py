import requests

def get_questions(amount=10, type="boolean", difficulty=None, category=None):
    url = f"https://opentdb.com/api.php?amount={amount}&type={type}"

    if difficulty:
        url += f"&difficulty={difficulty.lower()}"
    if category:
        url += f"&category={category}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data["response_code"] != 0:
            # API returned successfully, but no questions available
            return []

        return data["results"]
    except requests.exceptions.RequestException:
        # Connection-level error or bad response
        return []
