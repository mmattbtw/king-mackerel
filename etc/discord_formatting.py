def as_bold(text):
    return f'**{text}**'

def as_italics(text):
    return f'*{text}*'

def as_underline(text):
    return f'__{text}__'

def as_bold_underline(text):
    return as_underline(as_bold(text))

def as_bold_italics(text):
    return as_bold(as_italics(text))

def as_bold_underline_italics(text):
    return as_underline(as_bold_italics(text))