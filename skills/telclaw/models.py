from dataclasses import dataclass

@dataclass
class CommandRequest:
    id: str
    user_id: str
    command: str
    args: dict
    risk: int
    status: str
    timestamp: str

@dataclass
class Approval:
    id: str
    command_id: str
    approver_id: str
    timestamp: str
    decision: str
    rationale: str

@dataclass
class ExecutionResult:
    command_id: str
    success: bool
    output: str
    error: str
    timestamp: str
