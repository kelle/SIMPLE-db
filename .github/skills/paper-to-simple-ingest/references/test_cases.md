# Test Cases

Use these papers to validate the workflow end to end.

## Case A
- URL: https://arxiv.org/abs/2603.24663
- Expected output:
  - ingest plan scoped to this paper only
  - script folder scripts/ingests/2603_24663/
  - script includes publication ingest and data-type ingests identified from the paper

## Case B
- URL: https://arxiv.org/abs/2603.24662
- Expected output:
  - ingest plan scoped to this paper only
  - script folder scripts/ingests/2603_24662/
  - script includes publication ingest and data-type ingests identified from the paper

## Pass Criteria
- Two independent ingest folders are generated.
- Both scripts ingest publication metadata first.
- Mapping and idempotency checks pass for both cases.
