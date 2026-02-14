"""
UI Configuration Loader
"""
import yaml
from pathlib import Path
from config.settings import settings


class UIConfigLoader:
    """UI კონფიგურაციების ჩატვირთვა"""
    
    def __init__(self):
        self.config_dir = settings.CONFIG_DIR / "ui"
    
    def load_css(self):
        """CSS-ის ჩატვირთვა"""
        css_path = self.config_dir / "styles.css"
        try:
            with open(css_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return ""
    
    def load_ui_config(self):
        """UI კონფიგურაციის ჩატვირთვა"""
        config_path = self.config_dir / "ui_config.yaml"
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {}
    
    def load_sample_questions(self):
        """სატესტო კითხვების ჩატვირთვა"""
        questions_path = self.config_dir / "sample_questions.yaml"
        try:
            with open(questions_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data.get('all_questions', [])
        except FileNotFoundError:
            return []
    
    def load_questions_by_category(self):
        """კითხვები კატეგორიებად"""
        questions_path = self.config_dir / "sample_questions.yaml"
        try:
            with open(questions_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data.get('categories', {})
        except FileNotFoundError:
            return {}


# Helper function
def load_ui_css():
    """CSS-ის სწრაფი ჩატვირთვა"""
    loader = UIConfigLoader()
    return loader.load_css()

def load_questions():
    """კითხვების სწრაფი ჩატვირთვა"""
    loader = UIConfigLoader()
    return loader.load_sample_questions()