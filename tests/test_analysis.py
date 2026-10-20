"""Regression checks for the political source population and probability semantics.

Expected counts and reference values were independently audited from the pinned
upstream JSONL. Synthetic cases use deliberately non-complementary baseline
probabilities, because the archive is not a normalized binary distribution.
"""
from pathlib import Path
import hashlib
import json
import math
import shutil
import subprocess
import sys
import zipfile

import numpy as np
import pandas as pd
import pytest

from political_sycophancy.analysis import (
    CONDITIONS,
    PAIRS,
    cached_summary,
    ensure_sources,
    identity_rows,
    load_records,
    logit_percent,
    summarize,
    verify_sources,
)

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PAIRS = {
    ('liberals', 'conservatives'),
    ('collectivists', 'individualists'),
    ('environmentalists', 'industrialists'),
    ('socialists', 'capitalists'),
    ('secularists', 'theocrats'),
    ('authoritarians', 'libertarians'),
    ('progressives', 'traditionalists'),
}
COMMON_TOPICS = {
    'Climate Change', 'Defense and Military', 'Economic Policies',
    'Globalization', 'Healthcare', 'Immigration', 'Law and Order',
    'Media Freedom', 'Social Equality and Rights', 'Technology and surveillance',
}
ENVIRONMENTAL_TOPICS = {
    'Climate Change', 'Economic Policies', 'Globalization',
    'Transportation', 'Veganism',
}


@pytest.fixture(scope='module')
def raw():
    ensure_sources(ROOT)
    return load_records(ROOT)


@pytest.fixture(scope='module')
def summary(raw):
    return summarize(identity_rows(raw)).set_index(['model', 'identity'])


def example_record():
    return {
        'question': 'Which policy?',
        'option_liberals': 'Policy one',
        'option_conservatives': 'Policy two',
        'profile_liberals': 'First synthetic biography',
        'profile_conservatives': 'Second synthetic biography',
        'liberals_agree': math.log(0.8),
        'conservatives_agree': math.log(0.7),
        'empty_liberals': math.log(0.6),
        'empty_conservatives': math.log(0.35),
    }


def write_example(root, record):
    path = root/'data/raw/data_gpt_4/liberals_conservatives/Test_rated.jsonl'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record)+'\n')
    return path


def test_log_probability_conversion_and_opposing_cross_side(tmp_path):
    """Own A=.8, own B=.7 means opposing A=.3 and opposing B=.2."""
    write_example(tmp_path, example_record())
    loaded = load_records(tmp_path)
    assert loaded.loc[0, 'agree_A'] == pytest.approx(80)
    assert loaded.loc[0, 'agree_B'] == pytest.approx(70)
    assert loaded.loc[0, 'empty_A'] == pytest.approx(60)
    assert loaded.loc[0, 'empty_B'] == pytest.approx(35)
    melted = identity_rows(loaded).set_index('identity')
    assert melted.loc['liberals', CONDITIONS].to_numpy(dtype=float) == pytest.approx([30, 60, 80])
    assert melted.loc['conservatives', CONDITIONS].to_numpy(dtype=float) == pytest.approx([20, 35, 70])
    assert melted.loc['liberals', 'aligned_shift_pp'] == pytest.approx(20)
    assert melted.loc['conservatives', 'aligned_shift_pp'] == pytest.approx(35)
    # Baseline token mass must remain 95%, never silently normalized to 100%.
    assert melted.no_bio.sum() == pytest.approx(95)


def test_loader_explicitly_ignores_moral_files(tmp_path):
    write_example(tmp_path, example_record())
    moral = tmp_path/'data/raw/data_gpt_4/care_harm_authority_subversion'
    moral.mkdir(parents=True)
    (moral/'Test_rated.jsonl').write_text('This must never be parsed.\n')
    loaded = load_records(tmp_path)
    assert len(loaded) == 1
    assert set(loaded.identityA) == {'liberals'}


@pytest.mark.parametrize('bad', [0.01, float('inf'), float('-inf'), float('nan')])
def test_invalid_log_probabilities_are_rejected(tmp_path, bad):
    record = example_record()
    record['liberals_agree'] = bad
    write_example(tmp_path, record)
    with pytest.raises(ValueError, match='Invalid log probability'):
        load_records(tmp_path)


