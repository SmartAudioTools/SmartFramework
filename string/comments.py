def removeComment(line):
    if isinstance(line, str):
        backslash = "\\"
        doublequote = '"'
        comment = "#"
    elif isinstance(line, bytes):
        backslash = ord("\\")
        doublequote = ord('"')
        comment = ord("#")

    # a little state machine with two state varaibles:
    inQuote = False  # whether we are in a quoted string right now
    backslashEscape = False  # true if we just saw a backslash
    for i, ch in enumerate(line):
        if not inQuote and ch == comment:
            # not in a quote, saw a '#', it's a comment.  Chop it and return!
            return line[:i]
        elif backslashEscape:
            # we must have just seen a backslash; reset that flag and continue
            backslashEscape = False
        elif inQuote and ch == backslash:
            # we are in a quote and we see a backslash; escape next char
            backslashEscape = True
        elif ch == doublequote:
            inQuote = not inQuote
    return line


def removeComments(value):  # accepte des bytes ou des str
    if isinstance(value, list):
        lines = value
    elif isinstance(value, (str, bytes)):
        if isinstance(value, str):
            sharp = "#"
        else:
            sharp = b"#"
        if value.find(sharp) != -1:  # Remove comments
            lines = value.splitlines()
        else:
            return value
    else:
        print(type(value))
        raise Exception("type de valeure passe a removeComments inconnu")
    linesWithoutComments = []
    for line in lines:
        sharpIndex = line.find(sharp)
        if sharpIndex != -1:
            linesWithoutComments.append(removeComment(line))
        else:
            linesWithoutComments.append(line)
    if isinstance(linesWithoutComments[0], str):
        string = "\n".join(linesWithoutComments)
    else:
        string = b"\n".join(linesWithoutComments)
    return string
