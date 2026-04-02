"""
* Render Spec Module
* Handles parsing render spec file, aka text files that contain a set of configurations and cards to render
"""

# Standard Library Imports
import os
import re
import glob
import re as regex
from pathlib import Path
from typing import Dict, TypedDict
from dataclasses import dataclass, astuple

# Local Imports
from src.cards import CardDetails, parse_card_info

"""
* Types
"""


@dataclass
class RenderConfiguration:
    name: str
    spec: str


@dataclass
class CardSpec:
    spec: str
    actual_path: str | None


class RenderSpec(TypedDict):
    """Render spec obtained from parsing the file."""

    name: str
    file: Path
    configs: Dict[str, RenderConfiguration]
    cards: list[CardDetails]


"""
* File parsing
"""


def parse_render_spec(file_path: Path) -> RenderSpec:
    """Retrieve render spec from the input file.

    Args:
        file_path: Path to the text file.

    Returns:
        Dict containing the configurations and cards in this spec.
    """

    # Extract just the spec name
    file_name = file_path.stem
    parent_dir = str(file_path.parent)

    # Load all the content and get rid of empty lines and comments
    spec_lines = open(file_path, "r").read().splitlines()
    spec_lines = [l.split("#")[0].strip() for l in spec_lines]
    spec_lines = [l for l in spec_lines if l]

    # Split lines with configs and lines with cards
    config_lines = [l for l in spec_lines if regex.match(r"([a-zA-Z0-9_ ]+):(.*)", l)]
    card_lines = [l for l in spec_lines if l not in config_lines]

    # Find all the configurations first
    configs = {}
    for l in config_lines:
        [config_name, config_spec] = map(str.strip, l.split(":"))
        configs[config_name] = RenderConfiguration(
            name=config_name,
            spec=config_spec,
        )

    # Now find all the cards and parse them by using the configs
    cards = []
    groups = []
    for l in card_lines:
        # Entering a group
        if l.startswith("{"):
            groups.append([])
            l = l[1:].strip()
            if not l:
                continue

        parts = list(map(str.strip, l.split("|")))
        spec_base = parts[0]

        def append_config(
            card: CardSpec, config: RenderConfiguration | str
        ) -> CardSpec:
            if isinstance(config, RenderConfiguration):
                config = config.spec
            return CardSpec(card.spec + f" {config}", card.actual_path)

        def append_card(card_spec: CardSpec):
            spec, path = astuple(card_spec)
            # Make sure the extension doesn't contain a ']' as that implies
            # we have something without extension using a config that contains
            # something with extension, e.g. [art=file.png]
            if not re.match(r"\.[^\]]+$", spec):
                spec += ".png"
            # Pretend this is a file right next to the spec and parse that
            full_card_path = file_path.parent / Path(spec).name
            card_info = parse_card_info(full_card_path)
            if path is not None and "art" not in card_info["additional_cfg"]:
                card_info["additional_cfg"]["art"] = path
            cards.append(card_info)

        if "*" in spec_base:
            specs = glob.glob(spec_base, root_dir=parent_dir, recursive=True)
            specs = [
                CardSpec(s.split(".")[0], s) for s in specs if not s.endswith(".txt")
            ]
        elif os.path.exists(spec_base):
            specs = [CardSpec(spec_base.split(".")[0], spec_base)]
        else:
            specs = [CardSpec(spec_base, None)]

        used_configs = parts[1:]
        for c in used_configs:
            if c in configs:
                specs = [append_config(s, configs[c]) for s in specs]
            else:
                specs = [append_config(s, c) for s in specs]

        # If part of a group we need to just accumulate
        if groups:
            if l.startswith("}"):
                # The group ended, so we assign this configuration to all the cards in it
                group_spec = specs[0].spec[1:].strip()
                ended_group = groups.pop()
                ended_group = [append_config(c, group_spec) for c in ended_group]

                def expand_variable(card, variable, value):
                    return (card[0].replace(variable, str(value)), card[1])

                if groups:
                    # Replace special variables
                    ended_group = [
                        expand_variable(c, "${GROUP_INDEX}", i)
                        for (i, c) in enumerate(ended_group)
                    ]
                    ended_group = [
                        expand_variable(c, "${INNER_GROUP_INDEX}", i)
                        for (i, c) in enumerate(ended_group)
                    ]

                    # If this was a nested group we just put these into the outer group
                    groups[-1].extend(ended_group)
                else:
                    # Replace special variables
                    ended_group = [
                        expand_variable(c, "${GROUP_INDEX}", i)
                        for (i, c) in enumerate(ended_group)
                    ]
                    ended_group = [
                        expand_variable(c, "${OUTER_GROUP_INDEX}", i)
                        for (i, c) in enumerate(ended_group)
                    ]

                    # Otherwise append to the render spec
                    for card in ended_group:
                        append_card(card)
            else:
                # Append the card to the group
                groups[-1].extend(specs)
        else:
            for card_spec in specs:
                append_card(card_spec)

    # Return dictionary
    return {
        "name": file_name,
        "file": file_path,
        "configs": configs,
        "cards": cards,
    }
