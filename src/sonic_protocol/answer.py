

import logging
import re
import sys
import time
from typing import Any, Callable, Dict, List, Literal, Optional, Union

import attrs



@attrs.define()    
class Answer:
    # on_setattr=None, prevents the generation of a setter for an attribute.
    message: str = attrs.field(on_setattr=None) 
    # TODO: probably better to make an enum ValidationStatus and merge valid and was_validated
    valid: bool = attrs.field(on_setattr=None)
    was_validated: bool = attrs.field(on_setattr=None)
    value_dict: Dict[str, Any] = attrs.field(default={}, on_setattr=None)
    # received_timestamp: float = attrs.field(factory=time.time, init=False, on_setattr=None)


@attrs.define
class Converter:
    worker: Callable[[Any], Any] = attrs.field()
    logger: logging.Logger = attrs.field(default=logging.getLogger())
    _converted: bool = attrs.field(default=False, init=False, repr=False)
    _result: Any = attrs.field(init=False)

    @property
    def result(self) -> Any:
        if self._converted:
            return self._result
        else:
            self.logger.error("ERROR: Converter did not convert yet.")
            return False

    def convert(self, *args, **kwargs) -> Any:
        try:
            self._result = self.worker(*args, **kwargs)
        except Exception:
            self.logger.error("ERROR", sys.exc_info())
            return False
        else:
            self._converted = True
            return self._result


@attrs.define
class AfterConverter:
    converter: Converter = attrs.field()
    keywords: List[str] = attrs.field(default=[])

# TODO: fix linter errors. Improve type hints
@attrs.define
class AnswerValidator:
    pattern: str = attrs.field(on_setattr=None)
    _named_pattern: str = attrs.field(init=False)
    _converters: Dict[str, Converter] = attrs.field(init=False, repr=False)
    _after_converters: Dict[str, AfterConverter] = attrs.field(init=False, repr=False)
    _compiled_pattern: re.Pattern[str] = attrs.field(init=False, repr=False)

    def __init__(
        self,
        pattern: str,
        **kwargs: type[Any] | Callable[[Any], Any] | AfterConverter,
    ) -> None:
        """
        Initializes the CommandValidator instance with the specified pattern and converters.

        Parameters:
            pattern (str): The pattern to be used.
            **kwargs:   Additional keyword arguments that are passed to the Converter constructor.
                        The keyword argument should be a string that is the name of the
                        value. The value should be a Callable that takes in the value and returns
                        the value in the correct type. The converted values are available in the
                        result attribute.

                        Additionally, the keyword argument can be a dictionary with the following
                        keys: "worker" and "keywords". The "worker" key should be a Callable that
                        takes in the value and returns the value in the correct type. The "keywords"
                        are the names of the values used to determine the type of the value. These
                        are "after converters". They are using the previously converted values.

        Example:
            CommandValidator(
                pattern="(?P<foo>[a-z]+) (?P<bar>[0-9]+)",
                foo=int,
                bar=float,
                foobar={
                    "worker": lambda foo, bar: foo * bar,
                    "keywords": ["foo", "bar"],
                }

        Returns:
            None
        """
        workers: dict[str, Converter] = dict()
        after_workers: dict[str, AfterConverter] = dict()

        for keyword, worker in kwargs.items():
            if isinstance(worker, AfterConverter):
                after_workers[keyword] = worker
                continue

            workers[keyword] = worker if isinstance(worker, Converter) else Converter(worker)
        
        self.pattern = pattern
        self._converters = workers
        self._after_converters = after_workers
        self._named_pattern = self.generate_named_pattern(
            pattern=self.pattern, keywords=list(self._converters.keys())
        )
        self._compiled_pattern = re.compile(
            pattern=self._named_pattern,
            flags=re.IGNORECASE,
        )


    @staticmethod
    def generate_named_pattern(pattern: str, keywords: List[str]) -> str:
        """
        Generates a named pattern by replacing the unnamed capture groups in the given pattern with named capture groups.

        Args:
            pattern (str): The pattern to generate the named pattern from.
            keywords (List[str]): The list of keywords to use for naming the capture groups.

        Returns:
            str: The generated named pattern.

        Example:
            >>> generate_named_pattern("(?:foo) (bar) (?:baz)", ["keyword1", "keyword2"])
            '(?P<keyword1>:foo) (?P<keyword2>(bar)) (?:baz)'

        Note:
            - The named capture groups are generated using the keywords provided.
            - The unnamed capture groups are replaced with named capture groups.
            - The named capture groups are enclosed in parentheses and prefixed with '?P<keyword>'.
            - The named capture groups are generated in the order of the keywords provided.
            - If no keywords are provided, the original pattern is returned.
        """
        if not keywords:
            return pattern
        segments = re.split(r"(\(.*?\))", pattern)

        assert len(segments) == len(keywords)
        processed = "".join(
            (
                f"(?P<{keyword}>{segment[1:-1]})"
                if not segment.startswith("(?:") and segment.startswith("(")
                else segment
            )
            for keyword, segment in zip(keywords, segments)
            if segment
        )
        return processed

    def validate(self, data: str) -> Answer:
        """
        Checks if the given data matches the compiled pattern and performs conversions on the matched groups.
        The converted values are stored in the result attribute.

        Args:
            data (str): The input data to check against the pattern.

        Returns:
            bool: True if the data matches the pattern and conversions are successful, False otherwise.
        """

        result: Optional[re.Match] = self._compiled_pattern.search(data)
        if result is None:
            return Answer(data, False, True)

        result_dict: Dict[str, Any] = {
            keyword: self._converters[keyword].convert(value)
            for keyword, value in result.groupdict().items()
        }
        result_dict.update(
            {
                keyword: self._after_converters[keyword].converter.convert(
                    **{
                        k: result_dict.get(k)
                        for k in worker.keywords
                        if k in result.groupdict()
                    }
                )
                for keyword, worker in self._after_converters.items()
            }
        )

        answer = Answer(data, True, True, result_dict)

        return answer