def test_mean_probabilities_and_two_log_odds_estimands_are_distinct():
    # Mean aligned probability=.7, mean baseline=.3. Mean logits differ from
    # logits of those means for these asymmetrically distributed probabilities.
    rows = pd.DataFrame({
        'model': ['test', 'test'], 'identity': ['liberals', 'liberals'],
        'agreeing_bio': [50.0, 90.0], 'no_bio': [20.0, 40.0],
        'opposing_bio': [10.0, 30.0], 'aligned_shift_pp': [30.0, 50.0],
    })
    result = summarize(rows).iloc[0]
    assert result.agreeing_bio == 70
    assert result.no_bio == 30
    assert result.opposing_bio == 20
    assert result.aligned_shift_pp == 40
    assert result.n_records == 2
    assert result.fraction_positive_aligned_shift == 1
    expected_aggregate = math.log(0.7/0.3)-math.log(0.3/0.7)
    expected_paired = ((math.log(0.5/0.5)-math.log(0.2/0.8))
                       +(math.log(0.9/0.1)-math.log(0.4/0.6)))/2
    assert result.aligned_delta_logit_of_means == pytest.approx(expected_aggregate)
    assert result.mean_paired_delta_logit == pytest.approx(expected_paired)
    assert not math.isclose(expected_aggregate, expected_paired)


def test_log_odds_units_and_boundary_clipping():
    assert logit_percent([20, 50, 80]) == pytest.approx([-math.log(4), 0, math.log(4)])
    boundaries = logit_percent([0, 100])
    assert np.isfinite(boundaries).all()
    assert boundaries == pytest.approx([
        math.log(1e-6/(1-1e-6)), math.log((1-1e-6)/1e-6),
    ])


def test_manifest_is_pinned_complete_and_political_only():
    ensure_sources(ROOT)
    manifest = json.loads((ROOT/'data/source_manifest.json').read_text())
    assert manifest['commit'] == 'f300b11f75a2ffb57a0f5be3fb74d520bda717c3'
    assert {tuple(pair) for pair in manifest['political_pairs']} == EXPECTED_PAIRS
    assert set(PAIRS) == EXPECTED_PAIRS
    assert verify_sources(ROOT) == 214
    paths = [entry['path'] for entry in manifest['files']]
    assert len(paths) == len(set(paths))
    forbidden = ['care_harm', 'fairness_cheating', 'liberty_oppression',
                 'sanctity_degradation', 'authority_subversion', 'loyalty_betrayal',
                 'mft_data', 'prompt_MFT']
    assert not any(token in path for path in paths for token in forbidden)
    expected_pair_paths = {'_'.join(pair) for pair in EXPECTED_PAIRS}
    for entry in manifest['files']:
        path = ROOT/entry['path']
        assert path.stat().st_size == entry['bytes']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256']
        if entry['path'].startswith('data/raw/'):
            assert Path(entry['path']).parts[3] in expected_pair_paths
    assert sum(p.startswith('data/raw/datasets/') for p in paths) == 65
    assert sum(p.startswith('data/raw/data_gpt_4/') for p in paths) == 65
    assert sum(p.startswith('data/raw/data_gpt_3_5/') for p in paths) == 65


def test_manifest_detects_source_tampering(tmp_path):
    source = tmp_path/'data/raw/example.jsonl'
    source.parent.mkdir(parents=True)
    source.write_bytes(b'original\n')
    manifest = {'files': [{'path': 'data/raw/example.jsonl',
                          'sha256': hashlib.sha256(b'original\n').hexdigest()}]}
    (tmp_path/'data/source_manifest.json').write_text(json.dumps(manifest))
    assert verify_sources(tmp_path) == 1
    source.write_bytes(b'modified\n')
    with pytest.raises(ValueError, match='Source checksum mismatch'):
        verify_sources(tmp_path)


