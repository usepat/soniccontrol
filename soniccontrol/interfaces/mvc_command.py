import abc

class MvcCommand:
    def __init__(self, target: any = None, source: any = None):
        self.target = target
        self.source = source

    def __call__(self):
        if self.can_execute():
            self.execute()

    @abc.abstractmethod
    def can_execute(self) -> bool:
        return True

    @abc.abstractmethod
    def execute(self) -> None:
        ...
    