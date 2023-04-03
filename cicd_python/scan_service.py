import requests
import time
import docker
import base64
import json


def _getHeaders(config):
    return {
        "Content-Type": "application/json",
        "X-API-KEY": config["api_key"]
    }


def _getUrl(path, config):
    return config["base_url"]+"/"+path


def create_default_scan_configuration(api_id, config):
    url = _getUrl(
        "api/v2/apis/{}/scanConfigurations/default".format(api_id), config)
    data = {
        "name": "defailt"
    }
    response = requests.post(url, headers=_getHeaders(config), json=data)
    if response.ok:
        response_json = response.json()
        return response_json.get('id')
    else:
        raise Exception("Can't get configuration for api with id {}, error: {})".format(
            api_id, response.text))


def read_scan_configuration(configId, config):
    url = _getUrl("api/v2/scanConfigurations/{}".format(configId), config)
    response = requests.get(url, headers=_getHeaders(config))
    if response.ok:
        return response.json()
    else:
        raise Exception("Can't read scan configuration with id {}, error: {})".format(
            configId, response.text))


def read_default_scanId(api_id, config):
    MAX_RETRY_TIME = 30
    RETRY_TIME = 1
    url = _getUrl("api/v2/apis/{}/scanConfigurations".format(api_id), config)

    start_time = time.time()
    while time.time() <= start_time + MAX_RETRY_TIME:
        response = requests.get(url, headers=_getHeaders(config))
        if response.ok and len(response.json().get('list', [])) > 0:
            return response.json()['list'][0]['scanConfigurationId']
        else:
            time.sleep(RETRY_TIME)

    raise Exception(
        "Can't read list configuration for api_id {}".format(api_id))


def getScanToken(api_id, config):
    create_default_scan_configuration(api_id, config)
    scanId = read_default_scanId(api_id, config)
    scanConfiguration = read_scan_configuration(scanId, config)
    token = scanConfiguration['scanConfigurationToken']
    print("token for {} is {}".format(api_id, token))
    return token


def runScanDocker(scan_token, api_id, config):
    client = docker.from_env()
    env_vars = {'SCAN_TOKEN': scan_token,
                'PLATFORM_SERVICE': 'services.42crunch.com:8001'}
    container = client.containers.run(
        '42crunch/scand-agent:v2.0.0-rc05', environment=env_vars, detach=True)
    container.wait()
    print(container.logs().decode('utf-8'))
    reportId = waitScanReport(api_id, config)
    print("ReportId {}".format(reportId))
    return readScanReport(reportId, config)


def waitScanReport(api_id, config):
    MAX_RETRY_TIME = 30
    RETRY_TIME = 1
    url = _getUrl("api/v2/apis/{}/scanReports".format(api_id), config)

    start_time = time.time()
    while time.time() <= start_time + MAX_RETRY_TIME:
        response = requests.get(url, headers=_getHeaders(config))
        if response.ok and len(response.json().get('list', [])) > 0:
            return response.json()["list"][0]['taskId']
        else:
            time.sleep(RETRY_TIME)

    raise Exception(
        "Can't read list snacReports for api_id {}, response = {}".format(api_id, response))


def readScanReport(taskId, config):
    url = _getUrl("api/v2/scanReports/{}".format(taskId), config)
    response = requests.get(url, headers=_getHeaders(config))
    if response.ok:
        return json.loads(base64.b64decode(response.json()["data"].encode("utf-8")).decode("utf-8"))
    else:
        raise Exception("Can't read scan report with id {}, error: {})".format(
            taskId, response.text))


def getScanSQGS(config):
    url = _getUrl("/api/v2/sqgs/scan", config)
    response = requests.get(url, headers=_getHeaders(config))
