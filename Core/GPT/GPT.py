import os
import openai
openai.api_key = "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"

def Suggestion(text):
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": f"""Suggest movie with below feature but follow these conditions :
                                        1. Don't explanation
                                        2. If can't find any movie just say 'no movie'.
                                        3. If there are exist upper than 5 movie just 
                                            return 5 of them in random mode.
                                        4. Return just movie name  with out any 
                                            description in list view
                                        Features:
                                        {text}"""}])

    suggestions = completion.choices[0].message['content'].split('\n')
    movies =[]
    for i in suggestions:
        movies.append(i.split('. ')[1])
    return movies
 