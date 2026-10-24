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
                raise ValueError("dependencies must be non-empty strings")
            if dep not in jobs:
                raise ValueError("unknown dependency: %r" % (dep,))

    indegree = {name: len(set(deps)) for name, deps in jobs.items()}
    dependents = {name: [] for name in jobs}
    for name, deps in jobs.items():
        for dep in set(deps):
            dependents[dep].append(name)

    ready = [name for name, degree in indegree.items() if degree == 0]
    heapq.heapify(ready)
    order = []
    while ready:
        name = heapq.heappop(ready)
        order.append(name)
        for child in dependents[name]:
            indegree[child] -= 1
            if indegree[child] == 0:
                heapq.heappush(ready, child)

    if len(order) != len(jobs):
        raise ValueError("cyclic dependency")
    return order
