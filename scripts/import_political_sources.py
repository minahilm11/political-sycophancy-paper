"""Copy an explicit political-only allowlist from the pinned upstream checkout."""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import shutil
import subprocess

PAIRS = [('liberals','conservatives'), ('collectivists','individualists'),
         ('environmentalists','industrialists'), ('socialists','capitalists'),
         ('secularists','theocrats'), ('authoritarians','libertarians'),
         ('progressives','traditionalists')]
COMMIT = 'f300b11f75a2ffb57a0f5be3fb74d520bda717c3'
URL = 'https://github.com/minahilm11/Detecting-and-measuring-moral-and-political-Sycophancy-in-LLMs'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('checkout', type=Path)
    args = parser.parse_args()
    src = args.checkout.resolve()
    root = Path(__file__).resolve().parents[1]
    revision = subprocess.check_output(['git','-C',str(src),'rev-parse','HEAD'], text=True).strip()
    if revision != COMMIT:
        raise ValueError(f'Expected pinned upstream {COMMIT}, found {revision}')
    manifest = []
    def copy(rel, dest):
        source = src / rel
        target = root / dest
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        manifest.append({'source_path':str(rel), 'path':str(dest),
                         'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
                         'bytes':target.stat().st_size, 'transformation':'none'})
    for a,b in PAIRS:
        pair = f'{a}_{b}'
        for prefix, glob in [('datasets','*.json'),('data_gpt_4','*.jsonl'),('data_gpt_3_5','*.jsonl')]:
            for source in sorted((src/prefix/pair).glob(glob)):
                rel = source.relative_to(src)
                copy(rel, Path('data/raw')/rel)
        for prefix, name in [('few_shot_examples', f'examples_{pair}.txt'),
                             ('dataset_gen_prompts', f'example_prompt_{pair}.txt')]:
            rel = Path(prefix)/name
            copy(rel, Path('prompts')/rel)
    copy(Path('prompt_political.txt'), Path('prompts/prompt_political.txt'))
    copy(Path('dataset_generation_political.py'), Path('historical/dataset_generation_political.py'))
    for name in ['pol_data.csv','pol_data_percent.csv']:
        copy(Path('csv_data')/name, Path('data/reference/upstream_csv')/name)
    # Preserve the experiment implementation, restricting its pair list explicitly.
    original = (src/'sycophancy_testing_all_IDs.py').read_text()
    tree = ast.parse(original)
    assignment = next(n for n in tree.body if isinstance(n,ast.Assign)
                      and any(isinstance(t,ast.Name) and t.id=='identity_pairs' for t in n.targets))
    lines = original.splitlines(keepends=True)
    lines[assignment.lineno-1:assignment.end_lineno] = ['identity_pairs = '+repr(PAIRS)+'\n']
    target = root/'historical/sycophancy_testing_political.py'
    target.write_text(''.join(lines))
    manifest.append({'source_path':'sycophancy_testing_all_IDs.py',
                     'path':str(target.relative_to(root)),
                     'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
                     'bytes':target.stat().st_size,
                     'transformation':'identity_pairs restricted to seven political pairs; all other code retained'})
    (root/'data/source_manifest.json').write_text(json.dumps({
        'upstream_url':URL, 'commit':COMMIT, 'retrieved_date':'2026-10-20',
        'political_pairs':PAIRS,'files':manifest},indent=2)+'\n')
    print(f'Imported {len(manifest)} political source files from {revision}')

if __name__ == '__main__':
    main()
