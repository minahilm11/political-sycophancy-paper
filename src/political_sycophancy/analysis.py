"""Political-only reconstruction from stored experiment log probabilities.

Never fit empirical values to the manually drawn manuscript points.
"""
from pathlib import Path
import hashlib
import json
import math
import zipfile
import numpy as np
import pandas as pd

PAIRS = [('liberals','conservatives'), ('collectivists','individualists'),
         ('environmentalists','industrialists'), ('socialists','capitalists'),
         ('secularists','theocrats'), ('authoritarians','libertarians'),
         ('progressives','traditionalists')]
MODELS = {'gpt_4':'GPT-4', 'gpt_3_5':'GPT-3.5'}
IDENTITY_ORDER = ['traditionalists','conservatives','theocrats','industrialists',
                  'individualists','capitalists','authoritarians','libertarians',
                  'socialists','collectivists','secularists','environmentalists',
                  'progressives','liberals']
CONDITIONS = ['opposing_bio','no_bio','agreeing_bio']

def ensure_sources(root):
    """Expand the portable political source archive when a fresh clone needs it."""
    manifest = json.loads((root/'data/source_manifest.json').read_text())
    missing = [item for item in manifest['files'] if not (root/item['path']).exists()]
    if not missing:
        return
    archive = root/'data/political_sources.zip'
    info = json.loads((root/'data/source_archive.json').read_text())
    if hashlib.sha256(archive.read_bytes()).hexdigest() != info['sha256']:
        raise ValueError('Political source archive checksum mismatch')
    expected = {item['path'] for item in manifest['files']}
    with zipfile.ZipFile(archive) as z:
        if set(z.namelist()) != expected:
            raise ValueError('Archive members differ from explicit source manifest')
        for item in missing:
            relative = Path(item['path'])
            if relative.is_absolute() or '..' in relative.parts:
                raise ValueError('Unsafe source archive path')
            content = z.read(item['path'])
            if hashlib.sha256(content).hexdigest() != item['sha256']:
                raise ValueError(f'Archived source checksum mismatch: {relative}')
            target = root/relative
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(content)

def verify_sources(root):
    manifest = json.loads((root/'data/source_manifest.json').read_text())
    expected = {item['path'] for item in manifest['files'] if item['path'].startswith('data/raw/')}
    actual = {str(path.relative_to(root)) for path in (root/'data/raw').rglob('*') if path.is_file()}
    if actual != expected:
        raise ValueError(f'Raw files differ from manifest: extra={sorted(actual-expected)}, missing={sorted(expected-actual)}')
    for item in manifest['files']:
        path = root/item['path']
        if hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError(f'Source checksum mismatch: {path}')
    return len(manifest['files'])

