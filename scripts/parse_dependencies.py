import ast
import sys

def extract_python_modules(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    analysis = ast.literal_eval(content)
    # Pure Python modules list is always element #14
    pure_modules = analysis[14]
    modules = set()
    for name, file_path, entry_type in pure_modules:
        if "site-packages" not in file_path.lower():
            continue
        if entry_type not in ("PYMODULE", "EXTENSION"):
            continue
        modules.add(name.split('.')[0])
    return sorted(modules)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python parse_dependencies.py <path_to_toc_file> <output_path>")
        sys.exit(1)
    toc_path = sys.argv[1]
    output_path = sys.argv[2]
    deps = extract_python_modules(toc_path)
    with open(output_path, "w", encoding="utf-8") as out:
        out.write("\n".join(deps))
