import cicd_python.report_service as report_service
import cicd_python.scan_service as scan_service
import argparse
import json
import cicd_python.sarif_service as sarif_service


def main():
    # command argument switch setup
    parser = argparse.ArgumentParser(
        description='This program will automate the cyclondex scan finding export to DefectDojo. ')
    parser.add_argument('-k', '--key', help='42Crunch API key',  required=True)
    parser.add_argument('-rp', '--reportPath',
                        help='report path',  required=True)
    parser.add_argument('-pu', '--platformUrl', help='(Optional) Platform url',
                        default="https://platform.42crunch.com", required=False)
    args = parser.parse_args()

    path_to_report = args.reportPath
    platformSettings = {
        "api_key": args.key,
        "base_url": args.platformUrl
    }
    print(f"Platform url: {platformSettings['base_url']}")
    print(f"Path to report: {path_to_report}")

    audited = report_service.read_audited_ids_from_report(path_to_report)
    scanReports = {}
    for file, api_id in audited.items():
        print(file)
        scan_token = scan_service.getScanToken(api_id, platformSettings)
        report = scan_service.runScanDocker(
            scan_token, api_id, platformSettings)
        scanReports[file] = report
    scan_service.getScanSQGS(platformSettings)
    sarif = sarif_service.produceSarifFromScanReports(scanReports)
    with open("report.sarif", "w") as outfile:
        json.dump(sarif, outfile, indent=4)


if __name__ == '__main__':
    main()
