# MCP-AIP Bridge

Production-grade bidirectional bridge between Model Context Protocol (MCP) and Agentic Interop Platform (AIP).

## Features

✅ **Protocol Translation**: MCP ⇄ AIP with UIR conversion  
✅ **Deterministic Threading**: UUID v5 from method+request_id  
✅ **Idempotency**: Transaction log prevents duplicate processing  
✅ **Canonical Signatures**: Ed25519 signing with JCS canonicalization  
✅ **Preflight Security**: Policy checks at gateway ingress  
✅ **Memory Sync**: Shared semantic memory with backpressure handling  
✅ **Observability**: OpenTelemetry traces + Prometheus metrics  

## Quick Start

```bash
# Setup
./scripts/setup.sh

# Run tests
pytest tests/

# Start bridge
docker-compose up -d

# Run test harness
python scripts/test-harness.py

# Check metrics
curl http://localhost:9090/metrics
```

## Configuration

Edit `configs/bridge.yaml` for:

- Security policies
- Memory sync settings
- Retry behavior
- Observability config

## Testing

```bash
# Unit tests
pytest tests/test_translator.py -v

# Integration tests  
pytest tests/test_idempotency.py -v

# Load test (1k req/min)
python scripts/load-test.py --rate 1000 --duration 60

# Chaos test
docker-compose kill nats
# Wait 10s, restart
docker-compose up -d nats
# Verify queue drains
```

## Production Checklist

- [ ] Generate Ed25519 keypair for signing
- [ ] Configure mTLS certificates
- [ ] Set up OPA policies
- [ ] Configure memory size limits
- [ ] Enable distributed tracing
- [ ] Set appropriate rate limits
- [ ] Configure disk queue for backpressure
- [ ] Test failover scenarios

## Metrics SLOs

- P95 translation latency < 25ms
- End-to-end bridge latency < 500ms
- Zero duplicate deliveries
- 99.9% schema validation success

## Next Steps

```bash
# Initialize the project
cd mcp-aip-bridge
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run local tests
pytest tests/ -v

# Start full stack
docker-compose up -d

# Monitor
docker-compose logs -f mcp-bridge
```

This production-ready scaffold implements hardening requirements for deterministic threading, canonical signatures, and preflight policy checks.
