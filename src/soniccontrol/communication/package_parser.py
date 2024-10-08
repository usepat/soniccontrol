from dataclasses import dataclass
import re


@dataclass
class Package:
    destination: str
    source: str
    identifier: int
    content: str

    @property
    def length(self) -> int:
        return len(self.content)


class PackageParser:
    max_bytes = 2048
    start_symbol = "<"
    end_symbol = ">"

    @staticmethod
    def parse_package(data: str) -> Package:
        regex = re.compile(r"<([^#]+)#([^#]+)#(\d+)#\d+#(.*)>", re.DOTALL)
        regex_match = re.search(regex, data)
        if regex_match is None:
            raise SyntaxError(f"Could not parse package: {data}")
        
        return Package(
            destination=regex_match.group(1),
            source=regex_match.group(2),
            identifier=int(regex_match.group(3)),
            content=regex_match.group(4),
        )

    @staticmethod
    def write_package(package: Package) -> str:
        return f"<{package.destination}#{package.source}#{package.identifier}#{package.length}#{package.content}>"
