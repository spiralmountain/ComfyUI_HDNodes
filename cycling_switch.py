import random
import secrets


class CyclingSwitch:
    """
    A switch that automatically cycles through inputs on each run.
    No external counter needed - just connects inputs and it cycles through them.
    """

    def __init__(self):
        self.counter = 0

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                "input1": ("STRING", {"forceInput": True}),
                "input2": ("STRING", {"forceInput": True}),
                "input3": ("STRING", {"forceInput": True}),
                "input4": ("STRING", {"forceInput": True}),
                "input5": ("STRING", {"forceInput": True}),
                "input6": ("STRING", {"forceInput": True}),
                "input7": ("STRING", {"forceInput": True}),
                "input8": ("STRING", {"forceInput": True}),
                "input9": ("STRING", {"forceInput": True}),
                "input10": ("STRING", {"forceInput": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("output",)
    FUNCTION = "switch"
    CATEGORY = "hdelmont/utils"

    def switch(self, input1=None, input2=None, input3=None, input4=None, input5=None,
               input6=None, input7=None, input8=None, input9=None, input10=None):
        """Cycle through connected inputs automatically"""

        # Collect all connected inputs
        inputs = []
        for inp in [input1, input2, input3, input4, input5, input6, input7, input8, input9, input10]:
            if inp is not None:
                inputs.append(inp)

        if not inputs:
            return ("",)

        # Get current input
        selected = inputs[self.counter % len(inputs)]
        
        # Increment counter for next run
        self.counter += 1

        print(f"[CyclingSwitch] Selected input {(self.counter - 1) % len(inputs) + 1} of {len(inputs)}: {selected[:50]}...")

        return (selected,)


class RandomSwitch:
    """
    A switch that randomly selects from available inputs on each run.
    Equal probability for all connected inputs.
    Uses cryptographically secure randomness - no seed needed.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                "input1": ("STRING", {"forceInput": True}),
                "input2": ("STRING", {"forceInput": True}),
                "input3": ("STRING", {"forceInput": True}),
                "input4": ("STRING", {"forceInput": True}),
                "input5": ("STRING", {"forceInput": True}),
                "input6": ("STRING", {"forceInput": True}),
                "input7": ("STRING", {"forceInput": True}),
                "input8": ("STRING", {"forceInput": True}),
                "input9": ("STRING", {"forceInput": True}),
                "input10": ("STRING", {"forceInput": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("output",)
    FUNCTION = "switch"
    CATEGORY = "hdelmont/utils"

    def switch(self, input1=None, input2=None, input3=None, input4=None, input5=None,
               input6=None, input7=None, input8=None, input9=None, input10=None):
        """Randomly select from connected inputs using secure randomness"""

        # Collect all connected inputs
        inputs = []
        for inp in [input1, input2, input3, input4, input5, input6, input7, input8, input9, input10]:
            if inp is not None:
                inputs.append(inp)

        if not inputs:
            return ("",)

        # Use secrets for true randomness (no seed needed)
        selected = secrets.choice(inputs)
        selected_idx = inputs.index(selected)

        print(f"[RandomSwitch] Randomly selected input {selected_idx + 1} of {len(inputs)}: {selected[:50]}...")

        return (selected,)


class CyclingSwitchAny:
    """
    A switch that automatically cycles through ANY type inputs on each run.
    """

    def __init__(self):
        self.counter = 0

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                "input1": ("*", {"forceInput": True}),
                "input2": ("*", {"forceInput": True}),
                "input3": ("*", {"forceInput": True}),
                "input4": ("*", {"forceInput": True}),
                "input5": ("*", {"forceInput": True}),
                "input6": ("*", {"forceInput": True}),
                "input7": ("*", {"forceInput": True}),
                "input8": ("*", {"forceInput": True}),
                "input9": ("*", {"forceInput": True}),
                "input10": ("*", {"forceInput": True}),
            }
        }

    RETURN_TYPES = ("*",)
    RETURN_NAMES = ("output",)
    FUNCTION = "switch"
    CATEGORY = "hdelmont/utils"

    def switch(self, input1=None, input2=None, input3=None, input4=None, input5=None,
               input6=None, input7=None, input8=None, input9=None, input10=None):
        """Cycle through connected inputs automatically"""

        # Collect all connected inputs
        inputs = []
        for inp in [input1, input2, input3, input4, input5, input6, input7, input8, input9, input10]:
            if inp is not None:
                inputs.append(inp)

        if not inputs:
            return (None,)

        # Get current input
        selected = inputs[self.counter % len(inputs)]
        
        # Increment counter for next run
        self.counter += 1

        print(f"[CyclingSwitchAny] Selected input {(self.counter - 1) % len(inputs) + 1} of {len(inputs)}")

        return (selected,)


class RandomSwitchAny:
    """
    A switch that randomly selects from ANY type inputs on each run.
    Uses cryptographically secure randomness - no seed needed.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                "input1": ("*", {"forceInput": True}),
                "input2": ("*", {"forceInput": True}),
                "input3": ("*", {"forceInput": True}),
                "input4": ("*", {"forceInput": True}),
                "input5": ("*", {"forceInput": True}),
                "input6": ("*", {"forceInput": True}),
                "input7": ("*", {"forceInput": True}),
                "input8": ("*", {"forceInput": True}),
                "input9": ("*", {"forceInput": True}),
                "input10": ("*", {"forceInput": True}),
            }
        }

    RETURN_TYPES = ("*",)
    RETURN_NAMES = ("output",)
    FUNCTION = "switch"
    CATEGORY = "hdelmont/utils"

    def switch(self, input1=None, input2=None, input3=None, input4=None, input5=None,
               input6=None, input7=None, input8=None, input9=None, input10=None):
        """Randomly select from connected inputs using secure randomness"""

        # Collect all connected inputs
        inputs = []
        for inp in [input1, input2, input3, input4, input5, input6, input7, input8, input9, input10]:
            if inp is not None:
                inputs.append(inp)

        if not inputs:
            return (None,)

        # Use secrets for true randomness (no seed needed)
        selected = secrets.choice(inputs)
        selected_idx = inputs.index(selected)

        print(f"[RandomSwitchAny] Randomly selected input {selected_idx + 1} of {len(inputs)}")

        return (selected,)


NODE_CLASS_MAPPINGS = {
    # New names with prefix
    "LuxuryPresence_CyclingSwitch": CyclingSwitch,
    "LuxuryPresence_RandomSwitch": RandomSwitch,
    "LuxuryPresence_CyclingSwitchAny": CyclingSwitchAny,
    "LuxuryPresence_RandomSwitchAny": RandomSwitchAny,
    # Legacy names for backward compatibility
    "CyclingSwitch": CyclingSwitch,
    "RandomSwitch": RandomSwitch,
    "CyclingSwitchAny": CyclingSwitchAny,
    "RandomSwitchAny": RandomSwitchAny
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LuxuryPresence_CyclingSwitch": "Cycling Switch 🔄",
    "LuxuryPresence_RandomSwitch": "Random Switch 🎲",
    "LuxuryPresence_CyclingSwitchAny": "Cycling Switch (Any) 🔄",
    "LuxuryPresence_RandomSwitchAny": "Random Switch (Any) 🎲",
    # Legacy names
    "CyclingSwitch": "Cycling Switch 🔄",
    "RandomSwitch": "Random Switch 🎲",
    "CyclingSwitchAny": "Cycling Switch (Any) 🔄",
    "RandomSwitchAny": "Random Switch (Any) 🎲"
}
