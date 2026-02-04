import requests
from src.utils.logger import get_logger
from src.utils.retry_decorator import retry
import allure

class BaseClient:
    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url
        self.session = requests.Session()
        self.timeout = timeout
        self.logger = get_logger()

    @retry(max_retries=3, delay=2)
    def get(self, endpoint: str, params=None):
        url = f"{self.base_url}{endpoint}"
        self.logger.info(f"GET {url} | params={params}")
        response = self.session.get(url, params=params, timeout=self.timeout)
        self.logger.info(f"Response: {response.status_code}")
        try:
            json_resp = response.json()
            self.logger.info(f"JSON Response: {json_resp}")
            allure.attach(
                str(json_resp),
                name=f"Response for {url}",
                attachment_type=allure.attachment_type.JSON
            )
        except Exception as e:
            self.logger.warning(f"Failed to parse JSON response: {e}")
        return response

    @retry(max_retries=3, delay=2)
    def post(self, endpoint: str, json=None, data=None):
        url = f"{self.base_url}{endpoint}"
        self.logger.info(f"POST {url} | json={json} | data={data}")
        response = self.session.post(url, json=json, data=data, timeout=self.timeout)
        self.logger.info(f"Response: {response.status_code}")
        try:
            json_resp = response.json()
            self.logger.info(f"JSON Response: {json_resp}")
            allure.attach(
                str(json_resp),
                name=f"Response for {url}",
                attachment_type=allure.attachment_type.JSON
            )
        except Exception as e:
            self.logger.warning(f"Failed to parse JSON response: {e}")
        return response

    @retry(max_retries=3, delay=2)
    def put(self, endpoint: str, json=None, data=None):
        url = f"{self.base_url}{endpoint}"
        self.logger.info(f"PUT {url} | json={json} | data={data}")
        response = self.session.put(url, json=json, data=data, timeout=self.timeout)
        self.logger.info(f"Response: {response.status_code}")
        try:
            json_resp = response.json()
            self.logger.info(f"JSON Response: {json_resp}")
            allure.attach(
                str(json_resp),
                name=f"Response for {url}",
                attachment_type=allure.attachment_type.JSON
            )
        except Exception as e:
            self.logger.warning(f"Failed to parse JSON response: {e}")
        return response

    @retry(max_retries=3, delay=2)
    def patch(self, endpoint: str, json=None, data=None):
        url = f"{self.base_url}{endpoint}"
        self.logger.info(f"PATCH {url} | json={json} | data={data}")
        response = self.session.patch(url, json=json, data=data, timeout=self.timeout)
        self.logger.info(f"Response: {response.status_code}")
        try:
            json_resp = response.json()
            self.logger.info(f"JSON Response: {json_resp}")
            allure.attach(
                str(json_resp),
                name=f"Response for {url}",
                attachment_type=allure.attachment_type.JSON
            )
        except Exception as e:
            self.logger.warning(f"Failed to parse JSON response: {e}")
        return response

    @retry(max_retries=3, delay=2)
    def delete(self, endpoint: str):
        url = f"{self.base_url}{endpoint}"
        self.logger.info(f"DELETE {url}")
        response = self.session.delete(url, timeout=self.timeout)
        self.logger.info(f"Response: {response.status_code}")
        try:
            json_resp = response.json()
            self.logger.info(f"JSON Response: {json_resp}")
            allure.attach(
                str(json_resp),
                name=f"Response for {url}",
                attachment_type=allure.attachment_type.JSON
            )
        except Exception as e:
            self.logger.warning(f"Failed to parse JSON response: {e}")
        return response
