import report_service
import scan_service
import os
import json
import sarif_service

path_to_report = os.environ['report-path']

audited = report_service.read_audited_ids_from_report("path_to_report")
scanReports = {}
for api_id in audited:
    scan_token = scan_service.getScanToken(api_id)
    report = scan_service.runScanDocker(scan_token, api_id)
    scanReports[api_id] = report
scan_service.getScanSQGS()
sarif = sarif_service.produceSarifFromScanReports(scanReports)
with open("report.sarif".format(api_id), "w") as outfile:
    json.dump(sarif, outfile, indent=4)
