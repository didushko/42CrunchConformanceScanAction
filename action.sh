#!/bin/bash

if [ -n "$command" ]; then
  eval "$command"
else
  xliic_scan --api_key=$api_token --platform_url=$platform_url json-report check-sqg $report_path
fi
