import os
import requests

Token = ""
Movie_api = ""
class OMDB:
    def __init__(self, api_key):
        # self.youtube_api = os.getenv("youtube_api")
        self.api_key = Movie_api
        self.url = "http://www.omdbapi.com/?apikey=" + self.api_key
        self.poster_url = "http://img.omdbapi.com/?apikey=" + self.api_key

    def movie_info(self, movieTitle):
        param = {"api_key": self.api_key, "t": movieTitle}
        response = requests.get(self.url, param).json()

        if response.get("Response") != "True":
            return None

        movie_info = {}
        movie_info["title"] = response.get("Title")
        movie_info["year"] = response.get("Year")
        movie_info["plot"] = response.get("Plot")
        movie_info["actors"] = response.get("Actors")
        movie_info["ratings"] = response.get("Ratings")
        movie_info["imdb_ratings"] = response.get("imdbRating")
        movie_info['poster'] = response.get('Poster')

        # Fetch the YouTube trailer link
        youtube_trailer_url = self.fetch_youtube_trailer(response.get("imdbID"))
        movie_info["youtube_trailer"] = youtube_trailer_url

        return movie_info

    def fetch_youtube_trailer(self, imdb_id):
        youtube_url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "key": self.api_key,  # Use your actual YouTube API key
            "q": f"{imdb_id} trailer",
            "part": "id",
            "maxResults": 1,
            "type": "video"
        }
        response = requests.get(youtube_url, params=params).json()

        if "items" in response and len(response["items"]) > 0:
            video_id = response["items"][0]["id"]["videoId"]
            youtube_trailer_link = f"https://www.youtube.com/watch?v={video_id}"
            return youtube_trailer_link

        return None
