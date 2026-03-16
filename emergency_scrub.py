
import os

def scrub_pii():
    targets = ['user', 'user']
    root_dir = r'.'
    
    for root, dirs, files in os.walk(root_dir):
        # Skip .git if it still exists (we'll delete it later anyway)
        if '.git' in dirs:
            dirs.remove('.git')
            
        for file in files:
            if file.endswith(('.py', '.json', '.md', '.lua', '.bat')):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    for target in targets:
                        content = content.replace(target, 'user')
                    
                    # Also replace the full path if it appears
                    content = content.replace('.', '.')
                    content = content.replace('.', '.')
                    
                    if content != original_content:
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"Scrubbed: {path}")
                except Exception as e:
                    print(f"Error reading {path}: {e}")

if __name__ == "__main__":
    scrub_pii()
