# tmdb_client.py

import os
import requests
import pandas as pd
from typing import List, Dict, Any

class TMDBClient:
    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(
        self,
        api_key_v3: str | None = None,
        read_token_v4: str | None = None,
        language: str = "fr-FR",
    ):
        self.api_key_v3 = api_key_v3 or os.getenv("TMDB_API_KEY")
        self.read_token_v4 = read_token_v4 or os.getenv("TMDB_API_READ_TOKEN")
        if not self.api_key_v3 and not self.read_token_v4:
            raise ValueError("Aucune clé TMDB fournie (v3 ou v4).")
        self.language = language

    def _get(self, endpoint: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        if params is None:
            params = {}
        params["language"] = self.language

        headers = {"accept": "application/json"}

        if self.api_key_v3:
            params["api_key"] = self.api_key_v3
        else:
            headers["Authorization"] = f"Bearer {self.read_token_v4}"

        url = f"{self.BASE_URL}{endpoint}"
        resp = requests.get(url, params=params, headers=headers)
        resp.raise_for_status()
        return resp.json()

    def get_genre_map(self) -> Dict[int, str]:
        data = self._get("/genre/movie/list")
        return {g["id"]: g["name"] for g in data.get("genres", [])}
    
    def get_now_playing_movies(self, nb_pages: int = 2) -> list[dict]:
        """Derniers films sortis en salle (now_playing)."""
        results = []
        for page in range(1, nb_pages + 1):
            data = self._get("/movie/now_playing", params={"page": page})
            results.extend(data.get("results", []))
        return results
    
    def get_popular_movies(self, nb_pages: int = 3) -> List[Dict[str, Any]]:
        results = []
        for page in range(1, nb_pages + 1):
            data = self._get("/movie/popular", params={"page": page})
            results.extend(data.get("results", []))
        return results

    def get_movie_details(self, movie_id: int) -> Dict[str, Any]:
        """Détails complets d'un film (budget, revenue, runtime, etc.)."""
        return self._get(f"/movie/{movie_id}")

    def movies_to_dataframe(self, movies: List[Dict[str, Any]], genre_map: Dict[int, str]) -> pd.DataFrame:
        rows = []
        for m in movies:
            genres = [genre_map.get(gid, str(gid)) for gid in m.get("genre_ids", [])]
            rows.append(
                {
                    "id": m.get("id"),
                    "title": m.get("title"),
                    "original_title": m.get("original_title"),
                    "release_date": m.get("release_date"),
                    "release_year": int(m["release_date"][:4]) if m.get("release_date") else None,
                    "vote_average": m.get("vote_average"),
                    "vote_count": m.get("vote_count"),
                    "popularity": m.get("popularity"),
                    "original_language": m.get("original_language"),
                    "genres": genres,
                    "genres_str": ", ".join(genres),
                    "poster_path": m.get("poster_path"),
                }
            )
        return pd.DataFrame(rows)

    @staticmethod
    def build_poster_url(poster_path: str | None, size: str = "w342") -> str | None:
        if not poster_path:
            return None
        return f"https://image.tmdb.org/t/p/{size}{poster_path}"
