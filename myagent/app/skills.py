import yaml
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent / "skills"


def list_skills():
    if not SKILL_DIR.exists():
        return []
    return [f.stem for f in SKILL_DIR.glob("*.yaml")]


def load_skill(name: str) -> dict:
    path = SKILL_DIR / f"{name}.yaml"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def is_file_path(text: str) -> bool:
    path = Path(text)
    return path.exists() and path.is_file()


def read_file_content(file_path: str) -> str:
    try:
        return Path(file_path).read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return f"Error reading file: {e}"


def write_file_content(file_path: str, content: str) -> bool:
    try:
        Path(file_path).write_text(content, encoding="utf-8")
        return True
    except Exception as e:
        return False


def run_skill(skill_name: str, inputs: dict, provider):
    skill = load_skill(skill_name)
    if not skill:
        return f"Skill '{skill_name}' not found"

    prompt = skill["prompt"]
    for key, val in inputs.items():
        if is_file_path(val):
            val = read_file_content(val)
        prompt = prompt.replace("{" + key + "}", val)

    result = provider.generate(prompt, system="")
    return result["text"] if isinstance(result, dict) else result


def run_skill_with_fix(skill_name: str, inputs: dict, provider, auto_fix: bool = False):
    skill = load_skill(skill_name)
    if not skill:
        return f"Skill '{skill_name}' not found", None

    original_path = None
    prompt = skill["prompt"]
    for key, val in inputs.items():
        if is_file_path(val):
            original_path = val
            val = read_file_content(val)
        prompt = prompt.replace("{" + key + "}", val)

    fix_prompt = prompt + "\n\nIf there are issues, provide the FIXED version of the code between ```fixed and ``` markers."
    result = provider.generate(fix_prompt, system="")
    text = result["text"] if isinstance(result, dict) else result

    fixed_code = None
    if "```fixed" in text and "```" in text.split("```fixed")[1]:
        fixed_code = text.split("```fixed")[1].split("```")[0].strip()

    if auto_fix and fixed_code and original_path:
        write_file_content(original_path, fixed_code)
        return text, original_path

    return text, None