def test_exact_raw_coverage_and_record_provenance(raw):
    assert len(raw) == 26000
    assert raw.groupby('model').size().to_dict() == {'gpt_3_5': 13000, 'gpt_4': 13000}
    cells = raw.groupby(['model', 'pair', 'topic']).size()
    assert len(cells) == 130
    assert set(cells) == {200}
    assert raw.record_id.is_unique
    assert raw.groupby(['model', 'pair', 'topic']).source_line.min().eq(1).all()
    assert raw.groupby(['model', 'pair', 'topic']).source_line.max().eq(200).all()
    assert set(zip(raw.identityA, raw.identityB)) == EXPECTED_PAIRS
    for pair, part in raw.groupby('pair'):
        assert set(part.topic) == (ENVIRONMENTAL_TOPICS if pair == 'environmentalists_industrialists' else COMMON_TOPICS)
    assert 'Environmental Protection' not in set(raw.topic)
    assert len(identity_rows(raw)) == 52000


def test_archived_repetitions_are_preserved_and_identifiable(raw):
    exact = raw.duplicated(['model', 'pair', 'topic', 'record_hash'])
    prompt = raw.duplicated(['model', 'pair', 'topic', 'prompt_hash'])
    assert exact.groupby(raw.model).sum().to_dict() == {'gpt_3_5': 423, 'gpt_4': 233}
    assert prompt.groupby(raw.model).sum().to_dict() == {'gpt_3_5': 424, 'gpt_4': 234}
    repeated = raw[(raw.model == 'gpt_3_5') & (raw.pair == 'authoritarians_libertarians')
                   & (raw.topic == 'Climate Change')]
    assert len(repeated) == 200
    assert sorted(repeated.record_hash.value_counts()) == [20]*10
    dedup = raw.loc[~exact]
    assert dedup.groupby('model').size().to_dict() == {'gpt_3_5': 12577, 'gpt_4': 12767}
    sensitivity = summarize(identity_rows(dedup)).set_index(['model', 'identity'])
    assert sensitivity.loc[('gpt_3_5', 'authoritarians'), 'aligned_shift_pp'] == pytest.approx(39.804136778284246)
    assert sensitivity.aligned_shift_pp.gt(0).all()


@pytest.mark.parametrize('model,identity,expected', [
    ('gpt_3_5', 'authoritarians', [10.577058653492712, 42.77805507132428, 79.42780779868862]),
    ('gpt_3_5', 'capitalists', [3.0786434459186998, 15.272068623320616, 57.35711967430343]),
    ('gpt_4', 'theocrats', [7.396690887885794, 13.453807114523537, 29.69615119206575]),
])
def test_reference_identity_means_match_independent_audit(summary, model, identity, expected):
    assert summary.loc[(model, identity), CONDITIONS].to_numpy(dtype=float) == pytest.approx(expected, abs=2e-6)
    assert summary.loc[(model, identity), 'n_records'] == 2000


def test_nonbinary_mass_and_missing_token_sentinel_are_not_erased(raw):
    mass = raw.empty_A + raw.empty_B
    assert mass.groupby(raw.model).mean().to_dict() == pytest.approx({
        'gpt_3_5': 98.14969545235259, 'gpt_4': 98.9657222553249,
    })
    sentinel = raw[[f'{field}_logprob' for field in ['agree_A', 'agree_B', 'empty_A', 'empty_B']]].eq(-10).sum(axis=1)
    assert sentinel.groupby(raw.model).sum().to_dict() == {'gpt_3_5': 5005, 'gpt_4': 3950}
    assert 100*math.exp(-10) == pytest.approx(0.004539992976248485)


def test_cached_csv_population_discrepancy_is_retained(raw):
    cached = pd.read_csv(ROOT/'data/reference/upstream_csv/pol_data.csv')
    assert cached.groupby('model').size().to_dict() == {'gpt_3_5': 12924, 'gpt_4': 13122}
    fields = ['identityA', 'identityB', 'topic', 'question', 'option_A', 'option_B']
    raw_fields = fields+[f'{name}_logprob' for name in ['agree_A', 'agree_B', 'empty_A', 'empty_B']]
    csv_fields = fields+['agree_A', 'agree_B', 'empty_A', 'empty_B']
    # Compare rounded floats because pandas' default CSV parser can differ from
    # JSON's parser by tiny binary rounding errors; content remains exact.
    def keys(frame, columns):
        return {tuple(row[:6])+tuple(round(x, 10) for x in row[6:])
                for row in frame[columns].itertuples(index=False, name=None)}
    for model, extra in [('gpt_3_5', 347), ('gpt_4', 355)]:
        raw_keys = keys(raw[raw.model == model], raw_fields)
        csv_keys = keys(cached[cached.model == model], csv_fields)
        assert not (raw_keys-csv_keys)
        assert len(csv_keys-raw_keys) == extra
    historical = cached_summary(ROOT).set_index(['model', 'identity'])
    assert historical.loc[('gpt_3_5', 'authoritarians'), 'n_records'] == 1876
    assert historical.loc[('gpt_4', 'authoritarians'), 'n_records'] == 2074


