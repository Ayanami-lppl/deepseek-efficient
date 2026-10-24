import heapq


def _validated_dependencies(jobs):
    """Validate the input and return {name: set(dependencies)} without mutation."""
    if not isinstance(jobs, dict):
        raise ValueError("jobs must be a dict of task name -> dependency list")

    dependencies = {}
    for name, deps in jobs.items():
        if not isinstance(name, str) or not name:
            raise ValueError("task names must be non-empty strings")
        if not isinstance(deps, list):
            raise ValueError("dependencies of %r must be a list" % (name,))
        unique = set()
        for dep in deps:
            if not isinstance(dep, str) or not dep:
                raise ValueError("dependencies of %r must be non-empty strings" % (name,))
            unique.add(dep)
        dependencies[name] = unique

    for name, deps in dependencies.items():
        for dep in deps:
            if dep not in dependencies:
                raise ValueError("unknown dependency %r required by %r" % (dep, name))

    return dependencies


def order_jobs(jobs):
    dependencies = _validated_dependencies(jobs)

    children = {name: set() for name in dependencies}
    missing = {}
    for name, deps in dependencies.items():
        missing[name] = len(deps)
        for dep in deps:
            children[dep].add(name)

    ready = [name for name, count in missing.items() if count == 0]
    heapq.heapify(ready)

    order = []
    while ready:
        name = heapq.heappop(ready)
        order.append(name)
        for child in children[name]:
            missing[child] -= 1
            if missing[child] == 0:
                heapq.heappush(ready, child)

    if len(order) != len(dependencies):
        raise ValueError("dependency graph contains a cycle")

    return order
