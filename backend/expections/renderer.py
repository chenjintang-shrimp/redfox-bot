class NoSkinAvailableError(Exception):
    """没有可用的皮肤"""

    def __init__(self, skin_name: str, template_name: str):
        self.skin_name = skin_name
        self.template_name = template_name
        super().__init__(f"没有可用皮肤: {skin_name}/{template_name}")
