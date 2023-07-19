import logging
import json
import traceback
import os
import json
import azure_bot
import boto3
from conversation_data import Conversation, ConversationItem, conversation_dict_factory
import call_gpt
from dataclasses import asdict
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


def lambda_handler(event, context):
    try:
        # Get previous conversation from DynamoDB
        event_body = json.loads(event["body"])
        conversation = load_previous_conversation(event_body["conversation"]["id"])

        # Set the current(recieved) conversation to conversation data.
        conversation.add_converstion_item(
            ConversationItem(content=event_body["text"], role="user")
        )

        # Call GPT
        gpt_response_conversation_item = call_gpt.send_data_to_gpt(conversation)

        # Send the ChatGPT response to Teams via Azure Bot service.
        azure_bot.send_message_to_teams(
            event_body, gpt_response_conversation_item.content
        )

        # Set the ChatGPT response to conversation data.
        conversation.add_converstion_item(gpt_response_conversation_item)

        # Save conversation data to DynamoDB
        save_conversation(conversation)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "success",
                }
            ),
        }

    except Exception as e:
        traceback.print_exc()
        azure_bot.send_message_to_teams(
            event_body, "Sorry, your message couldn't be processed. Please try again."
        )
        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "message": "Error " + traceback.format_exc(),
                }
            ),
        }


def load_previous_conversation(conversation_id: str) -> Conversation:
    """The fuction of Load conversation from AWS DynamoDB"""

    # connect for test Enviroment
    # for refference https://ramble.impl.co.jp/3718/
    # db_resource = boto3.resource("dynamodb",endpoint_url="http://dynamodb:8000")
    db_resource = boto3.resource("dynamodb")

    table = db_resource.Table("ConversationTable")
    response = table.get_item(Key={"conversation_id": conversation_id})

    if "Item" in response:
        return convert_to_conversation(response["Item"])
    else:
        return Conversation(id=conversation_id)


def save_conversation(conversation: Conversation):
    """The fuction of Save conversation to AWS DynamoDB"""

    # db_resource = boto3.resource("dynamodb" ,endpoint_url="http://dynamodb:8000")
    db_resource = boto3.resource("dynamodb")

    table = db_resource.Table("ConversationTable")
    # Convert from object to dict
    registration_item = asdict(conversation, dict_factory=conversation_dict_factory)

    res = table.put_item(Item=registration_item)


def delete_conversation(conversation: Conversation):
    """The fuction of Delete conversation from AWS DynamoDB"""
    # db_resource = boto3.resource("dynamodb" ,endpoint_url="http://dynamodb:8000")
    db_resource = boto3.resource("dynamodb")

    table = db_resource.Table("ConversationTable")
    res = table.delete_item(Key={"conversation_id": conversation.conversation_id})


def convert_to_conversation(target: dict) -> Conversation:
    """The function of to convert from Json to Conversation_data"""
    converted_item = Conversation(target["conversation_id"])

    for item in target["conversation_items"]:
        converted_item.add_converstion_item(
            ConversationItem(
                content=item["content"],
                role=item["role"],
                completion_token=item["completion_token"],
                prompt_token=item["prompt_token"],
                prompt=item["prompt"],
                content_at=datetime.strptime(item["content_at"], "%Y/%m/%d %H:%M:%S"),
            )
        )

    return converted_item
