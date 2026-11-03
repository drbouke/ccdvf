"""Check that this machine is ready for the course code.

    python check_setup.py          checks Python, the packages, the API key and Claude Code (no request sent)
    python check_setup.py --ping   also sends one tiny request to Claude Haiku 5.5 (costs a small fraction of a cent)
"""
import importlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

ok = True


def line(passed, what, hint=''):
    global ok
    ok = ok and passed
    print(('  [ok]   ' if passed else '  [fix]  ') + what + ('' if passed or not hint else '\n         ' + hint))


print('Python and packages')
line(sys.version_info >= (3, 11), 'Python %d.%d' % sys.version_info[:2], 'Install Python 3.11 or later from python.org.')
for module, package in (('anthropic', 'anthropic'), ('claude_agent_sdk', 'claude-agent-sdk'), ('pydantic_ai', 'pydantic-ai-slim'),
                        ('dotenv', 'python-dotenv'), ('pytest', 'pytest')):
    try:
        importlib.import_module(module)
        line(True, package)
    except ImportError:
        line(False, package + ' is missing', 'Run: pip install -r requirements.txt  (inside your virtual environment)')

print('API key')
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / '.env')
except ImportError:
    pass
key = os.environ.get('ANTHROPIC_API_KEY', '')
if key:
    line(key.startswith('sk-ant-'), 'ANTHROPIC_API_KEY is set: %s' % key,
         'The key should start with sk-ant-. Copy it again from the Class Key slide.')
else:
    line(False, 'No ANTHROPIC_API_KEY', 'Paste the class key into .env (SETUP.md, step 4). Until then, read the recorded runs in recorded_runs/.')

print('Claude Code')
claude = shutil.which('claude')
if claude:
    try:
        out = subprocess.run([claude, '--version'], capture_output=True, text=True, timeout=30).stdout.strip()
        line(True, 'claude ' + out)
    except Exception as e:
        line(False, 'claude did not start: %s' % e, 'See SETUP.md, step 5.')
else:
    print('  [info] Claude Code is not installed. It is needed for the Claude Code demos only. See SETUP.md, step 5.')

if '--ping' in sys.argv:
    print('Request to Claude')
    if not key:
        line(False, 'No key to send a request with', 'Set ANTHROPIC_API_KEY first.')
    else:
        try:
            import anthropic
            resp = anthropic.Anthropic().messages.create(
                model='claude-haiku-5-5', max_tokens=2500,
                messages=[{'role': 'user', 'content': 'Reply with the single word: Ready'}])
            line(True, 'Claude answered: %s (%d input, %d output tokens)' % (
                ''.join(b.text for b in resp.content if b.type == 'text').strip(), resp.usage.input_tokens, resp.usage.output_tokens))
        except Exception as e:
            line(False, 'The request failed: %s' % e,
                 'Check the key, the credit balance and the spend limit in the Claude Console.')

print('\nReady.' if ok else '\nFix the items marked [fix], then run this check again.')
sys.exit(0 if ok else 1)
