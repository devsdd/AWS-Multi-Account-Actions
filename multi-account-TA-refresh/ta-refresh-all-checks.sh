#!/bin/sh

# check whether credentials file has profiles or config?

# profiles=`awk '/^\[/ {print $NF}' ~/.aws/config | tr -d ']'`

# get list of all checks and refresh each one (bulk refresh not currently supported)
# region hardcoded to us-east-1 since support API currently served only from that region
aws support describe-trusted-advisor-checks --region us-east-1 --language en | jq '.[][].id' | tr -d '"'  | \
	while read check_id
		do aws support --region us-east-1 refresh-trusted-advisor-check --check-id $check_id
	done
