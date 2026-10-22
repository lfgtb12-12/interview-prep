"""M03-L07: deterministic checkpoint and ambiguous-provider-write exercise.

An in-memory simulator; it does NOT supply database durability or exactly-once delivery.
"""
from dataclasses import dataclass


@dataclass
class Operation:
    operation_id: str
    payload_digest: str
    state: str = "PENDING"
    version: int = 0
    owner: str | None = None
    provider_key: str | None = None


class FakeProvider:
    def __init__(self):
        self.accepted: dict[str, str] = {}
        self.effect_count = 0

    def send(self, key: str, digest: str, *, lose_ack=False) -> str:
        if key in self.accepted:
            if self.accepted[key] != digest:
                raise ValueError("idempotency key reused with different payload")
            return "accepted"
        self.accepted[key] = digest
        self.effect_count += 1
        if lose_ack:
            raise TimeoutError("provider accepted operation; response lost")
        return "accepted"

    def lookup(self, key: str) -> bool:
        return key in self.accepted


def claim(operation: Operation, worker: str, expected_version: int) -> int:
    if operation.state != "PENDING" or operation.version != expected_version:
        raise ValueError("stale claim or invalid state")
    operation.state = "CLAIMED"
    operation.owner = worker
    operation.version += 1
    return operation.version


def dispatch(operation: Operation, worker: str, version: int,
             provider: FakeProvider, *, lose_ack=False) -> None:
    if operation.state != "CLAIMED" or operation.owner != worker or operation.version != version:
        raise ValueError("stale execution attempt")
    key = operation.provider_key or operation.operation_id
    operation.provider_key = key
    try:
        provider.send(key, operation.payload_digest, lose_ack=lose_ack)
    except TimeoutError:
        operation.state = "UNKNOWN"
        operation.version += 1
        return
    operation.state = "SUCCEEDED"
    operation.version += 1


def reconcile(operation: Operation, provider: FakeProvider) -> bool:
    if operation.state != "UNKNOWN" or not operation.provider_key:
        raise ValueError("only UNKNOWN operations with stable keys can reconcile")
    if provider.lookup(operation.provider_key):
        operation.state = "SUCCEEDED"
        operation.version += 1
        return True
    # Absence at lookup is not proof of failed delivery in a real distributed system.
    return False
