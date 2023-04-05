import click
import x42crunch_python_sdk.src.scan_service as scan_service
import x42crunch_python_sdk.src.report_service as report_service
import x42crunch_python_sdk.src.sarif_service as sarif_service
import json


class Scan:
    def __init__(self, api_key, platform_url):
        self.api_key = api_key
        self.platform_url = platform_url

    def __platform__(self):
        return f"<Platform url:  {self.config.platform_url}>"


pass_scan = click.make_pass_decorator(Scan)


@click.group()
@click.option(
    "--api_key",
    required=True,
    envvar="X42_API_KEY",
    help="Set 42Crunch api key",
)
@click.option(
    "--platform_url",
    envvar="X42_PLATFORM_URL",
    default="https://platform.42crunch.com",
    help="Set 42Crunch platform url",
)
@click.version_option("1.0")
@click.pass_context
def _scan(ctx, api_key, platform_url):
    ctx.obj = Scan(api_key, platform_url)


@click.group("json-report")
def _json_report():
    pass


_scan.add_command(_json_report)


@_json_report.command("convert-to-sarif", short_help="Read scan by API ID")
@click.argument("report_path")
@click.argument("sarif_path")
@pass_scan
def _jsonReportConvertToSarif(scan, report_path, sarif_path):
    """Convert scan report to sarif using audit report json file.
    Need existing scan configuration.
    """
    audited = report_service.read_audited_ids_from_report(report_path)
    scanReports = {}
    scanService = scan_service.ScanService(scan.api_key, scan.platform_url)
    for file, api_id in audited.items():
        print(f"{file} with ApiId {api_id}")
        # scanService.create_default_scan_configuration(api_id)
        # scanId = scanService.read_default_scanId(api_id)
        # scanConfiguration = scanService.read_scan_configuration(scanId)
        # token = scanConfiguration["token"]
        # print(f"Got scan token for Api {api_id}")
        # scanService.runScanDocker(token,"services.dev.42crunch.com:8001")
        reportId = scanService.waitScanReport(api_id)
        report = scanService.readScanReport(reportId)
        scanReports[file] = report
    sarif = sarif_service.produceSarifFromScanReports(scanReports)
    with open(f"{sarif_path}", "w") as outfile:
        json.dump(sarif, outfile, indent=4)


@_json_report.command("check-sqg", short_help="Read scan using audit report json file")
@click.argument("report_path")
@pass_scan
def _byReport(scan, report_path):
    """Check sqg for scan, using audit report json file.
    Need existing scan configuration.
    """
    scanService = scan_service.ScanService(scan.api_key, scan.platform_url)
    audited = report_service.read_audited_ids_from_report(report_path)
    for file, apiId in audited.items():
        taskId = scanService.waitScanReport(apiId)
        compl = scanService.getScanCompliance(taskId)
        with open("compl.json", "w") as outfile:
            json.dump(compl, outfile, indent=4)
    sqgs = scanService.getScanSQGS()
    scanService.checkSqg(sqgs, compl)
