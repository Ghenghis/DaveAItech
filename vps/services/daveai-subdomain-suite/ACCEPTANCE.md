# DaveAI Subdomain Acceptance Gates

A route changes from `soon` only after its gate passes in production.

| Service | Production acceptance |
| --- | --- |
| DIY | Auth gate responds; `/health` is 200; scaffold API returns valid multi-file output; browser form renders |
| Dev | Auth gate responds; `/health` is 200; live dependency probe returns named service results |
| Staging | Auth gate responds; `/health` is 200; release gate returns UI hash and route checks |
| Git | Gitea health is 200 locally; external route reaches auth; persistent volume and root URL are configured |
| Database | Adminer is 200 locally; PostgreSQL network is reachable; external route reaches auth |
| Monitor | Prometheus, node-exporter, and Grafana are healthy; external route reaches auth; provisioned dashboard exists |
| Fleet | Auth gate responds; `/health` is 200; process/container inventory is real and redacted |
| WebSocket | HTTPS health is 200; WSS upgrade connects; a test message is echoed with its id |
| Hermes 3D | HTTPS root and health are 200; agent API reports four Brain agents; interactive canvas renders |

Security-sensitive consoles remain `auth`, not `live`. Public safe services
become `live`.
