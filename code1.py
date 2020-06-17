def handle_error(program, string, msg, sync=[], follow=[], max_errors=0):
    global parser_errors
    parser_errors.append(tuple((lexical.line_count, lexical.i-lexical.chcnt-1, msg, string)))
    
    if(max_errors < 0):
        sync = follow

    # update_token(program)
    while(token not in sync+follow and lexical.i < len(program)):
        update_token(program)
    
    if(lexical.i < len(program)):
        if(max_errors < 0) or token in follow:
            return True
        else:
            return False
    else:
        print_errors()
        exit(1)