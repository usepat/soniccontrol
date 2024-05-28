import abc

class MvcCommand:
    def __call__(self):
        if self.can_execute():
            self.execute()

    @abc.abstractmethod
    def can_execute(self) -> bool:
        return True

    @abc.abstractmethod
    def execute(self) -> None:
        ...
    