#!/bin/bash

# Define the log file
LOG_FILE="ab_test_log.txt"

# Run the ApacheBench test and append the date and time to the log file
{
  echo "Test run at: $(date)"
  ab -n 1000 -c 700 http://ec2-34-255-118-76.eu-west-1.compute.amazonaws.com:8000/campaigns/21
  echo ""
} >> $LOG_FILE
