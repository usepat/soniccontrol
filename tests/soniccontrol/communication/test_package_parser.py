from soniccontrol.communication.package_parser import Package, PackageParser
import pytest


def test_package_parsing_preserves_data():
    message = "My parents are not home. Do you want to come over?"
    package = Package("boyfriend", "me", 420, message)
    package_str = PackageParser.write_package(package)
    parsed_package = PackageParser.parse_package(package_str)

    assert (parsed_package == package)

def test_package_parse_fails_if_no_closing_angle_bracket():
    package_str = "<src#dest#0#5#hello"
    with pytest.raises(SyntaxError):
        PackageParser.parse_package(package_str)


