from sigma.collection import SigmaCollection
from sigma.backends.opensearch.opensearch_ppl import OpenSearchPPLBackend

backend = OpenSearchPPLBackend()
c = SigmaCollection.from_yaml(r"""
title: "wazuh opensearch sigma test - Manager Started"
status: test
id: 32bc608c-67ab-4d58-8361-35d3baac726c
logsource:
    product: wazuh
    category: indexer
detection:
    sel:
        rule_id: 502
    condition: 1 of sel
custom:
    opensearch_ppl_min_time: "-5m"
    opensearch_ppl_max_time: "now"
""")

print(backend.convert(c)[0])
