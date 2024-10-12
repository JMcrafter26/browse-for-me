import requests
import json
from duckduckgo_search import DDGS
import bs4
import time
import os
import http.server


def getWebsiteData(url):
    print('Getting website data for: ', url)
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    # try to get the text in the main tag
    try:
        text = soup.find('main').get_text()
    except:
        text = soup.get_text()

    # unescape html entities
    # text = bs4.BeautifulSoup(text, 'html.parser').get_text()
    # remove \\n
    text = text.replace('\\n', '')
    return text

def preparePrompt(query, websiteData):
    print('Preparing prompt')
    print('Query:', query)
    # print('Website data:', websiteData)
    prompt = {
    "model": "llama3.2:3b",
    "stream": False,
      "format": "json",
  "messages": [
    {
      "content": "You are an advanced, reliable, candid AI system that takes user search queries, converts them into questions, and answers them, using specific facts and details sourced from webpages to prove your answer. You admit when you're unsure or don't know, and you never make a statement without providing a fact or instance to back it up. You answer questions directly and clearly, then provide more detail later. You follow the JSON schema exactly.",
      "role": "system"
    },
    {
      "role": "system"
    },
    {
      "role": "user",
    }
  ]
}

    DATE_TIME = time.strftime('%Y-%m-%d %H:%M:%S')
    QUERY = query
    HOST_1 = websiteData[0]['href']
    MARKDOWN_1 = websiteData[0]['rawBody']
    HOST_2 = websiteData[1]['href']
    MARKDOWN_2 = websiteData[1]['rawBody']
    HOST_3 = websiteData[2]['href']
    MARKDOWN_3 = websiteData[2]['rawBody']
    HOST_4 = websiteData[3]['href']
    MARKDOWN_4 = websiteData[3]['rawBody']
    HOST_5 = websiteData[4]['href']
    MARKDOWN_5 = websiteData[4]['rawBody']
    HOST_6 = ''
    MARKDOWN_6 = ''
    content1 = f"# CONTEXT\nCurrent date: {DATE_TIME}.\n\nHere are result  from a web search for '{QUERY}':\nBEGIN WEB PAGE {HOST_1} {MARKDOWN_1}END WEB PAGE\nBEGIN WEB PAGE {HOST_2} {MARKDOWN_2}END WEB PAGE\nBEGIN WEB PAGE {HOST_3} {MARKDOWN_3}END WEB PAGE\nBEGIN WEB PAGE {HOST_4} {MARKDOWN_4}END WEB PAGE\nBEGIN WEB PAGE {HOST_5} {MARKDOWN_5}END WEB PAGE\nBEGIN WEB PAGE {HOST_6} {MARKDOWN_6}END WEB PAGE"
    # replace \n\n\n with \n
    content1 = content1.replace('\n\n\n', '\n')
    content1 = content1.replace('\n\n\n', '\n')
    
    
    content2 = f"## YOUR JOB\nThe user searched for: '{QUERY}'.\nAbove, I pasted text from some search results for this query.\nYou will:\n1. Take the user's query and infer what questions they want answered.\n2. Read the documents above and find relevant info that answers their questions. Ignore irrelevant results.\n3. Write a document, in precise JSON format as described below, that answers their inferred questions.\n4. Then, add headings and sections that provide more detail below.\n\nWrite your answer by summarizing the webpage data above and/or using your own knowledge.\nYour answer should be fact-filled and SPECIFIC, providing information like prices, review sentiment, dates, addresses, times,  recipe instructions and ingredients with specific steps, times and amounts, timelines, characters, answers, features, comparisons, shipping times, related media.\nAvoid repeating text or concepts in your headings or bullets.\nStylistically write as though a Professor or The Economist would, in short, approachable, and professional language.\nDo not acknowledge specific webpage metadata; only quote page content and use its info.\nWhen asked to list entities, list 8-10 per section if possible.\n\n## INFERRING USER QUESTION\nHere are some examples of queries and how they were 'expanded' to infer what the user wants:\n\"notion company\" -> \"Provide facts and figures for Notion's size, products, funding, growth founders, and recent news. Add a section with a company timeline, and a section for key people.\"\n···basque dishes\" -> \"List and describe 8+ basque dishes in your initial answer. Then, add sections explaining the 4 key elements that define Basque cooking overall.···\n\"cook couscous\" -> \"First, provide an ordered list of 3-5 steps to cook couscous, then list all ingredients, tips for cooking and serving various kinds of couscous.\"\n\"die hard\" -> \"Tell me about the movie Die Hard, including plot, cast, reviews, and where to watch.\"\n\"perplexity series b\" -> \"With bullet points, tell me key details of Perplexity's Series B funding round like amount, key funders and goals. In the next sections, give me background on the company, competitors and industry.\"\n\"diff kindle scribe pens\" -> \"Compare and contrast the different Kindle Scribe pens, focusing on price, feature and other important differences.\"\n\"why is Goya famous\" -> \"Explain with specific examples, as an art historian would, why Goya is such an influential and famous painter, including the exact styles that made their work stand out relative to most artists. Include a section listing 5+ examples of their most famous works.\"\n\"white teeth book\" -> \"Provide a synopsis of the book White Teeth, details of the key themes covered, and the most celebrated or criticized aspects of the work.\"\n\"chinese restaurants park slope\" -> \"In your answer, list Chinese restaurants in Park Slope, with a brief description of why each is notable. Then, write headings + sections detailing the top 4's signature dishes, cuisine, prices and reviews.\"\n\"which is bigger, fanduel or draftkings\" -> \"Directly whether Draftkings or Fanduel is larger in the title. Then, provide concrete market share and users, followed by sections with a detailed history of both companies.\"\n\n## JSON Schema\n```\ninterface Response " + "{\n    // metadata:\n    inferredQuestion: string // In 1-2 sentences, what info do you think the user wants? Look at the examples above. Your answer and sections should answer this.\n    imageSearchQuery: string // SPECIFIC 8 word image query to accompany the report\n    tintColor: string // hex code of thematic color based on content\n    title: string // name of topic, e.g. \"How to Cook Cauliflower\", \"Why is Goya famous?\" or \"China has more people than the US.\" If the query was a specifically-answerable question, answer it.\n\n    // report content:\n    answer: Section // 1st part of doc: directly answer the inferred question, list examples, or say you don't know. Write at least a few sentences. The title of the document should be short but the answer underneath should be in-depth.\n    headings: string[4] // 2nd part: headings for 4 additional sections of your report, each 1-2 words. You can provide more detail on an item you talked about in `answer`, provide background knowledge, add a related list or timeline (plot points for a book, career for a person). Write a few sentences at least for each and go into more detail than you did in your answer.\n    sections: [string: Section] // Fill out a section for each heading with 5-10 bullet points for each, always include a sentence or two with each bullet point.\n}\n\ninterface Section {\n    emojiBullets: String[]; // Detailed bullet points listing entities, steps, facts, or examples. As many as necessary, ideally 5+. Use format \"[emoji] [title]: [detail]\". E.g. \"···· Price: $499 for base model\" or \"1······ Step 1: bring 2 cups water to boil\".\n    source: 'webpage' | 'knowledge' // where did the info you just wrote come from?\n    citedSubstring: string // If source=webpage, copy 1-2 sentences verbatim from the webpages to support what you wrote. Copy exactly: no translation, paraphraing, removal of syntax or special chars.\n}\n```\n\ntThe emojis should be in this format: :emojiname: e.g.: `:moon:` or `:calendar:`\n\nBelow, your report, following the JSON schema exactly:"

    prompt['messages'][1]['content'] = content1
    prompt['messages'][2]['content'] = content2
    return prompt