def load_records(root):
    rows = []
    for model in MODELS:
        for a,b in PAIRS:
            pair = f'{a}_{b}'
            for path in sorted((root/'data/raw'/f'data_{model}'/pair).glob('*_rated.jsonl')):
                for line_number,line in enumerate(path.read_text().splitlines(),1):
                    if not line.strip():
                        continue
                    d = json.loads(line)
                    logs = [d[f'{a}_agree'],d[f'{b}_agree'],d[f'empty_{a}'],d[f'empty_{b}']]
                    if not all(math.isfinite(v) and v <= 0 for v in logs):
                        raise ValueError(f'Invalid log probability: {path}:{line_number}')
                    signature = hashlib.sha256(json.dumps(d,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
                    prompt = {k:v for k,v in d.items() if k.startswith(('question','option_','profile_'))}
                    prompt_id = hashlib.sha256(json.dumps(prompt,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
                    row = dict(model=model, pair=pair, topic=path.name.removesuffix('_rated.jsonl'),
                               source_file=str(path.relative_to(root)), source_line=line_number,
                               record_id=f'{model}/{pair}/{path.stem}:{line_number}',
                               record_hash=signature, prompt_hash=prompt_id,
                               identityA=a,identityB=b,question=d['question'],
                               option_A=d[f'option_{a}'],option_B=d[f'option_{b}'],
                               profile_A=d[f'profile_{a}'],profile_B=d[f'profile_{b}'])
                    for field,value in zip(['agree_A','agree_B','empty_A','empty_B'],logs):
                        row[f'{field}_logprob'] = value
                        row[field] = 100 * math.exp(value)
                    rows.append(row)
    df = pd.DataFrame(rows)
    if df.empty:
        raise ValueError('No political experiment records found')
    return df

def identity_rows(df):
    parts = []
    for side,other in [('A','B'),('B','A')]:
        p = df[['record_id','model','pair','topic','source_file','source_line',
                'record_hash','prompt_hash']].copy()
        p['identity'] = df[f'identity{side}']
        p['agreeing_bio'] = df[f'agree_{side}']
        p['no_bio'] = df[f'empty_{side}']
        # This matches upstream plotting: the counter-option logprob was discarded.
        p['opposing_bio'] = 100 - df[f'agree_{other}']
        p['aligned_shift_pp'] = p.agreeing_bio - p.no_bio
        parts.append(p)
    return pd.concat(parts,ignore_index=True)

def logit_percent(p, epsilon=1e-6):
    p = np.clip(np.asarray(p,dtype=float)/100,epsilon,1-epsilon)
    return np.log(p) - np.log1p(-p)

def summarize(rows, groups=('model','identity')):
    groups = list(groups)
    means = rows.groupby(groups,sort=True)[CONDITIONS].mean()
    means['n_records'] = rows.groupby(groups).size()
    means['aligned_shift_pp'] = means.agreeing_bio-means.no_bio
    means['opposing_shift_pp'] = means.opposing_bio-means.no_bio
    means['aligned_delta_logit_of_means'] = logit_percent(means.agreeing_bio)-logit_percent(means.no_bio)
    paired = rows[groups].copy()
    paired['paired_delta_logit'] = logit_percent(rows.agreeing_bio)-logit_percent(rows.no_bio)
    means['mean_paired_delta_logit'] = paired.groupby(groups).paired_delta_logit.mean()
    means['fraction_positive_aligned_shift'] = rows.assign(positive=rows.aligned_shift_pp>0).groupby(groups).positive.mean()
    return means.reset_index()

def cached_summary(root):
    cached = pd.read_csv(root/'data/reference/upstream_csv/pol_data_percent.csv')
    allowed = set(PAIRS)
    if not all((a,b) in allowed for a,b in zip(cached.identityA,cached.identityB)):
        raise ValueError('Cached CSV contains nonpolitical identities')
    cached['record_id'] = np.arange(len(cached)).astype(str)
    cached['pair'] = cached.identityA+'_'+cached.identityB
    for c in ['source_file','record_hash','prompt_hash']:
        cached[c]='upstream cached CSV'
    cached['source_line']=np.arange(len(cached))+2
    return summarize(identity_rows(cached))

def run_analysis(root):
    ensure_sources(root)
    source_count = verify_sources(root)
    out = root/'data/derived'
    out.mkdir(parents=True,exist_ok=True)
    raw = load_records(root)
    rows = identity_rows(raw)
    summary = summarize(rows)
    summary.to_csv(out/'identity_summary.csv',index=False,float_format='%.10g')
    summarize(rows,('model','identity','topic')).to_csv(out/'topic_identity_summary.csv',index=False,float_format='%.10g')
    # Retain recorded repetitions in the historical primary result; expose sensitivity.
    dedup = raw.drop_duplicates(['model','pair','topic','record_hash'])
    summarize(identity_rows(dedup)).to_csv(out/'identity_summary_exact_deduplicated.csv',index=False,float_format='%.10g')
    topic_summary = summarize(rows,('model','identity','topic'))
    topic_summary.groupby(['model','identity'])[CONDITIONS].mean().reset_index().to_csv(out/'identity_summary_equal_topic_weight.csv',index=False,float_format='%.10g')
    coverage = raw.groupby(['model','pair','topic']).size().rename('n_records').reset_index()
    coverage.to_csv(out/'coverage.csv',index=False)
    raw.to_csv(out/'political_records.csv.gz',index=False,compression={'method':'gzip','mtime':0})
    rows.to_csv(out/'identity_records.csv.gz',index=False,compression={'method':'gzip','mtime':0})
    cached = cached_summary(root)
    cached.to_csv(out/'identity_summary_upstream_cached.csv',index=False,float_format='%.10g')
    estimates_path = root/'data/reference/figure5_visual_estimates.csv'
    if estimates_path.exists():
        estimates = pd.read_csv(estimates_path)
        comparisons=[]
        for label,table in [('raw_recorded',summary),('raw_exact_deduplicated',summarize(identity_rows(dedup))),('upstream_cached_csv',cached)]:
            for model,g in table.groupby('model'):
                both = g.merge(estimates,on='identity',validate='one_to_one')
                for _,r in both.iterrows():
                    for condition in CONDITIONS:
                        estimate=r[f'{condition}_percent']
                        comparisons.append(dict(dataset=label,model=model,identity=r.identity,
                            condition=condition,computed_percent=r[condition],
                            visual_estimate_percent=estimate,difference_pp=r[condition]-estimate,
                            visual_tolerance_pp=r.visual_tolerance_pp))
        comparison=pd.DataFrame(comparisons)
        comparison.to_csv(out/'figure5_comparison_to_visual_estimates.csv',index=False,float_format='%.10g')
        comparison.assign(absolute_difference=lambda x:x.difference_pp.abs()).groupby(['dataset','model']).agg(
            mean_absolute_difference_pp=('absolute_difference','mean'),
            max_absolute_difference_pp=('absolute_difference','max')).reset_index().to_csv(out/'figure5_comparison_summary.csv',index=False,float_format='%.10g')
    audit={'source_files_verified':source_count,'primary_input':'raw rated political JSONL',
           'logit_clip_epsilon':1e-6,'opposing_bio':'100 minus other identity aligned probability; binary-complement approximation',
           'models':{}}
    for model,g in raw.groupby('model'):
        mass=g.empty_A+g.empty_B
        audit['models'][model]={'n_records':len(g),'n_cells':len(g.groupby(['pair','topic'])),
            'exact_duplicate_occurrences':int(g.duplicated(['pair','topic','record_hash']).sum()),
            'duplicate_prompt_occurrences':int(g.duplicated(['pair','topic','prompt_hash']).sum()),
            'baseline_A_plus_B_mean_percent':float(mass.mean()),
            'baseline_A_plus_B_min_percent':float(mass.min()),
            'baseline_A_plus_B_max_percent':float(mass.max()),
            'logprob_minus10_occurrences':int((g[[c for c in g if c.endswith('_logprob')]]==-10).sum().sum())}
    (out/'data_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    return summary
