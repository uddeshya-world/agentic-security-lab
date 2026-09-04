import functools

from observability.otel_setup import get_tracer


def trace_agent_step(name: str):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            tracer = get_tracer()
            with tracer.start_as_current_span(f"agent.{name}"):
                return fn(*args, **kwargs)

        return wrapper

    return decorator


def trace_tool_call(tool_name: str):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            tracer = get_tracer()
            with tracer.start_as_current_span(f"tool_call.{tool_name}") as span:
                result = fn(*args, **kwargs)
                span.set_attribute("tool.name", tool_name)
                return result

        return wrapper

    return decorator