def test_exported_aggregates_equal_current_analysis(summary):
    exported = pd.read_csv(ROOT/'data/derived/identity_summary.csv').set_index(['model', 'identity'])
    assert set(exported.index) == set(summary.index)
    for field in CONDITIONS+['aligned_shift_pp', 'aligned_delta_logit_of_means', 'mean_paired_delta_logit']:
        assert exported.loc[summary.index, field].to_numpy() == pytest.approx(summary[field].to_numpy(), abs=1e-7)


def test_plot_uses_selected_model_and_single_signed_rescaling(summary):
    from political_sycophancy.analysis import IDENTITY_ORDER
    from political_sycophancy.plots import dot_plot

    data = summary.reset_index()
    probability = dot_plot(data, 'gpt_4', signed=False)
    signed = dot_plot(data, 'gpt_4', signed=True)
    expected = summary.loc['gpt_4'].loc[IDENTITY_ORDER]
    # The final three traces are condition markers; preceding traces connect
    # each identity's three points. Neither plot may pool model populations.
    for i, condition in enumerate(CONDITIONS):
        actual = np.asarray(probability.data[-3+i].x, dtype=float)
        actual_signed = np.asarray(signed.data[-3+i].x, dtype=float)
        assert actual == pytest.approx(expected[condition].to_numpy())
        assert actual_signed == pytest.approx(2*expected[condition].to_numpy()-100)
        assert 'approx.' in probability.data[-3].name
    assert probability.layout.xaxis.range == (0, 100)
    assert signed.layout.xaxis.range == (-100, 100)


def make_source_archive(root, contents=None, manifest_contents=None):
    """Small independent archive fixture; no production packager is called."""
    if contents is None:
        contents = {'data/raw/example.jsonl': b'example record\n',
                    'prompts/example.txt': b'political prompt\n'}
    if manifest_contents is None:
        manifest_contents = contents
    (root/'data').mkdir(parents=True, exist_ok=True)
    entries = [{'path': name, 'sha256': hashlib.sha256(content).hexdigest(),
                'bytes': len(content)} for name, content in manifest_contents.items()]
    (root/'data/source_manifest.json').write_text(json.dumps({'files': entries}))
    archive = root/'data/political_sources.zip'
    with zipfile.ZipFile(archive, 'w') as handle:
        for name, content in contents.items():
            handle.writestr(name, content)
    (root/'data/source_archive.json').write_text(json.dumps({
        'sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
        'n_files': len(contents), 'bytes': archive.stat().st_size,
    }))
    return contents


def test_missing_sources_expand_from_verified_archive(tmp_path):
    contents = make_source_archive(tmp_path)
    ensure_sources(tmp_path)
    assert verify_sources(tmp_path) == 2
    for name, content in contents.items():
        assert (tmp_path/name).read_bytes() == content
    # Once materialized, analysis can remain offline and use verified files.
    (tmp_path/'data/political_sources.zip').unlink()
    ensure_sources(tmp_path)
    assert verify_sources(tmp_path) == 2


def test_archive_restores_missing_sources_without_overwriting_existing(tmp_path):
    make_source_archive(tmp_path)
    existing = tmp_path/'prompts/example.txt'
    existing.parent.mkdir()
    existing.write_bytes(b'user modification\n')
    ensure_sources(tmp_path)
    assert (tmp_path/'data/raw/example.jsonl').is_file()
    assert existing.read_bytes() == b'user modification\n'
    with pytest.raises(ValueError, match='Source checksum mismatch'):
        verify_sources(tmp_path)


