lowercase_letters = "abcdefghijklmnopqrstuvwxyz"
safe_characters = lowercase_letters + "0123456789-+!$%&`'@~#.,^"
uppercase_letters = lowercase_letters.upper()
def encode(input, errors='strict'):
    """Convert Unicode strings to safe filenames."""
    output = ""
    i = 0
    input_length = len(input)
    while i < input_length:
        c = input[i]
        if c in safe_characters:
            output += str(c)
        elif c == " ":
            output += "_"
        elif c in uppercase_letters:
            output += "("
            while i < input_length and input[i] in uppercase_letters:
                output += str(input[i]).lower()
                i += 1
            output += ")"
            continue
        else:
            output += "{" + hex(ord(c))[2:] + "}"
        i += 1
    return output
def handle_problematic_characters(errors, input, start, end, message):
    if errors == 'ignore':
        return u""
    elif errors == 'replace':
        return u"?"
    else:
        raise UnicodeDecodeError("safefilename", input, start, end, message)
def decode(input, errors='strict'):
    """Convert safe filenames to Unicode strings."""
    input = str(input)
    input_length = len(input)
    output = u""
    i = 0
    while i < input_length:
        c = input[i]
        if c in safe_characters:
            output += c
        elif c == "_":
            output += " "
        elif c == "(":
            i += 1
            while i < input_length and input[i] in lowercase_letters:
                output += input[i].upper()
                i += 1
            if i == input_length:
                handle_problematic_characters(errors, input, i-1, i, "open parenthesis was never closed")
                continue
            if input[i] != ')':
                handle_problematic_characters(
                        errors, input, i, i+1, "invalid character '%s' in parentheses sequence" % input[i])
                continue
        elif c == "{":
            end_position = input.find("}", i)
            if end_position == -1:
                end_position = i+1
                while end_position < input_length and input[end_position] in "0123456789abcdef" and \
                        end_position - i <= 8:
                    end_position += 1
                output += handle_problematic_characters(errors, input, i, end_position,
                                                             "open backet was never closed")
                i = end_position
                continue
            else:
                try:
                    output += unichr(int(input[i+1:end_position], 16))
                except:
                    output += handle_problematic_characters(errors, input, i, end_position+1,
                                                            "invalid data between brackets")
            i = end_position
        else:
            output += handle_problematic_characters(errors, input, i, i+1, "invalid character '%s'" % c)
        i += 1
    return output

