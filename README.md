
# BGP ORIGIN VALIDATION AS A TRUST DIMENSION
## An extension to BGP Trust-Aware Routing Simulator

An extension to the comprehensive CLI BGP routing simulator with integrated origin legitimacy validation that combines protocol-level security analysis with trust-based routing decisions. This is a Python-based gRPC service that validates the legitimacy of BGP route announcements through multi-source verification. Designed to integrate with BGP simulators and routing systems to detect route hijacks, unauthorized announcements, and other origin-based attacks.

### Architecture Overview

```text
+-----------------------------------+
|     C++ BGP Simulator (CLI)       |
| - Route processing                |
| - BGP state machine               |
| - Performance-critical logic      |
| - Trust Score Calculation         |
+-----------------------------------+
          |
          || Protocol Buffers
          || (Unix socket / Named pipe)
          v
+-----------------------------------+
|    Legitimacy Query Interface     |
| - Send announcements for validation|
| - Receive legitimacy verdicts     |
| - Trust penalties for illegit routes|
+-----------------------------------+
          |
          || gRPC
          v
+-----------------------------------+
|   Python Trust Engine Service     |
| - Origin legitimacy               |
| - RPKI validation (crypto proof)  |
| - IRR database queries            |
| - Origin pattern analysis         |
| - AS relationships possible?      |
+-----------------------------------+
