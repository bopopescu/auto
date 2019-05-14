class BlockedTest(Exception):
    """Raise this to mark a test as Blocked"""
    pass


class SkipTest(Exception):
    """Raise this to mark a test as Skipped."""
    pass


class DeprecatedTest(Exception):
    """Raise this to mark a test as Deprecated."""
    pass
