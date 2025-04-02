import requests

def get_questions(amount=10, type="boolean"):
    url = f"https://opentdb.com/api.php?amount={amount}&type={type}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data["results"]
    except requests.exceptions.RequestException:
        return [{"question": "API error occurred. Try again later.", "correct_answer": "True"}]
