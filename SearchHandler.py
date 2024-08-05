import openai

class ChatGPTHandler:
    def __init__(self, api_key):
        openai.api_key = api_key

    def ask_question(self, question, text_chunks, model="gpt-4", max_tokens=300):
        answers = []
        for chunk in text_chunks:
            prompt = f"{chunk}\n\nQuestion: {question}\nAnswer:"
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            answer = response.choices[0].message['content'].strip()
            answers.append(answer)
        return answers

    def get_precise_answer(self, question, text_chunks):
        initial_answers = self.ask_question(question, text_chunks)
        aggregated_answer = "\n\n".join(initial_answers)

        # Secondary query to refine the answer
        refinement_prompt = f"The following are multiple answers to the question '{question}':\n\n{aggregated_answer}\n\nPlease provide a concise and precise answer based on the above information."
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": refinement_prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        precise_answer = response.choices[0].message['content'].strip()

        return precise_answer
