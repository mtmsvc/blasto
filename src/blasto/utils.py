def capitalize_name(name: str) -> str:
    if not name:
        return ""
    return name[0].upper() + name[1:]
