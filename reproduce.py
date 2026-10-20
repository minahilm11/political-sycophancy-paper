"""Rebuild every analysis table and figure without making any model API calls."""
from pathlib import Path
import argparse
import sys

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--analysis-only',action='store_true',help='Skip all figure rendering')
    parser.add_argument('--figures-only',action='store_true',help='Reuse derived tables')
    args=parser.parse_args()
    if args.analysis_only and args.figures_only: parser.error('Choose at most one mode')
    if args.figures_only:
        from political_sycophancy.analysis import ensure_sources, verify_sources
        ensure_sources(ROOT)
        verify_sources(ROOT)
    if not args.figures_only:
        from political_sycophancy.analysis import run_analysis
        summary=run_analysis(ROOT)
        print(f'Built {len(summary)} model/identity summaries from verified political records.',flush=True)
    if not args.analysis_only:
        from political_sycophancy.plots import generate_plots
        from political_sycophancy.schematics import generate_schematics
        generate_plots(ROOT)
        generate_schematics(ROOT)
        print('Exported PNG, SVG, PDF, and interactive HTML figures.',flush=True)

if __name__=='__main__': main()