def getAiResponse(prompt):
    print('Getting AI response')
    # e.g.:
#     curl http://localhost:11434/api/chat -d '{
#   "model": "llama3.2",
#   "messages": [
#     {
#       "role": "user",
#       "content": "why is the sky blue?"
#     }
#   ]
# }'
    url = 'http://localhost:11434/api/chat'
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, json=prompt)
    response = response.json()
    # save response to a file
    with open('response.json', 'w') as f:
        json.dump(response, f)

    jsonData = json.loads(response['message']['content'])
    
    with open('1.json', 'w') as f:
        json.dump(jsonData, f)
    return jsonData

# STEPS

def step1(query):
    try:
        # get search results
        results = DDGS().text(query, max_results=5)
    except Exception as e:
        print('Error:', e)
        if '202 Ratelimit' in str(e):
            print('You have reached the maximum number of requests per minute. Please try again later.')
        exit()
    
    # save results to a file
    with open('results.json', 'w') as f:
        json.dump(results, f)

    # read results from a file
    with open('results.json', 'r') as f:
        results = json.load(f)

    return results

def step2(results):
    websiteData = []
    # merge results and website data (put websitedata in "rawBody" in results)
    print('Getting data from websites')

    for result in results:
        websiteData.append({
            'href': result['href'],
            'title': result['title'],
            'rawBody': getWebsiteData(result['href'])
        })
    
    return websiteData

def step3(jsonData):
    
    imageQuery = jsonData['imageSearchQuery']
    print('Getting images for:', imageQuery)
    try:
        images = DDGS().images(imageQuery, max_results=5)
    except Exception as e:
        print('Error:', e)
        if '202 Ratelimit' in str(e):
            print('You have reached the maximum number of requests per minute. Please try again later.')
            exit()
    # save images to a file
    with open('images.json', 'w') as f:
        json.dump(images, f)
    return images

def main(query='Who created GitHub?'):

    try:
        # remove every .json file in the directory
        for file in os.listdir():
            if file.endswith('.json'):
                os.remove(file)

    except:
        pass

    print('Getting search results for:', query)
    results = step1(query)
    
    # get website data
    websiteData = step2(results)

    prompt = preparePrompt(query, websiteData)
    
    # save prompt to a file
    with open('prompt.json', 'w') as f:
        json.dump(prompt, f)

    print('Getting data from AI')
    jsonData = getAiResponse(prompt)

    # check if the response is valid
    if 'title' not in jsonData or 'answer' not in jsonData or 'sections' not in jsonData:
        # repeat the process max 3 times
        for i in range(3):
            print('Invalid response. Trying again...')
            jsonData = getAiResponse(prompt)
            if 'title' in jsonData and 'answer' in jsonData and 'sections' in jsonData:
                break
        else:
            print('Invalid response. Try again later.')
    # add the sources to the data.json file
    # sources: [
    #    {
    #        "url": "https://www.example.com",
    #        "title": "Example"
    #    },...
    # ]


    sources = []
    for data in websiteData:
        sources.append({
            'url': data['href'],
            'title': data['title']
        })
    jsonData['sources'] = sources


    with open('2.json', 'w') as f:
        json.dump(jsonData, f)



    # search for images
    images = step3(jsonData)

    
    # add imageUrls to the data.json file
    with open('data.json', 'w') as f:
        jsonData['imageUrls'] = images
        json.dump(jsonData, f)
    
    print('Done')
    
    # host the files using a simple http server and open the browser
    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler
    # open localhost:8000 using the default browser
    os.system(f'start http://localhost:{PORT}/report.html')

    with http.server.HTTPServer(("", PORT), Handler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()



if __name__ == "__main__":
    print('Enter your query:')
    query = input()
    main(query)