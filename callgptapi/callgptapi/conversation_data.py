from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from decimal import Decimal
from datetime import datetime
from typing import Any
from datetime import datetime
from zoneinfo import ZoneInfo


@dataclass_json
@dataclass
class PromptItem:
    """Prompt for ChatGPT"""

    def __init__(self, content: str = "", role: str = "", seq: int = 0):
        self.content = content
        self.role = role
        self.seq = seq

    content: str
    """contents"""

    seq: int
    """content sequence"""

    role: str
    """speaker"""


@dataclass_json
@dataclass
class ConversationItem:
    """Item of conversation"""

    def __init__(
        self,
        content: str = "",
        role: str = "",
        completion_token: int = 0,
        prompt_token: int = 0,
        prompt: list[PromptItem] = [],
        content_at: datetime = datetime.now(ZoneInfo("Asia/Tokyo")),
    ):
        self.content = content
        self.role = role
        self.seq = -1  # It will be set by parent class
        self.completion_token = completion_token
        self.prompt_token = prompt_token
        self.prompt = prompt
        self.content_at = content_at

    content: str
    """contents"""

    seq: int
    """content sequence"""

    role: str
    """speaker"""

    completion_token: int
    """response token from ChatGPT"""

    prompt_token: int
    """prompt token from ChatGPT"""

    content_at: datetime
    """datetime of speaking"""

    prompt: list[PromptItem] = field(default_factory=list)
    """prompt sending to ChatGPT"""


@dataclass_json
@dataclass
class Conversation:
    """Conversation Management Class"""

    conversation_id: str
    """Conversation ID for Teams"""

    conversation_items: list[ConversationItem] = field(default_factory=list)
    """History of conversation"""

    def __init__(self, id: str):
        self.conversation_id = id
        self.conversation_items = []

    def has_conversation(self):
        if self.conversation_items == None:
            return False
        else:
            return False if self.conversation_items.count() <= 0 else True

    def add_converstion_item(self, item: ConversationItem):
        if ConversationItem == None:
            self.conversation_items = []

        item.seq = self.get_next_conversation_seq()
        self.conversation_items.append(item)

    def get_next_conversation_seq(self):
        return len(self.conversation_items) + 1


def decimal_to_int(obj):
    if isinstance(obj, Decimal):
        return int(obj)


def conversation_dict_factory(items: list[tuple[str, Any]]) -> dict[str, Any]:
    # convert conversation object to dict
    adict = {}
    for key, value in items:
        if isinstance(value, datetime):
            value = value.strftime("%Y/%m/%d %H:%M:%S")
        adict[key] = value

    return adict
