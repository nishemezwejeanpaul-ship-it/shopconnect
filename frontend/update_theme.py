import os

src_dir = r"E:\project\shopconnect\frontend\src"

index_css = """@import "tailwindcss";

:root {
  --color-primary: #16A34A;
  --color-primary-dark: #15803D;
  --color-accent: #D97706;
  --color-bg: #F9FAFB;
  --color-border: #E5E7EB;
  --color-text: #111827;
  --color-muted: #6B7280;
  --color-error: #DC2626;
}

@theme {
  --color-primary: var(--color-primary);
  --color-primary-dark: var(--color-primary-dark);
  --color-accent: var(--color-accent);
  --color-bg: var(--color-bg);
  --color-border: var(--color-border);
  --color-text: var(--color-text);
  --color-muted: var(--color-muted);
  --color-error: var(--color-error);
}

body {
  background-color: var(--color-bg);
  color: var(--color-text);
}
"""

with open(os.path.join(src_dir, "index.css"), "w", encoding="utf-8") as f:
    f.write(index_css)

def update_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Replacements
    replacements = {
        # Backgrounds
        "bg-indigo-600": "bg-primary",
        "hover:bg-indigo-700": "hover:bg-primary-dark",
        "bg-blue-600": "bg-primary",
        "hover:bg-blue-700": "hover:bg-primary-dark",
        "bg-slate-50": "bg-bg",
        "from-slate-50": "from-bg",
        "to-indigo-50": "to-primary/10",
        "to-blue-50": "to-primary/10",
        "hover:bg-slate-50": "hover:bg-bg",
        "hover:bg-slate-100": "hover:bg-border/50",
        
        # Text
        "text-indigo-600": "text-primary",
        "hover:text-indigo-800": "hover:text-primary-dark",
        "text-blue-600": "text-primary",
        "hover:text-blue-800": "hover:text-primary-dark",
        "text-slate-900": "text-text",
        "text-slate-800": "text-text",
        "text-slate-700": "text-text",
        "text-slate-600": "text-muted",
        "text-slate-500": "text-muted",
        "text-slate-400": "text-muted",
        "text-red-600": "text-error",
        "text-red-500": "text-error",
        "hover:text-red-800": "hover:text-error",
        
        # Borders
        "border-slate-100": "border-border",
        "border-slate-200": "border-border",
        "border-slate-300": "border-border",
        "border-red-500": "border-error",
        "border-red-100": "border-error/30",
        
        # Rings
        "focus:ring-indigo-500": "focus:ring-primary",
        "focus:ring-blue-500": "focus:ring-primary",
    }
    
    for old, new in replacements.items():
        content = content.replace(old, new)
        
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

update_file(os.path.join(src_dir, "pages", "LoginPage.jsx"))
update_file(os.path.join(src_dir, "pages", "RegisterPage.jsx"))
update_file(os.path.join(src_dir, "components", "Navbar.jsx"))
print("Theme updated successfully!")
