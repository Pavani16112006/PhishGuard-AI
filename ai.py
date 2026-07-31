from openai import OpenAI

client = OpenAI()

def analyze(site):

    prompt=f"""

URL:
{site.url}

Title:
{site.title}

Text:
{site.text}

Analyze this website.

Return JSON only.

"""

    response=client.responses.create(

        model="gpt-5.5",

        input=prompt

    )

    return response.output_text
