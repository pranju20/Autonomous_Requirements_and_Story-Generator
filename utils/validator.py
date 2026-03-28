def validate_requirements(reqs):
    valid = []
    for r in reqs:
        if isinstance(r, dict) and "title" in r and "description" in r:
            valid.append(r)
    return valid
