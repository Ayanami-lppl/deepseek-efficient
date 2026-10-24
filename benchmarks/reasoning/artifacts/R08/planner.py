import heapq


def _valid_name(value):
    return isinstance(value, str) and value != ""


def order_jobs(jobs):
    if not isinstance(jobs, dict):
        raise ValueError("jobs must be a dict")

    for name, deps in jobs.items():
        if not _valid_name(name):
            raise ValueError("task names must be non-empty strings")
        if not isinstance(deps, list):
            raise ValueError("dependencies must be a list")
        for dep in deps:
            if not _valid_name(dep):
                raise ValueError("dependencies must be non-empty strings")
            if dep not in jobs:
                raise ValueError("unknown dependency: %r" % (dep,))

    dependents = {name: [] for name in jobs}
    indegree = {}
    for name, deps in jobs.items():
        unique_deps = set(deps)
        indegree[name] = len(unique_deps)
        for dep in unique_deps:
            dependents[dep].append(name)

    ready = [name for name, degree in indegree.items() if degree == 0]
    heapq.heapify(ready)

    result = []
    while ready:
        name = heapq.heappop(ready)
        result.append(name)
        for dependent in dependents[name]:
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                heapq.heappush(ready, dependent)

    if len(result) != len(jobs):
        raise ValueError("cyclic dependencies")

    return result
