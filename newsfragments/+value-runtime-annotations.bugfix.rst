Default runtime type resolution of :class:`outcome.Value` now preserves its
original type variable after public module metadata is applied. This fixes
``typing.get_type_hints`` and ``attr.resolve_types`` when that attrs API is
available.
