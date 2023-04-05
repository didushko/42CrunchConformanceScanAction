import requests
import time
import base64
import json
import docker


class ScanService:
    def __init__(self, api_key, platform_url):
        self.api_key = api_key
        self.platform_url = platform_url
        self.headers = _getHeaders(api_key)

    def read_default_scanId(self, api_id):
        MAX_RETRY_TIME = 30
        RETRY_TIME = 1
        url = _getUrl(
            f"api/v2/apis/{api_id}/scanConfigurations", self.platform_url)

        start_time = time.time()
        while time.time() <= start_time + MAX_RETRY_TIME:
            response = requests.get(url, headers=self.headers)
            if response.ok and len(response.json().get("list", [])) > 0:
                return response.json()["list"][0]["configuration"]["id"]
            else:
                time.sleep(RETRY_TIME)

        raise Exception(f"Can't read list configuration for api_id {api_id}")

    def create_default_scan_configuration(self, api_id):
        url = _getUrl(
            f"api/v2/apis/{api_id}/scanConfigurations/default", self.platform_url
        )
        data = {"name": "defailt"}
        response = requests.post(url, headers=self.headers, json=data)
        if response.ok:
            response_json = response.json()
            return response_json.get("id")
        else:
            raise Exception(
                f"Can't get configuration for api with id {api_id}, error: {response.text}"
            )

    def read_scan_configuration(self, configId):
        url = _getUrl(
            f"api/v2/scanConfigurations/{configId}", self.platform_url)
        response = requests.get(url, headers=self.headers)
        if response.ok:
            return response.json()
        else:
            raise Exception(
                f"Can't read scan configuration with id {configId}, error: {response.text}"
            )

    def waitScanReport(self, api_id):
        MAX_RETRY_TIME = 30
        RETRY_TIME = 1
        url = _getUrl(f"api/v2/apis/{api_id}/scanReports", self.platform_url)

        start_time = time.time()
        while time.time() <= start_time + MAX_RETRY_TIME:
            response = requests.get(url, headers=self.headers)
            if response.ok and len(response.json().get("list", [])) > 0:
                return response.json()["list"][0]["report"]["taskId"]
            else:
                time.sleep(RETRY_TIME)

        raise Exception(
            f"Can't read list scanReports for api_id {api_id}, response = {response.text}"
        )

    def readScanReport(self, taskId):
        url = _getUrl(f"api/v2/scanReports/{taskId}", self.platform_url)
        response = requests.get(url, headers=self.headers)
        if response.ok:
            return json.loads(
                base64.b64decode(response.json()["file"].encode("utf-8")).decode(
                    "utf-8"
                )
            )
        else:
            raise Exception(
                f"Can't read scan report with id {taskId}, error: {response.text}"
            )

    def runScanDocker(self, scan_token, serviseApi):
        client = docker.from_env()
        env_vars = {
            "SCAN_TOKEN": scan_token,
            "PLATFORM_SERVICE": serviseApi,
        }
        container = client.containers.run(
            "42crunch/scand-agent:v2.0.0-rc05", environment=env_vars, detach=True
        )
        container.wait()
        print(container.logs().decode("utf-8"))

    def getScanSQGS(self):
        url = _getUrl("/api/v2/sqgs/scan", self.platform_url)
        response = requests.get(url, headers=self.headers)
        if response.ok:
            return response.json()
        else:
            raise Exception(f"Can't read scan sqg's: {response.text}")

    def getScanCompliance(self, taskId):
        url = _getUrl("/api/v2/sqgs/reportComplianceStatus", self.platform_url)
        response = requests.get(
            url, headers=self.headers, params={
                "reportType": "scan", "taskId": taskId}
        )
        if response.ok:
            return response.json()
        else:
            raise Exception(
                f"Can't read sqg compliance for task {taskId}: {response.text}")
    def checkSqg(self, sqgs, compl):
        if "processingDetails" in compl:
            errors = []
            for details in compl["processingDetails"]:
                for sqg in sqgs["list"]:
                    if sqg["id"] == details["blockingSqgId"]:
                        name = sqg["name"]
                        blockingRules = details["blockingRules"]
                        errors.append(
                            f"Fail SQG \"{name}\" blocking by rules: {blockingRules}")
            if len(errors) > 0:
                errors = '\n'.join(str(item) for item in errors)
                raise Exception(f"Fails next scan SQG's: \n{errors}")
        print("All SQG's pass successfull")



def _getHeaders(api_key):
    return {"Content-Type": "application/json", "X-API-KEY": api_key}


def _getUrl(path, platformUrl):
    return platformUrl + "/" + path

