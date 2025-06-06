"""
* LEVELER TEMPLATES
"""
# Standard Library
from functools import cached_property
from typing import Optional, Callable

# Third Party Imports
from photoshop.api._artlayer import ArtLayer
from photoshop.api._layerSet import LayerSet

# Local Imports
from src.enums.layers import LAYERS
import src.helpers as psd
from src.layouts import LevelerLayout
from src.templates._core import NormalTemplate
import src.text_layers as text_classes
from src.utils.adobe import ReferenceLayer

"""
* Modifier Classes
"""


class LevelerMod(NormalTemplate):
    """
    * Modifier for Level-Up cards introduced in Rise of the Eldrazi.

    Adds:
        * First, second, and third level ability text.
        * First, second, and third level power/toughness.
        * Level requirements for second and third stage.
    """

    """
    * Checks
    """

    @cached_property
    def is_leveler(self) -> bool:
        return isinstance(self.layout, LevelerLayout)

    """
    * Mixin Methods
    """

    @cached_property
    def text_layer_methods(self) -> list[Callable]:
        """Add Adventure text layers."""
        funcs = [self.text_layers_leveler] if self.is_leveler else []
        return [*super().text_layer_methods, *funcs]

    """
    * Groups
    """

    @cached_property
    def leveler_group(self) -> Optional[LayerSet]:
        """Group containing Leveler text layers."""
        return psd.getLayerSet("Leveler Text", self.text_group)

    """
    * Layers
    """

    @cached_property
    def pt_layer(self) -> Optional[ArtLayer]:
        if self.is_leveler:
            return psd.getLayer(self.twins, LAYERS.PT_AND_LEVEL_BOXES)
        return super().pt_layer

    """
    * Text Layers
    """

    @cached_property
    def text_layer_rules(self) -> Optional[ArtLayer]:
        if self.is_leveler:
            return psd.getLayer("Rules Text - Level Up", self.leveler_group)
        return super().text_layer_rules

    @cached_property
    def text_layer_pt(self) -> Optional[ArtLayer]:
        if self.is_leveler:
            return psd.getLayer("Top Power / Toughness", self.leveler_group)
        return super().text_layer_pt

    """
    * Leveler Text Layers
    """

    @cached_property
    def text_layer_rules_x_y(self) -> Optional[ArtLayer]:
        return psd.getLayer("Rules Text - Levels X-Y", self.leveler_group)

    @cached_property
    def text_layer_rules_z(self) -> Optional[ArtLayer]:
        return psd.getLayer("Rules Text - Levels Z+", self.leveler_group)

    @cached_property
    def text_layer_level_middle(self) -> Optional[ArtLayer]:
        return psd.getLayer("Middle Level", self.leveler_group)

    @cached_property
    def text_layer_level_bottom(self) -> Optional[ArtLayer]:
        return psd.getLayer("Bottom Level", self.leveler_group)

    @cached_property
    def text_layer_pt_middle(self) -> Optional[ArtLayer]:
        return psd.getLayer("Middle Power / Toughness", self.leveler_group)

    @cached_property
    def text_layer_pt_bottom(self) -> Optional[ArtLayer]:
        return psd.getLayer("Bottom Power / Toughness", self.leveler_group)

    """
    * References
    """

    @cached_property
    def textbox_reference(self) -> Optional[ReferenceLayer]:
        if self.is_leveler:
            return psd.get_reference_layer(f'{LAYERS.TEXTBOX_REFERENCE} - Level Text', self.leveler_group)
        return super().textbox_reference

    """
    * Leveler References
    """

    @cached_property
    def textbox_reference_x_y(self) -> Optional[ArtLayer]:
        return psd.get_reference_layer(f'{LAYERS.TEXTBOX_REFERENCE} - Level X-Y', self.leveler_group)

    @cached_property
    def textbox_reference_z(self) -> Optional[ArtLayer]:
        return psd.get_reference_layer(f'{LAYERS.TEXTBOX_REFERENCE} - Levels Z+', self.leveler_group)

    """
    * Leveler Text Methods
    """

    def rules_text_and_pt_layers(self) -> None:
        """Add rules and power/toughness text."""
        
        if self.is_leveler:
            # Level-Up text and starting P/T
            self.text.extend([
                text_classes.FormattedTextArea(
                    layer=self.text_layer_rules,
                    contents=self.layout.level_up_text,
                    reference=self.textbox_reference
                ),
                text_classes.TextField(
                    layer=self.text_layer_pt,
                    contents=str(self.layout.power) + "/" + str(self.layout.toughness)
                )
            ])
        else:
            return super().rules_text_and_pt_layers()

    def text_layers_leveler(self):
        """Add and modify text layers required by Leveler cards."""

        # Add Leveler sections
        self.text.extend([
            # Level 2
            text_classes.TextField(
                layer=self.text_layer_level_middle,
                contents=self.layout.middle_level
            ),
            text_classes.TextField(
                layer=self.text_layer_pt_middle,
                contents=self.layout.middle_power_toughness
            ),
            text_classes.FormattedTextArea(
                layer=self.text_layer_rules_x_y,
                contents=self.layout.middle_text,
                reference=self.textbox_reference_x_y
            ),
            # Level 3
            text_classes.TextField(
                layer=self.text_layer_level_bottom,
                contents=self.layout.bottom_level
            ),
            text_classes.TextField(
                layer=self.text_layer_pt_bottom,
                contents=self.layout.bottom_power_toughness
            ),
            text_classes.FormattedTextArea(
                layer=self.text_layer_rules_z,
                contents=self.layout.bottom_text,
                reference=self.textbox_reference_z
            )
        ])


"""
* Template Classes
"""


class LevelerTemplate(LevelerMod, NormalTemplate):
    """Template for Level-Up cards introduced in Rise of the Eldrazi."""
