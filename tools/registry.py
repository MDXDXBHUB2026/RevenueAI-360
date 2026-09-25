"""
RevenueAI 360 - Deterministic Tool Registry
Axiom: "Agents Decide, Tools Execute"
All state mutations, external calls, and database writes are encapsulated
in audited, permission-checked, schema-validated tools.
"""

from typing import Callable, Dict, Any, Type, Optional, List
import time
from datetime import datetime, timezone
from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RetryPolicy(BaseModel):
    max_retries: int = 2
    delay_seconds: float = 1.0
    backoff_multiplier: float = 2.0


class ToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: Type[BaseModel]
    output_schema: Type[BaseModel]
    side_effect: bool = False
    approval_required: bool = False  # If True, enqueues to Tier 2 HITL
    timeout_seconds: int = 30
    retry_policy: RetryPolicy = Field(default_factory=RetryPolicy)
    permission_level: str = "standard"  # read_only, standard, elevated, admin


class ToolExecutionResult(BaseModel):
    tool_name: str
    status: str  # SUCCESS, FAILED, BLOCKED_REQUIRES_APPROVAL
    input_data: Dict[str, Any]
    output_data: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    duration_ms: int = 0
    executed_at: datetime = Field(default_factory=utc_now)


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._handlers: Dict[str, Callable] = {}
        self._execution_history: List[ToolExecutionResult] = []

    def register(self, definition: ToolDefinition, handler: Callable):
        """Register a tool with its schema definition and handler."""
        self._tools[definition.name] = definition
        self._handlers[definition.name] = handler

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def list_tools(self) -> List[ToolDefinition]:
        return list(self._tools.values())

    async def execute(
        self,
        name: str,
        input_args: Dict[str, Any],
        caller_agent: str = "unknown",
        force_bypass_approval: bool = False,
        db_session: Any = None,
    ) -> ToolExecutionResult:
        """
        Executes a registered tool with full input validation, latency tracking,
        and approval enforcement.
        """
        if name not in self._tools:
            return ToolExecutionResult(
                tool_name=name,
                status="FAILED",
                input_data=input_args,
                error_message=f"Tool '{name}' is not registered in ToolRegistry.",
            )

        definition = self._tools[name]

        # Validate input schema
        try:
            validated_input = definition.input_schema.model_validate(input_args)
        except Exception as e:
            return ToolExecutionResult(
                tool_name=name,
                status="FAILED",
                input_data=input_args,
                error_message=f"Input validation error for tool '{name}': {str(e)}",
            )

        # Check Human-In-The-Loop Tier 2 policy
        if definition.approval_required and not force_bypass_approval:
            return ToolExecutionResult(
                tool_name=name,
                status="BLOCKED_REQUIRES_APPROVAL",
                input_data=validated_input.model_dump(),
                output_data={"message": f"Tool '{name}' requires human approval before execution."},
            )

        handler = self._handlers[name]
        start_time = time.time()
        
        # Execute handler with retry support
        last_error = None
        for attempt in range(definition.retry_policy.max_retries + 1):
            try:
                # Inspect handler parameters to pass db_session if supported
                import inspect
                sig = inspect.signature(handler)
                kwargs = validated_input.model_dump()
                if "db_session" in sig.parameters:
                    kwargs["db_session"] = db_session

                if inspect.iscoroutinefunction(handler):
                    raw_result = await handler(**kwargs)
                else:
                    raw_result = handler(**kwargs)

                # Validate output schema
                if isinstance(raw_result, definition.output_schema):
                    output_dump = raw_result.model_dump()
                elif isinstance(raw_result, dict):
                    output_dump = definition.output_schema.model_validate(raw_result).model_dump()
                else:
                    output_dump = {"raw": str(raw_result)}

                duration_ms = int((time.time() - start_time) * 1000)
                exec_result = ToolExecutionResult(
                    tool_name=name,
                    status="SUCCESS",
                    input_data=validated_input.model_dump(),
                    output_data=output_dump,
                    duration_ms=duration_ms,
                )
                self._execution_history.append(exec_result)
                return exec_result
            except Exception as ex:
                last_error = str(ex)
                if attempt < definition.retry_policy.max_retries:
                    time.sleep(definition.retry_policy.delay_seconds * (definition.retry_policy.backoff_multiplier ** attempt))

        duration_ms = int((time.time() - start_time) * 1000)
        failed_result = ToolExecutionResult(
            tool_name=name,
            status="FAILED",
            input_data=validated_input.model_dump(),
            error_message=f"Execution failed after {definition.retry_policy.max_retries + 1} attempts: {last_error}",
            duration_ms=duration_ms,
        )
        self._execution_history.append(failed_result)
        return failed_result


# Global Singleton Registry
tool_registry = ToolRegistry()
