import requests, json
# from tools import data
from requests_html import HTMLSession
from bs4 import BeautifulSoup

def sec(time_str:str):
    parts = time_str.split(":")
    hours = 0
    minutes = 0
    seconds = 0
    if len(parts) == 2:
        minutes = int(parts[0])
        seconds = int(parts[1])
    elif len(parts) == 1:
        seconds = int(parts[0])
    return hours * 3600 + minutes * 60 + seconds

def video(name:str):
    url = "https://www.youtube.com/results"
    payloads = { "search_query":name+" @puregym" }
    headers = { "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36" }
    session = HTMLSession()
    response = session.get(url=url, headers=headers, params=payloads)
    html_content = response.html.html
    session.close()
    soup = BeautifulSoup(html_content,'lxml')
    script_tag = soup.find('script', text=lambda text: text and 'var ytInitialData' in text)
    script_content = script_tag.string
    start_index = script_content.find('var ytInitialData = ') + len('var ytInitialData = ')
    end_index = script_content.find('};', start_index) + 1
    yt_initial_data = script_content[start_index:end_index]
    data = json.loads(yt_initial_data)
    l = []
    for i in data.get("contents").get("twoColumnSearchResultsRenderer").get("primaryContents").get("sectionListRenderer").get("contents")[0].get("itemSectionRenderer").get("contents"):
        if i.get("videoRenderer")!=None:
            if sec(i["videoRenderer"]["lengthText"]["simpleText"]) <= 29:
                return {
                    "id": i["videoRenderer"]["videoId"], 
                    "title": i["videoRenderer"]["title"]["runs"][0]["text"], 
                    "thumbnail": i["videoRenderer"]["thumbnail"][ "thumbnails"][0]["url"]
                }   
    return None

def get_exercise(muscle:str, category:str):
# category is the equipments and muscles are muscles I mean that's readable
    url = f"https://musclewiki.com/newapi/exercise/exercises/?limit=20&muscles={muscle}&category={category}"
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}
    response = requests.request(method="GET", url=url, headers=headers)
        
    res = response.json()
    result = []
    for i in res.get("results"):
        if i.get("name")!=None:
            result.append({
                "id": i["id"],
                "name": i["name"],
                "difficulty": i.get("difficulty"),
                "correct_steps": i.get("correct_steps"),
                "muscles": i.get("muscles"),
                "url": "/exercise/"+((i["name"]).replace(' ', '-')).lower()
        })
    
    return result