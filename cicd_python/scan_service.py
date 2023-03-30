import requests
import time
import docker
import base64
import json
import os


api_key = os.environ['api-token']
base_url = os.environ['platform-url']
headers = {
    "Content-Type": "application/json",
    "X-API-KEY": api_key,
    "X-42C-IDE": "true"
}


def _getUrl(str):
    return base_url+str


def create_default_scan_configuration(api_id):
    url = _getUrl("api/v2/apis/{}/scanConfigurations/default".format(api_id))
    data = {
        "name": "test"
    }
    response = requests.post(url, headers=headers, json=data)
    if response.ok:
        response_json = response.json()
        return response_json.get('id')
    else:
        raise Exception("Can't get configuration for api with id {}, error: {})".format(
            api_id, response.text))


def read_scan_configuration(configId):
    url = _getUrl("api/v2/scanConfigurations/{}".format(configId))
    response = requests.get(url, headers=headers)
    if response.ok:
        return response.json()
    else:
        raise Exception("Can't read scan configuration with id {}, error: {})".format(
            configId, response.text))


def read_default_scanId(api_id):
    MAX_RETRY_TIME = 30
    RETRY_TIME = 1
    url = _getUrl("api/v2/apis/{}/scanConfigurations".format(api_id))

    start_time = time.time()
    while time.time() <= start_time + MAX_RETRY_TIME:
        response = requests.get(url, headers=headers)
        if response.ok and len(response.json().get('list', [])) > 0:
            return response.json()['list'][0]['scanConfigurationId']
        else:
            time.sleep(RETRY_TIME)

    raise Exception(
        "Can't read list configuration for api_id {}".format(api_id))


def getScanToken(api_id):
    create_default_scan_configuration(api_id)
    scanId = read_default_scanId(api_id)
    scanConfiguration = read_scan_configuration(scanId)
    token = scanConfiguration['scanConfigurationToken']
    print("token for {} is {}".format(api_id, token))
    return token


def runScanDocker(scan_token, api_id):
    client = docker.from_env()
    env_vars = {'SCAN_TOKEN': scan_token,
                'PLATFORM_SERVICE': 'services.42crunch.com:8001'}
    container = client.containers.run(
        '42crunch/scand-agent:v2.0.0-rc05', environment=env_vars, detach=True)
    # container = client.containers.run(
    #     'hello-world', environment=env_vars, detach=True)
    print(container.logs().decode('utf-8'))
    reportId = waitScanReport(api_id)
    print("ReportId {}".format(reportId))
    return readScanReport(reportId)


def waitScanReport(api_id):
    MAX_RETRY_TIME = 30
    RETRY_TIME = 1
    url = _getUrl("api/v2/apis/{}/scanReports".format(api_id))

    start_time = time.time()
    while time.time() <= start_time + MAX_RETRY_TIME:
        response = requests.get(url, headers=headers)
        if response.ok and len(response.json().get('list', [])) > 0:
            return response.json()["list"][0]['taskId']
        else:
            time.sleep(RETRY_TIME)

    raise Exception(
        "Can't read list snacReports for api_id {}, response = {}".format(api_id, response))


def readScanReport(taskId):
    url = _getUrl("api/v2/scanReports/{}".format(taskId))
    response = requests.get(url, headers=headers)
    return json.loads(base64.b64decode(response.json()["data"].encode("utf-8")).decode("utf-8"))

def getScanSQGS():
    url = _getUrl("/api/v2/sqgs/scan")
    response = requests.get(url, headers=headers)
