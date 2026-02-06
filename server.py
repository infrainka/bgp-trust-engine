import grpc
from concurrent import futures
import sys
import os
import config
import route_trust_pb2
import route_trust_pb2_grpc

class RouteTrustServicer(route_trust_pb2_grpc.TrustEngineServicer):
    def __init__(self):
        self.mock_db = {}

        if config.IS_MOCK_MODE:
            self._load_topology_truth(config.TOPOLOGY_FILE)

    def _load_topology_truth(self, filepath):
        """Parsing the topology file to load mock data."""
        print(f"[DEBUG] Attempting to load topology from: '{filepath}'")
        if not os.path.exists(filepath):
            print(f"[Error] Topology file not found: {filepath}")
            return
        
        print(f"[Info] Loading topology from {filepath}...")
        try:
            with open(filepath, 'r') as f:
                in_prefix_section = False
                line_count = 0
                for line in f:
                    line_count += 1
                    original_line = line
                    line = line.strip()
                    # print(f"[DEBUG] Line {line_count}: '{line}'") # Verbose: Uncomment if needed

                    if line.startswith("#") or not line:
                        continue

                    if line == "[Prefixes]":
                        print(f"[DEBUG] Found [Prefixes] section at line {line_count}")
                        in_prefix_section = True
                        continue
                    elif line.startswith("[") and line.endswith("]"):
                        if in_prefix_section:
                            print(f"[DEBUG] Leaving [Prefixes] section at line {line_count} (Found '{line}')")
                        in_prefix_section = False
                        continue

                    if in_prefix_section:
                        parts = line.split()
                        if len(parts) >= 2:
                            try:
                                asn = int(parts[0])
                                prefix = parts[1]
                                self.mock_db[prefix] = asn
                                print(f"   🔹 Learned Valid Origin: {prefix} -> AS{asn}")
                            except ValueError:
                                print(f"[Warning] Failed to parse prefix line {line_count}: {line}")
                        else:
                             print(f"[Warning] Malformed prefix line {line_count}: {line}")

            print(f"[Info] Finished loading topology. {len(self.mock_db)} valid routes known.")
            print(f"[DEBUG] Mock DB Content: {self.mock_db}")

        except Exception as e:
            print(f"[Error] Failed to load topology: {e}")

    def ValidateRoute(self, request, context):
        cidr = f"{request.prefix_address}/{request.prefix_length}"
        origin_asn = request.as_path[-1] if request.as_path else 0

        print(f"[Check] Validating {cidr} via AS{origin_asn}...")

        if config.IS_MOCK_MODE:
            # Is the prefix defined in our topology?
            if cidr not in self.mock_db:
                print(f"Verdict: UNKNOWN prefix (Not in topology)")
                return route_trust_pb2.TrustReply(
                    is_legit=False,
                    trust_score_penalty=0.5, # Medium penalty for unknown garbage
                    reason="Prefix not allocated in topology"
                )

            # Does the Origin AS match the owner in topology?
            expected_asn = self.mock_db[cidr]
            
            if origin_asn == expected_asn:
                print(f"✅ Verdict: VALID")
                return route_trust_pb2.TrustReply(
                    is_legit=True,
                    trust_score_penalty=0.0,
                    reason="Valid Origin (Mock)"
                )
            else:
                print(f"Verdict: HIJACK DETECTED! Expected AS{expected_asn}, got AS{origin_asn}")
                return route_trust_pb2.TrustReply(
                    is_legit=False,
                    trust_score_penalty=1.0, # MAX Penalty
                    reason=f"Origin Mismatch: Expected AS{expected_asn}"
                )

        else:
            # Placeholder 'for Real RPKI logic
            return route_trust_pb2.TrustReply(is_legit=True, trust_score_penalty=0.0)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    route_trust_pb2_grpc.add_TrustEngineServicer_to_server(RouteTrustServicer(), server)
    port = config.GRPC_PORT
    # Using insecure port for development/testing. TLS can be added when integrating real RPKI.
    server.add_insecure_port(f'[::]:{port}')
    print(f"Trust Engine started on port {port}")
    print(f"   Mode: {'MOCK (Using topology.conf)' if config.IS_MOCK_MODE else 'REAL (Live RPKI)'}")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()