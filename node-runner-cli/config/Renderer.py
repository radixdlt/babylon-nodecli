import os
import sys
from os.path import dirname, join

import yaml
from jinja2 import Environment, FileSystemLoader


class Renderer:
    def load_file_based_template(
        self, template_file_name: str, templates_dir="templates"
    ):
        templates_path = join(dirname(dirname(__file__)), templates_dir)
        self.env = Environment(
            loader=FileSystemLoader(templates_path),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.env.filters["bool"] = bool
        self.template = self.env.get_template(template_file_name)
        return self

    def render(self, config):
        self.rendered = self.template.render(config)
        return self

    def to_yaml(self):
        def represent_none(self, _):
            return self.represent_scalar("tag:yaml.org,2002:null", "")

        yaml.add_representer(type(None), represent_none)
        return yaml.safe_load(self.rendered)

    def to_file(self, filepath: str):
        with open(filepath, "w") as f:
            f.write(self.rendered)
