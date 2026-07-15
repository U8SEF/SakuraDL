import re
import html
import json
import requests
from bs4 import BeautifulSoup

class handler:

    def __init__(self, url):
        self.url = url
        if "https://anime3rb.com/titles/" not in self.url:
            raise ValueError("Invalid URL. Please provide a valid anime3rb.com title URL.")
        self.anime_id = self.url.split("/")[-1]
        self.anime_url = f"https://anime3rb.com/titles/{self.anime_id}"
        self.session = requests.Session()

    def load(self):
        self.response = self.session.get(self.url)
        self.soup = BeautifulSoup(self.response.content, "html.parser")
        self.title = self.soup.find("h1", class_="text-2xl font-bold uppercase inline").text.strip()
        self.rating = self.soup.find("p", class_="text-lg leading-relaxed").text.strip()
        self.episodes_container = self.soup.find("div", class_="flex flex-grow flex-col")
        episodes = []

        for episode in self.episodes_container.find_all("a", class_="btn btn-md btn-light border-b w-full px-2 py-1 !rounded-none dark:border-dark-600/50 flex items-center gap-3"):
            episode_number = episode.find("div", class_="flex gap-2 items-end").text.strip()
            episode_name = episode.find("p", class_="text-sm").text.strip()
            episode_url = episode["href"]
            episodes.append({
                "number": episode_number,
                "name": episode_name,
                "url": episode_url
            })

        return {
            "title": self.title,
            "rating": self.rating,
            "episodes_count": len(episodes),
            "episodes": episodes
        }

    def episode_loader(self, episode_info, quality_preference="high"):
        try:
            episode_url = episode_info["url"]
            episode_response = self.session.get(episode_url)
            video_url_match = re.search(r'"video_url":"([^"]+)"', html.unescape(episode_response.text))

            if not video_url_match:
                raise ValueError("Could not find video URL in episode response")

            self.player_url = video_url_match.group(1).replace("\\/", "/")
            self.player_response = self.session.get(self.player_url)
            self.player_match = re.findall(r"var\s+video_sources\s*=\s*(\[[\s\S]*?\]);", self.player_response.text)

            if not self.player_match or len(self.player_match) < 2:
                raise ValueError("Could not find video sources in player response")

            video_sources = json.loads(self.player_match[1].replace("\\/", "/"))
            qualities = {source["label"]: source["src"] for source in video_sources if source["src"]}

            if quality_preference == "high":
                best_quality = max(qualities.keys(), key=lambda x: int(re.search(r'(\d+)', x).group(1)))
                return qualities[best_quality]
            elif quality_preference == "mid":
                mid_quality = sorted(qualities.keys(), key=lambda x: int(re.search(r'(\d+)', x).group(1)))[len(qualities) // 2]
                return qualities[mid_quality]
            elif quality_preference == "low":
                low_quality = min(qualities.keys(), key=lambda x: int(re.search(r'(\d+)', x).group(1)))
                return qualities[low_quality]
        except Exception as e:
            raise Exception(f"Error in episode_loader: {str(e)}")




