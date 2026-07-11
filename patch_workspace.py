import re
with open('views/dispatch_workspace.py', 'r') as f:
    content = f.read()
# Replace the broken pyplot call with the correct st.image call
new_content = re.sub(
    r'st\.pyplot\(gantt_fig, width="stretch"\)',
    'st.image(gantt_fig, use_container_width=True)',
    content
)
with open('views/dispatch_workspace.py', 'w') as f:
    f.write(new_content)
