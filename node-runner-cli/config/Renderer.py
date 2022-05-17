import os

import yaml
from jinja2 import Environment, FileSystemLoader


class Renderer:
    def load_file_based_template(self, template_file_name: str, template_path="templates"):
        self.env = Environment(loader=FileSystemLoader(f"{os.getcwd()}/{template_path}"), trim_blocks=True,
                               lstrip_blocks=True)
        self.template = self.env.get_template(f"{template_file_name}")
        return self

    def render(self, config):
        self.rendered = self.template.render(config)
        return self

    def to_yaml(self):
        def represent_none(self, _):
            return self.represent_scalar('tag:yaml.org,2002:null', '')

        yaml.add_representer(type(None), represent_none)
        return yaml.safe_load(self.rendered)
