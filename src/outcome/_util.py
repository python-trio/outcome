from typing import Any, Mapping


class AlreadyUsedError(RuntimeError):
    """An Outcome can only be unwrapped once."""
    pass


def fixup_module_metadata(module_name: str,
                          namespace: Mapping[str, Any]) -> None:
    def fix_one(obj: Any) -> None:
        mod = getattr(obj, "__module__", None)
        if mod is not None and mod.startswith("outcome."):
            obj.__module__ = module_name
            if isinstance(obj, type):
                for attr_value in obj.__dict__.values():
                    fix_one(attr_value)

    for objname in namespace["__all__"]:
        obj = namespace[objname]
        fix_one(obj)


# TODO: Use TypeVar(bound=BaseException) once this fix is released:
# https://github.com/python/typeshed/pull/4298
def remove_tb_frames(exc: BaseException, n: int) -> BaseException:
    tb = exc.__traceback__
    for _ in range(n):
        if tb is not None:
            tb = tb.tb_next
    return exc.with_traceback(tb)
