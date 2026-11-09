"""Run a program of the Acme support project with your API key:

    python run.py part1/04_tools/agent.py
    python run.py part1/04_tools/tool_errors.py --generic

It loads ANTHROPIC_API_KEY from the .env file next to this script (or your environment), then runs the program from its
own folder. Without a key it stops and names the recorded run of that program in its lesson folder, which holds the real
output with its tokens and cost.
"""
import os
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)
    try:
        from dotenv import load_dotenv
        load_dotenv(ROOT / '.env')
    except ImportError:
        pass
    os.environ.setdefault('PYDANTIC_AI_NO_BANNER', '1')   # Pydantic AI prints a first-run banner otherwise
    script = Path(args[0]).resolve()
    if not script.is_file():
        sys.exit(f'File not found: {args[0]}')
    if not os.environ.get('ANTHROPIC_API_KEY') and 'anthropic' in script.read_text(encoding='utf-8'):   # a program that calls no model runs without a key
        recorded = sorted((script.parent / 'recorded_runs').glob(script.stem + '*.txt'))
        sys.exit('No ANTHROPIC_API_KEY found (see SETUP.md, step 4).\n'
                 + ('Recorded run of this program: ' + ', '.join(str(r.relative_to(ROOT)) for r in recorded) if recorded else ''))
    sys.path.insert(0, str(script.parent))
    os.chdir(script.parent)
    sys.argv = [str(script)] + args[1:]
    runpy.run_path(str(script), run_name='__main__')


if __name__ == '__main__':
    main()
