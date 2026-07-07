class NoSkinAvailableError(Exception):
    """没有可用的皮肤"""

    template_key = "NO_SKIN_AVAILABLE_TEMPLATE"

    def __init__(self, skin_name: str, template_name: str):
        self.skin_name = skin_name
        self.template_name = template_name
        self.error_msg = f"没有可用皮肤: {skin_name}/{template_name}"
        super().__init__(self.error_msg)
