import json
from time import sleep
from typing import Optional

import requests
import cloudscraper
from bs4 import BeautifulSoup

from .exceptions import (
    KotoboConnectionError,
    KotoboTooManyRequestsError,
    KotoboNotLoginException,
    KotoboUndefinedCategoryException,
)


class KotoboAPI:
    def __init__(self, email: str, password: str, tz_offset: int = -540) -> None:
        self.email: str = email
        self.password: str = password
        self.cf_req = cloudscraper.CloudScraper()
        self.req = requests.session()
        self.BASE_URL: str = "https://kotobo.app"
        self.token: Optional[str] = None
        self.already_login: bool = False
        self.tz_offset: int = tz_offset  # -540min / 60min = -9h (JST -> UTC)?
    
    def _cf_request(self, path: str, param: Optional[dict] = None,
                    headers: Optional[dict] = None, method: str = "GET", ):
        url: str = f"{self.BASE_URL}/{path}"
        if headers is None:
            ua: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
            headers: dict = {"User-Agent": ua, "referer": url}
        return self.cf_req.request(url=url, method=method, data=param, headers=headers)
    
    def _requests(self, path: str, param: Optional[dict] = None,
                  headers: Optional[dict] = None, method: str = "GET", ):
        if headers is None:
            ua: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
            headers: dict = {"User-Agent": ua}
        url: str = f"{self.BASE_URL}/{path}"
        return self.req.request(url=url, method=method, data=param, headers=headers)
    
    def login(self) -> None:
        res = self._cf_request("login")
        bs = BeautifulSoup(res.text, "lxml")
        self.token = bs.find("input", attrs={"name": "_token", "type": "hidden"})["value"]
        param: dict = {
            "email": self.email,
            "password": self.password,
            "_token": self.token,
        }
        sleep(1)
        res = self._cf_request(path="login", method="POST", param=param)
        if "認証情報と一致するレコードがありません。" in res.text:
            raise KotoboConnectionError("Error connecting")
        elif res.status_code == 429:
            raise KotoboTooManyRequestsError("Too many requests")
        self.req.cookies = self.cf_req.cookies
        self.already_login = True
        sleep(1)
    
    def _login_check(self) -> None:
        if not self.already_login:
            raise KotoboNotLoginException("You must be logged in to operate the API.")
    
    def _categories(self):
        self._login_check()
        res = self._requests("categories")
        sleep(1)
        return BeautifulSoup(res.text, "lxml")
    
    def get_category(self) -> dict:
        bs = self._categories()
        records = bs.find_all("tr")
        category: dict = {}
        for n, record in enumerate(records):
            category[n] = record.find("th").text
        return category
    
    def delete_category(self, tar_category: str):
        bs = self._categories()
        records = bs.find_all("tr")
        for record in records:
            read_category = record.find("th").text
            if read_category == tar_category:
                form = record.find("form")
                path = form["action"].lstrip("/")
                token = form.find("input", attrs={"name": "_token", "type": "hidden"})["value"]
                param: dict = {
                    "_method": "DELETE",
                    "_token": token,
                }
                print(param, path)
                return self._requests(path=path, method="POST", param=param)
        print("The target Category was not found")
    
    def edit_category(self, tar_category: str, new_name: str):
        bs = self._categories()
        records = bs.find_all("tr")
        for record in records:
            read_category = record.find("th").text
            if read_category == tar_category:
                edit = record.find("a")["href"].lstrip("/")
                res = self._requests(edit)
                sleep(1)
                bs = BeautifulSoup(res.text, "lxml")
                token = bs.find("input", attrs={"name": "_token", "type": "hidden"})["value"]
                param = {
                    "_method": "PUT",
                    "_token": token,
                    "name": new_name,
                }
                return self._requests(
                    edit.replace("/edit", ""),
                    method="POST",
                    param=param
                )
        print("The target Category was not found")
    
    def create_record(self, category: str, start, end, content: str = "", device_name: str = "MyKotoboDevice"):
        self._login_check()
        res = self._requests("works/create")
        bs = BeautifulSoup(res.text, "lxml")
        category_list: list = [e["value"] for e in bs.find_all("option")]
        if category in category_list:
            raise KotoboUndefinedCategoryException("The specified category has not been defined.")
        self.token = bs.find("input", attrs={"name": "_token", "type": "hidden"})["value"]
        # tz_offset = bs.find("input", attrs={"name": "timezone_offset_min", "type": "hidden"})
        sleep(1)
        param: dict = {
            "_token": self.token,
            "category_name": category,
            "content": content,
            "started_at": f"{start:%Y-%m-%d %H:%M:%S}",
            "finished_at": f"{end:%Y-%m-%d %H:%M:%S}",
            "timezone_offset_min": self.tz_offset,
            "device_name": device_name,
        }
        return self._requests(path="works/", method="POST", param=param)
    
    def get_records(self, start, end):
        self._login_check()
        path: str = f"ajax/works?start_date={start:%Y-%m-%d}&end_date={end:%Y-%m-%d}&timezone_offset_min={self.tz_offset}"
        res = self._requests(path)
        if res.status_code == 200:
            return json.loads(res.text)