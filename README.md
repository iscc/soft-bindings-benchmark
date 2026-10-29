# ISCC rerun of the soft-bindings benchmark

In this fork of [Original-Pictures/soft-bindings-benchmark](https://github.com/Original-Pictures/soft-bindings-benchmark),
we rerun the paper's ISCC image methods in the paper's harness, with ISCC releases that fix two
flaws in the Image-Code implementation. The original README follows
[below](#watermarks-and-fingerprints-as-soft-bindings-for-content-provenance).

- Up to iscc-sdk 0.9.6, the border trim before hashing cropped only borders of exactly one colour, so a watermark
  or faint noise on a white background switched the crop off. The paper attributed its ISCC watermark and
  transfer-attack failures to this step. Since iscc-sdk 0.9.7 the trim tolerates differences of up to 16 grey
  levels. We chose the trim's design and tolerance using this benchmark's images.
- Since iscc-core 1.5.0 and iscc-lib 0.7.0, bits 65 to 256 of the Image-Code come from the top-right, bottom-left
  and bottom-right 8×8 squares of the 16×16 low-frequency DCT block, the squares ISO 24138 5.4.5.2 e) names;
  earlier versions used copies of the first square shifted by one coefficient. This fix leaves 64-bit Image-Codes
  unchanged.

## Results

With the paper's ISCC versions (iscc-sdk 0.9.5, iscc-core 1.4.0, iscc-lib 0.6.0), our rerun reproduces the
paper's image-track results exactly, its watermark results within 0.3 points and its security results within 2.
The differences below therefore come from the update (iscc-sdk 0.9.7, iscc-core 1.5.0, iscc-lib 0.7.0). Each
method has its own threshold in each run, calibrated to a pair-level false-match rate of 10⁻⁷ unless marked
otherwise. ↑ means higher is better, ↓ lower is better; bold marks the better of paper and update.

| | ISCC-Image-64 paper | ISCC-Image-64 update | ISCC-Image-256 paper | ISCC-Image-256 update | PDQ paper |
|---|---|---|---|---|---|
| **Watermark-combination track** (300 product photos marked with TrustMark Q) | | | | | |
| ↓ Marked photos no longer matching their unmarked original | 62.0 % | **3.7 %** | 56.7 % | **1.3 %** | 0.3 % |
| ↑ Attacked marked copies matched, registry holds the unmarked originals | 19.0 % | **43.0 %** | 21.9 % | **48.2 %** | 49.2 % |
| ↑ Attacked marked copies matched, registry holds the marked photos | **47.1 %** | 43.9 % | 48.7 % | **49.1 %** | 49.5 % |
| **Image track** (72,000 attacked copies) | | | | | |
| ↑ Attacked copies matched | 42.7 % | **43.9 %** | 45.8 % | **49.1 %** | 49.5 % |
| **Security track** (100 registered originals, false-match rate 10⁻⁶) | | | | | |
| ↓ Evaded by the transfer attack, 2 grey levels | 54 % | **0 %** | 52 % | **0 %** | 0 % |
| ↓ Evaded by the transfer attack, 16 grey levels | 56 % | **26 %** | 55 % | **9 %** | 0 % |
| ↓ Evaded by the surrogate attack, 2 grey levels (10⁻⁷) | 81 % | **41 %** | – | – | 22 % |

The transfer attack is crafted on three neural models (DINOv2-S, SSCD, OpenCLIP), not on the hash it is scored
against. The surrogate attack follows the gradient of a differentiable surrogate of the hash, which the paper built
for ISCC-Image-64 but not for ISCC-Image-256. Grey levels are the largest change an attack may make to any pixel
value, out of 255. [RESULTS.md](fingerprinting/bench-2026-10/results-iscc/RESULTS.md) has the detailed results and
lists the numbers in the paper's text that change.

### Semantic-Code

The paper ran the ISCC Semantic-Code only in its pilot; its harness places it in the reference tier, with
ISC21-1st, from which its model derives. On the full image track, with the paper's adapter, ISCC-SCI-256
(iscc-sci 0.4.1) matches 68.7 % of attacked copies at 10⁻⁷, against 49.1 % for ISCC-Image-256 and 75.5 % for
ISC21-1st. At 10⁻⁶ the transfer attack evades it for 44 % of originals at 16 grey levels (ISCC-Image-256: 9 %); no
white-box attack was run on it.

## How it was run

The [`iscc-update`](https://github.com/iscc/soft-bindings-benchmark/tree/iscc-update) branch changes the harness
in two commits: one sets the ISCC version pins in
[`scripts/requirements.in`](fingerprinting/bench-2026-10/scripts/requirements.in), the other makes the ISCC
surrogate in [`scripts/hash_surrogates.py`](fingerprinting/bench-2026-10/scripts/hash_surrogates.py) trim borders
like the installed iscc-sdk instead of like iscc-sdk 0.9.5. Both are merged here, so the original README's
instructions install the update, while `results-gpu/` keeps the paper's records. Our scripts are in
[`iscc/`](fingerprinting/bench-2026-10/iscc/), the records and frozen environments in
[`results-iscc/`](fingerprinting/bench-2026-10/results-iscc/). Not rerun: the audio and video parts of every track
(the update leaves the Audio-Code and Video-Code unchanged), edit retrieval and localisation, latency, cross-host
stability, descriptor inversion and the two-of-three duplicate rule.

To rerun both versions on a Linux host with a copy of DISC21 (see `iscc/run.sh`):

```sh
cd fingerprinting/bench-2026-10
PY="uv run --no-project --with numpy==2.4.6 --with scipy==1.17.1 python"
for v in 0.9.5 0.9.7; do
  iscc/run.sh setup $v && iscc/run.sh image $v && iscc/run.sh wm $v &&
    iscc/run.sh security $v && iscc/run.sh sensitivity $v && $PY iscc/stats.py $v
done
$PY iscc/compare.py
```

## Use of generative AI

Claude (Anthropic) wrote the scripts in `iscc/` and the harness changes, ran the benchmark and drafted this text.
Titusz Pan (ISCC Foundation) set the scope, reviewed the results and the text, and is responsible for both.

---

# Watermarks and Fingerprints as Soft Bindings for Content Provenance

Code, results and LaTeX source for the preprint *Watermarks and Fingerprints as Soft Bindings for Content Provenance: An Open-Licence Benchmark for Images, Audio and Video*. The authors are Seyedmahdi Kazempourradi, Ramtin Mojtahedi and Behrang Mohseni, all at Original Pictures Technologies, Inc.

C2PA soft bindings recover a stripped provenance manifest from the content itself, in one of two ways: an invisible watermark read from the media, or a fingerprint looked up in a registry. This repository benchmarks openly licensed methods of both kinds on public media for images, audio and video, under one protocol:
- false-match rates are calibrated on held-out negatives;
- uncertainty is estimated at the level of the source item.

The compiled paper is [`soft-bindings-preprint.pdf`](soft-bindings-preprint.pdf).

## Layout

| Path | Contents |
|---|---|
| `paper/` | Manuscript: `main.tex`, `sections/`, `refs.bib`. `scripts/assemble.py` collects both tracks' generated numbers, tables and figures. `build.sh` rebuilds the PDF. |
| `watermarking/bench-2026-09/` | Watermarking track. `scripts/` is the harness (corpus fetch, embedding, attacks, decoding, aggregation). `results-gpu/` and `results-followup/` hold the raw per-configuration records, and `results.json` the aggregate. `paper/scripts/` generates this track's numbers, tables and figures. |
| `fingerprinting/bench-2026-10/` | Fingerprinting track. `scripts/` is the harness (fingerprint adapters, retrieval, localization, security, watermark complementarity). `results-gpu/` holds the raw records, including per-query score arrays (`_perquery/`). `tests/` holds the unit tests. `paper/scripts/` generates this track's numbers, tables and figures. |

`corpus_manifest.json` and `results-gpu/locks/` pin the inputs:
- each corpus item, with its source URL, licence and SHA-256;
- model weights (`weights.lock.json`) and upstream source trees (`sources.lock.json`);
- the Python environments of the GPU hosts (`requirements-gpu-*.lock`).

## Rebuild the paper from the recorded results

Requires [uv](https://docs.astral.sh/uv/), Python 3.11+ and Docker.

```sh
./paper/build.sh
```

The script:
1. runs both tracks' `paper/scripts/build_numbers.py`, which writes every cited number to `generated/numbers.tex` and writes every table;
2. assembles them into `paper/`;
3. compiles with pdfLaTeX in `texlive/texlive:latest-medium`;
4. packs the arXiv source and recompiles it without BibTeX;
5. writes `soft-bindings-preprint.pdf`.

No number in the manuscript is typed by hand. Each is a `\val{...}` macro produced in step 1 from the files in `results*/`.

Figures are committed. To redraw one, run the track's `paper/scripts/figures.py` (requires matplotlib). The galleries and residual figures also need the benchmark media, which are not distributed (see below).

## Re-run the experiments

Media never enter the repository. `fetch_corpus.py` downloads every item from its original source into `$BENCH_WORK` and checks it against the manifest hashes. Each track runs on its own:

```sh
cd watermarking/bench-2026-09            # or fingerprinting/bench-2026-10
export BENCH_WORK=~/wm-bench-work         # media, descriptors and caches
uv venv -p 3.11 $BENCH_WORK/.venv
uv pip install --python $BENCH_WORK/.venv/bin/python -r scripts/requirements.in
cd scripts
python fetch_sources.py && python fetch_weights.py   # pinned trees, SHA-256-checked weights
python fetch_corpus.py                               # fingerprinting: --scale full
```

**Watermarking:**
```sh
python bench_image.py && python bench_audio.py && python bench_video.py && python stability.py make
python aggregate.py <results dir>
```

**Fingerprinting:**
- Run `pytest ../tests` first.
- Then run the stages defined in `scripts/gpu/stage.sh`, in this order: image, audio, nmfp, video, wm, edits, security, stability, latency.

**Hardware used for the recorded results:**
- AWS g5.xlarge and g5.2xlarge (NVIDIA A10G 24 GB, AMD EPYC 7R32);
- a c5a CPU host for hash extraction;
- an Apple M5 Pro for the cross-device checks.

**AWS helper scripts.** `scripts/gpu/` holds helpers that provision a tagged temporary instance, move files through a scratch S3 bucket, run stages over SSM and tear everything down.
- They need `AWS_PROFILE_BENCH` and `BENCH_AWS_ACCOUNT`, and refuse any other account.
- `BENCH_PROTECTED_INSTANCE` can name an instance that teardown must never touch.
- `sync.sh down` uses `aws s3 sync --delete`, which deletes local results the host does not have.

The two decoder environments that cannot share dependencies are pinned separately: SilentCipher in `requirements-gpu-silentcipher.lock`, and NMFP (TensorFlow) in `requirements-gpu-nmfp.lock`.

## Licences

- **Code** (everything outside `paper/` and the PDF): [Apache-2.0](LICENSE).
- **Manuscript, figures and tables:** [CC BY 4.0](LICENSE-paper).
- **Third-party models and data:** not redistributed. `fetch_weights.py` and `fetch_corpus.py` download them under their own licences, which the paper's method tables list. Several were measured as reference points only:
  - DISC21 was used under its non-commercial research licence.
  - The SSCD and ISC21 weights were trained on DISC21.
  - NMFP is GPL-3.0 and runs as an external tool in its own environment.

## Citation

See [`CITATION.cff`](CITATION.cff). Correspondence: Seyedmahdi Kazempourradi, mahdi@originalpictures.com.
