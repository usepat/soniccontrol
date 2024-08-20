from sonicpackage.communication.sonicprotocol import SonicProtocol


def test_sonicprotocol_parse_request_simple():
    content = "!freq=1000"
    request_id = 1
    request_str = SonicProtocol().parse_request(content, request_id)
    assert request_str == f"<0#0#{request_id}#{len(content)}#{content}>\n"

def test_sonicprotocol_parse_response_simple():
    content = "1050#1000 Hz"
    request_id = 15
    response_str = f"<0#0#{request_id}#{len(content)}#{content}>"
    package_id, answer = SonicProtocol().parse_response(response_str)
    assert package_id == request_id
    assert answer == content

def test_sonicprotocol_parse_response_empty_lines_get_ignored():
    content = """1050#1000 Hz
    
ahh!


wth?
    
"""
    request_id = 10
    response_str = f"<0#0#{request_id}#{len(content)}#{content}>"
    package_id, answer = SonicProtocol().parse_response(response_str)
    assert package_id == request_id
    print (answer)
    assert answer == """1050#1000 Hz
ahh!
wth?
"""
