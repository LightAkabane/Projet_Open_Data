# imdb_client.py

import os
from typing import Optional, Dict, Any

import requests


class IMDbClient:
    BASE_URL = "https://imdb8.p.rapidapi.com"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("RAPIDAPI_IMDB_KEY")
        if not self.api_key:
            raise ValueError("Aucune clé RapidAPI IMDb fournie (RAPIDAPI_IMDB_KEY).")

    def _get(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "imdb8.p.rapidapi.com",
        }
        url = f"{self.BASE_URL}{path}"
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def _clean_tconst(imdb_id: str) -> str:
        """
        Accepte :
        - 'tt0796366'
        - '/title/tt0796366/'
        - 'title/tt0796366/'
        et renvoie toujours 'tt0796366'
        """
        imdb_id = imdb_id.strip()
        if imdb_id.startswith("/title/"):
            imdb_id = imdb_id[len("/title/"):]
        if imdb_id.startswith("title/"):
            imdb_id = imdb_id[len("title/"):]
        imdb_id = imdb_id.strip("/")
        return imdb_id

    def get_ratings(self, imdb_id: str) -> Dict[str, Any]:
        """
        ⚠️ On utilise le même endpoint que dans ton JS :
        GET /title/get-ratings?tconst=ttXXXXXXX
        => retourne { rating, ratingCount, ratingsHistograms, ... }
        """
        tconst = self._clean_tconst(imdb_id)
        return self._get("/title/get-ratings", params={"tconst": tconst})

    def get_business(self, imdb_id: str) -> Dict[str, Any]:
        """
        Pour le box office : on reste sur la v2 comme dans ton exemple JSON
        GET /title/v2/get-business?tconst=ttXXXXXXX
        """
        tconst = self._clean_tconst(imdb_id)
        return self._get("/title/v2/get-business", params={"tconst": tconst})
