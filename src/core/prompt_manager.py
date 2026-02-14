"""
Prompt Template Manager
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

import yaml
from config.settings import settings


class PromptManager:
    """Prompt templates manager"""
    
    def __init__(self, prompts_file="base.yaml"):
        self.prompts_path = settings.PROMPTS_DIR / prompts_file
        self.prompts = self._load_prompts()
    
    def _load_prompts(self):
        """ჩატვირთე prompts YAML ფაილიდან"""
        try:
            with open(self.prompts_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompts file not found: {self.prompts_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML: {e}")
    
    def get_prompt(self, prompt_name="base"):
        """მოიძიე prompt template"""
        if prompt_name not in self.prompts:
            raise ValueError(f"Prompt '{prompt_name}' not found")
        return self.prompts[prompt_name]
    
    def build_prompt(self, prompt_name="base", **variables):
        """ააშენე სრული prompt"""
        prompt_config = self.get_prompt(prompt_name)
        full_prompt = prompt_config['system'] + "\n\n" + prompt_config['template']
        
        try:
            return full_prompt.format(**variables)
        except KeyError as e:
            raise ValueError(f"Missing variable: {e}")
    
    def get_metadata(self, prompt_name="base"):
        """მიიღე metadata"""
        prompt_config = self.get_prompt(prompt_name)
        return {
            'temperature': prompt_config.get('temperature', 0.0),
            'max_tokens': prompt_config.get('max_tokens', 2000)
        }
    
    def list_prompts(self):
        """ყველა prompt-ის სია"""
        return list(self.prompts.keys())


if __name__ == "__main__":
    manager = PromptManager()
    print("📋 ხელმისაწვდომი prompts:", manager.list_prompts())
    
    prompt = manager.build_prompt("base", context="დღგ 18%", question="რა არის დღგ?")
    print("\n🔍 Base prompt:")
    print(prompt[:200] + "...")
    
    print("\n⚙️ Metadata:", manager.get_metadata("base"))