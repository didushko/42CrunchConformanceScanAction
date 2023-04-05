#!/bin/bash

if [ -n "$command" ]; then
  eval "$command"
else
  xliic_scan json-report check-sqg $report_path
fi