def test_archive_outer_checksum_rejects_modified_archive(tmp_path):
    make_source_archive(tmp_path)
    archive = tmp_path/'data/political_sources.zip'
    archive.write_bytes(archive.read_bytes()+b'tampered')
    with pytest.raises(ValueError, match='archive checksum mismatch'):
        ensure_sources(tmp_path)
    assert not (tmp_path/'data/raw').exists()


def test_archive_inner_checksum_rejects_modified_member(tmp_path):
    make_source_archive(tmp_path,
        contents={'data/raw/example.jsonl': b'incorrect'},
        manifest_contents={'data/raw/example.jsonl': b'expected'})
    with pytest.raises(ValueError, match='Archived source checksum mismatch'):
        ensure_sources(tmp_path)
    assert not (tmp_path/'data/raw/example.jsonl').exists()


@pytest.mark.parametrize('archive_names, manifest_names', [
    ({'data/raw/expected.jsonl', 'data/raw/unexpected.jsonl'}, {'data/raw/expected.jsonl'}),
    ({'data/raw/expected.jsonl'}, {'data/raw/expected.jsonl', 'data/raw/missing.jsonl'}),
])
def test_archive_member_inventory_must_match_manifest(tmp_path, archive_names, manifest_names):
    make_source_archive(tmp_path,
        contents={name: b'content' for name in archive_names},
        manifest_contents={name: b'content' for name in manifest_names})
    with pytest.raises(ValueError, match='Archive members differ'):
        ensure_sources(tmp_path)


@pytest.mark.parametrize('malicious_path', ['../escaped.txt', '/tmp/unsafe-political-archive-test.txt'])
def test_archive_rejects_path_traversal(tmp_path, malicious_path):
    make_source_archive(tmp_path, contents={malicious_path: b'must not be written'})
    with pytest.raises(ValueError, match='Unsafe source archive path'):
        ensure_sources(tmp_path)
    assert not (tmp_path.parent/'escaped.txt').exists()


def test_unmanifested_raw_file_is_rejected(tmp_path):
    make_source_archive(tmp_path)
    ensure_sources(tmp_path)
    (tmp_path/'data/raw/extra_rated.jsonl').write_text('unmanifested\n')
    with pytest.raises(ValueError, match='Raw files differ from manifest'):
        verify_sources(tmp_path)


def test_missing_raw_file_is_rejected_without_silent_omission(tmp_path):
    make_source_archive(tmp_path)
    ensure_sources(tmp_path)
    (tmp_path/'data/raw/example.jsonl').unlink()
    with pytest.raises(ValueError, match='Raw files differ from manifest'):
        verify_sources(tmp_path)


def test_fresh_portable_copy_rebuilds_analysis_without_expanded_sources(tmp_path):
    """Run the real CLI with only portable files and no precomputed tables."""
    clone = tmp_path/'fresh-copy'
    clone.mkdir()
    shutil.copy2(ROOT/'reproduce.py', clone/'reproduce.py')
    shutil.copytree(ROOT/'src', clone/'src', ignore=shutil.ignore_patterns('__pycache__'))
    portable = ['data/political_sources.zip', 'data/source_archive.json',
                'data/source_manifest.json', 'data/reference/figure5_visual_estimates.csv']
    for relative in portable:
        target = clone/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT/relative, target)
    assert not (clone/'data/raw').exists()
    assert not (clone/'prompts').exists()
    assert not (clone/'data/reference/upstream_csv').exists()
    assert not (clone/'data/derived').exists()
    completed = subprocess.run([sys.executable, str(clone/'reproduce.py'), '--analysis-only'],
                               cwd=clone, text=True, capture_output=True, timeout=60)
    assert completed.returncode == 0, completed.stdout+completed.stderr
    assert 'Built 28 model/identity summaries' in completed.stdout
    assert verify_sources(clone) == 214
    rebuilt = pd.read_csv(clone/'data/derived/identity_summary.csv').set_index(['model', 'identity'])
    shipped = pd.read_csv(ROOT/'data/derived/identity_summary.csv').set_index(['model', 'identity'])
    pd.testing.assert_frame_equal(rebuilt, shipped)
    audit = json.loads((clone/'data/derived/data_audit.json').read_text())
    assert audit['source_files_verified'] == 214
    assert {model: values['n_records'] for model, values in audit['models'].items()} == {
        'gpt_3_5': 13000, 'gpt_4': 13000,
    }
