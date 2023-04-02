import openai


def get_summary(message: str, max_summary_length=2000) -> str:
    return openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"Сформируй подробное саммари к части диалога из Discord, с большим количеством деталей по конкретным пользователям, до {max_summary_length} символов."},
            {"role": "user", "content": f"{message}"},
        ],
    ).choices[0].message.content


def get_json_summary(message: str) -> str:
    prompt = '''
    Дан диалог в Discord. Необходимо сгенерировать ответ в виде json в следующем формате:
    { "context": { "sinopsis":"...", "keywords":["...", "..."] }, "opinions": [ {"participant_name":"...", "opinions":["...", "..."]}, {"participant_name":"...", "opinions":["...", "..."]} ] }
    В объекте context содержится описание переписки,  в sinopsis краткое описание, в списке keywords нормализованные ключевые слова, если ключевое слово искаженное или сленговое, оно должно быть заменено на общеупотребимый аналог.
    В объекте opinions содержатся описание позиций каждого из участников переписки в виде "любит апельсины", "считает сложной игру в шахматы" и т.п.
    '''
    return openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": message},
        ],
    ).choices[0].message.content
