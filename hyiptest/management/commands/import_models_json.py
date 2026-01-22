import json
import pathlib

import jsonschema
from django.core.management.base import BaseCommand

from hyiptest.models import Answer, BadDomain, BadSite, Question

SCHEMA = {
    "$id": "https://example.com/hyiptest_import.schema.json",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Hyiptest Import",
    "description": ("Used to import the initial data from a JSON file to the database"),
    "type": "object",
    "properties": {
        "badsites": {
            "description": "BadSite models with BadDomain's",
            "type": "array",
            "items": {"$ref": "#/$defs/badsite"},
            "minItems": 1,
        },
        "questions": {
            "description": "Question models containing Answer's",
            "type": "array",
            "items": {"$ref": "#/$defs/question"},
            "minItems": 1,
        },
    },
    "anyOf": [{"required": ["badsites"]}, {"required": ["questions"]}],
    "$defs": {
        "badsite": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "minLength": 1},
                "bad_type": {"type": "string", "minLength": 1},
                "domains": {
                    "type": "array",
                    "items": {"type": "string", "minLength": 1},
                    "minItems": 1,
                },
            },
            "required": ["name", "bad_type"],
        },
        "question": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "minLength": 1},
                "description": {"type": "string", "minLength": 1},
                "answers": {
                    "type": "array",
                    "items": {"$ref": "#/$defs/answer"},
                    "minItems": 1,
                },
            },
            "required": ["text"],
        },
        "answer": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "minLength": 1},
                "description": {"type": "string", "minLength": 1},
                "risk_score": {"type": "integer", "minimum": 0},
            },
            "required": ["text", "risk_score"],
        },
    },
}


class Command(BaseCommand):
    help = "Import models from a JSON file with custom schema to the database"

    def add_arguments(self, parser):
        parser.add_argument("json_file", type=pathlib.Path, help="json file")

    def handle(self, *args, **options):
        data = json.loads(options["json_file"].read_text())
        jsonschema.validate(data, SCHEMA)

        for badsite in data.get("badsites", []):
            self.process_badsite(badsite)

        for question in data.get("questions", []):
            self.process_question(question)

    def process_badsite(self, badsite):
        self.stdout.write(f'+ BadSite "{badsite["name"]}" "{badsite["bad_type"]}"')
        created = BadSite.objects.create(
            name=badsite["name"], bad_type=badsite["bad_type"]
        )

        for domain in badsite["domains"]:
            self.stdout.write(f'\t+ BadDomain "{domain}" -> {created}')
            BadDomain.objects.create(name=domain, site=created)

    def process_question(self, question):
        self.stdout.write(f'+ Question "{question["text"]}"')
        created = Question.objects.create(
            text=question["text"], description=question.get("description", "")
        )

        for answer in question["answers"]:
            self.stdout.write(
                f'\t+ Answer "{answer["text"]}" {answer["risk_score"]} -> {created}'
            )
            Answer.objects.create(
                text=answer["text"],
                description=answer.get("description", ""),
                risk_score=answer["risk_score"],
                question=created,
            )
