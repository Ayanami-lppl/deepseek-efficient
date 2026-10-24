import heapq


def order_jobs(jobs):
    if not isinstance(jobs, dict):
        raise ValueError("jobs must be a dict")
    for name, deps in jobs.items():
        if not isinstance(name, str) or not name:
            raise ValueError("job names must be non-empty strings")
        if not isinstance(deps, list):
            raise ValueError("dependencies must be a list")
        for dep in deps:
            if not isinstance(dep, str) or not dep:
                raise ValueError("dependency names must be non-empty strings")
            if dep not in jobs:
                raise ValueError("unknown dependency: %r" % (dep,))

    # Count unique prerequisites per job so duplicate edges count once.
    remaining = {name: len(set(deps)) for name, deps in jobs.items()}
    dependents = {name: [] for name in jobs}
    for name, deps in jobs.items():
        for dep in set(deps):
            dependents[dep].append(name)

    ready = [name for name, count in remaining.items() if count == 0]
    heapq.heapify(ready)
    order = []
    while ready:
        name = heapq.heappop(ready)
        order.append(name)
        for dependent in dependents[name]:
            remaining[dependent] -= 1
            if remaining[dependent] == 0:
                heapq.heappush(ready, dependent)

    if len(order) != len(jobs):
        raise ValueError("cycle detected")
    return order
