import logging
import requests
import traceback
import json
import os
from datetime import datetime
from conversation_data import Conversation, ConversationItem, PromptItem
import parameters

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


def send_data_to_gpt(conversation: Conversation) -> ConversationItem:
    """Send a conversation item to ChatGPT."""

    apikey = os.environ.get(
        "CHATGPT_API_KEY",
        parameters.get_encrypted_parameter("/callgptapi/CHATGPT_API_KEY"),
    )
    openai_endpoint = "https://api.openai.com/v1/chat/completions"

    system_content = ""

    payload = {
        "model": parameters.get_parameter("/callgptapi/CHATGPT_MODEL"),
        "messages": [
            {"role": "system", "content": system_content},
        ],
    }

    return_conversation_item = ConversationItem()
    # Set system(default) prompt.
    prompt_counter = 1
    return_conversation_item.prompt.append(
        PromptItem(content=system_content, seq=prompt_counter, role="system")
    )
    prompt_counter += 1

    # Create & set prompt from convesation histories.
    number_of_max_prompt = (
        int(
            parameters.get_parameter("/callgptapi/CHATGPT_NUMBER_OF_MAX_PROMPT_HISTORY")
        )
        * -1
    )
    for item in conversation.conversation_items[number_of_max_prompt:]:
        payload["messages"].append({"role": item.role, "content": item.content})
        return_conversation_item.prompt.append(
            PromptItem(content=item.content, seq=prompt_counter, role=item.role)
        )
        prompt_counter += 1

    headers = {"Content-type": "application/json", "Authorization": "Bearer " + apikey}

    try:
        response = requests.post(
            openai_endpoint, data=json.dumps(payload), headers=headers
        )
        response_data = response.json()

        # Set the response from ChatGPT
        return_conversation_item.content = response_data["choices"][0]["message"][
            "content"
        ]
        return_conversation_item.role = response_data["choices"][0]["message"]["role"]
        return_conversation_item.completion_token = response_data["usage"][
            "completion_tokens"
        ]
        return_conversation_item.prompt_token = response_data["usage"]["prompt_tokens"]

        return return_conversation_item

    except:
        logger.error(traceback.format_exc())
        return traceback.format_exc()
