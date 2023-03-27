import openai


def get_summary(message: str) -> str:
    return openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Сформируй подробное саммари к диалогу из Discord"},
            {"role": "user", "content": f"{message}"},
        ],
        temperature=0.3,
    ).choices[0].message.content


def get_json_summary(message: str) -> str:
    prompt = '''
    Дан диалог в Discord. Необходимо сгенерировать ответ в виде json в следующем формате:
    {
        "context": {
            "sinopsis":"...",
             "keywords":["...", "..."]
             },
        "opinions": [
            {"participant_name":"...", "opinions":["...", "..."]},
            {"participant_name":"...", "opinions":["...", "..."]}
        ]
    }
    В объекте context содержится описание переписки,  в sinopsis краткое описание, в списке keywords нормализованные ключевые слова, если ключевое слово искаженное или сленговое, оно должно быть заменено на общеупотребимый аналог.
    В объекте opinions содержатся описание позиций каждого из участников переписки в виде "любит апельсины", "считает сложной игру в шахматы" и т.п.
    '''
    return openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": message},
        ],
        temperature=0.3,
    ).choices[0].message.content
