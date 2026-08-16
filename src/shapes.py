"""Group attested Indus signs from their rendered shapes.

The font, not sign-number adjacency, supplies the evidence here.  This script
renders every usable mapping, measures aligned overlap/containment and chamfer
distance, derives clustering cuts from two-component mixtures of the observed
nearest-neighbour distributions, and writes machine-readable groups plus a
contact sheet.  Run ``src/shapes_validate.py`` afterwards for the independent
and corpus-side tests.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from scipy import ndimage
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform
from sklearn.mixture import GaussianMixture


ROOT = Path(__file__).resolve().parents[1]
FONT_PATH = ROOT / "data/yaj/src/assets/fonts/sk_indus_script-webfont.ttf"
LINES_PATH = ROOT / "data/parsed/lines.json"
GLYPHS_PATH = ROOT / "data/parsed/glyphs.json"
OUT_PATH = ROOT / "data/parsed/shape_families.json"
RASTER_CACHE = ROOT / "data/parsed/shape_rasters.npz"
PAIR_CACHE = ROOT / "data/parsed/shape_pairwise.npz"
RESIDUAL_CACHE = ROOT / "data/parsed/shape_residuals.npz"
SHEET_PATH = ROOT / "notes/shape-families.png"
RESIDUAL_SHEET_PATH = ROOT / "notes/shape-residuals.png"

CANVAS = 64
INNER = 52
RENDER_SIZE = 256
SCALES = (0.90, 1.00, 1.10)
SHIFTS = (-2, 0, 2)
EPS = 1e-9


def load_corpus():
    lines = json.loads(LINES_PATH.read_text())
    freq = Counter(g for line in lines for g in line["signs"] if g)
    records = json.loads(GLYPHS_PATH.read_text())
    mapping = {}
    for record in records:
        cps = [int(x, 16) for x in re.findall(
            r"&#x([0-9A-Fa-f]+);", record.get("unicode", ""))]
        mapping[int(record["glyph_id"])] = cps
    return lines, freq, mapping


def crop_ink(mask):
    ys, xs = np.nonzero(mask)
    if not len(xs):
        return None
    return mask[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def resize_binary(mask, size):
    im = Image.fromarray(mask.astype(np.uint8) * 255, "L")
    im = im.resize((max(1, int(size[0])), max(1, int(size[1]))),
                   Image.Resampling.LANCZOS)
    return np.asarray(im) >= 96


def centre(mask, canvas=CANVAS):
    out = np.zeros((canvas, canvas), dtype=bool)
    h, w = mask.shape
    if h > canvas or w > canvas:
        raise ValueError("mask does not fit canvas")
    y = (canvas - h) // 2
    x = (canvas - w) // 2
    out[y:y + h, x:x + w] = mask
    return out


def normalize(mask, preserve_aspect):
    crop = crop_ink(mask)
    if crop is None:
        return None
    h, w = crop.shape
    if preserve_aspect:
        scale = INNER / max(h, w)
        nh, nw = max(1, round(h * scale)), max(1, round(w * scale))
    else:
        nh = nw = INNER
    return centre(resize_binary(crop, (nw, nh)))


def render_all(force=False):
    lines, freq, mapping = load_corpus()
    if RASTER_CACHE.exists() and not force:
        z = np.load(RASTER_CACHE, allow_pickle=False)
        ids = z["ids"].astype(int)
        return {
            "ids": ids,
            "aspect": z["aspect"].astype(bool),
            "stretched": z["stretched"].astype(bool),
            "raw_aspect": z["raw_aspect"],
            "descriptors": json.loads(str(z["descriptors_json"])),
            "excluded": json.loads(str(z["excluded_json"])),
            "freq": freq,
            "lines": lines,
        }

    tt = TTFont(FONT_PATH)
    cmap = tt.getBestCmap()
    pilfont = ImageFont.truetype(str(FONT_PATH), RENDER_SIZE)
    ids, aspect, stretched, raw_aspects, descriptors = [], [], [], [], []
    excluded = []
    for gid in sorted(freq):
        cps = mapping.get(gid, [])
        reason = None
        if not cps:
            reason = "no codepoint mapping"
        elif any(cp not in cmap or cmap.get(cp) == ".notdef" for cp in cps):
            reason = "codepoint absent from cmap/.notdef"
        if reason:
            excluded.append({"id": gid, "tokens": freq[gid], "reason": reason})
            continue
        text = "".join(chr(cp) for cp in cps)
        # Pillow's bbox includes negative bearings.  Drawing at margin-bbox
        # makes the result independent of those bearings and avoids clipping.
        bbox = pilfont.getbbox(text)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        if w <= 0 or h <= 0:
            excluded.append({"id": gid, "tokens": freq[gid],
                             "reason": "empty font bounding box"})
            continue
        margin = 24
        im = Image.new("L", (w + 2 * margin, h + 2 * margin), 0)
        draw = ImageDraw.Draw(im)
        draw.text((margin - bbox[0], margin - bbox[1]), text,
                  fill=255, font=pilfont)
        raw = np.asarray(im) >= 96
        crop = crop_ink(raw)
        if crop is None or crop.sum() < 4:
            excluded.append({"id": gid, "tokens": freq[gid],
                             "reason": "blank or negligible rendered ink"})
            continue
        a = normalize(crop, True)
        s = normalize(crop, False)
        if a is None or s is None:
            excluded.append({"id": gid, "tokens": freq[gid],
                             "reason": "blank after normalization"})
            continue
        comp = int(ndimage.label(crop, structure=np.ones((3, 3)))[1])
        padded = np.pad(crop, 1, constant_values=False)
        bg, nbg = ndimage.label(~padded, structure=np.ones((3, 3)))
        border = set(np.unique(np.r_[bg[0], bg[-1], bg[:, 0], bg[:, -1]]))
        holes = sum(label not in border for label in range(1, nbg + 1))
        ch, cw = crop.shape
        desc = {
            "id": gid,
            "tokens": freq[gid],
            "raw_width": int(cw),
            "raw_height": int(ch),
            "aspect": float(cw / ch),
            "ink_fraction": float(crop.mean()),
            "components": comp,
            "holes": int(holes),
            "euler": int(comp - holes),
            "extent": float(crop.sum() / (cw * ch)),
            "codepoints": [f"U+{cp:04X}" for cp in cps],
        }
        ids.append(gid)
        aspect.append(a)
        stretched.append(s)
        raw_aspects.append(cw / ch)
        descriptors.append(desc)

    payload = {
        "ids": np.asarray(ids, dtype=np.int16),
        "aspect": np.asarray(aspect, dtype=np.uint8),
        "stretched": np.asarray(stretched, dtype=np.uint8),
        "raw_aspect": np.asarray(raw_aspects, dtype=np.float32),
        "descriptors_json": np.asarray(json.dumps(descriptors)),
        "excluded_json": np.asarray(json.dumps(excluded)),
    }
    np.savez_compressed(RASTER_CACHE, **payload)
    return {**payload, "aspect": payload["aspect"].astype(bool),
            "stretched": payload["stretched"].astype(bool),
            "descriptors": descriptors, "excluded": excluded,
            "freq": freq, "lines": lines}


def transform(mask, scale, dy, dx):
    crop = crop_ink(mask)
    if crop is None:
        return np.zeros_like(mask)
    h, w = crop.shape
    resized = resize_binary(crop, (round(w * scale), round(h * scale)))
    base = centre(resized) if max(resized.shape) <= CANVAS else centre(
        resize_binary(resized, (min(CANVAS, resized.shape[1]),
                                min(CANVAS, resized.shape[0]))))
    out = np.zeros_like(base)
    sy0, sy1 = max(0, -dy), min(CANVAS, CANVAS - dy)
    sx0, sx1 = max(0, -dx), min(CANVAS, CANVAS - dx)
    out[sy0 + dy:sy1 + dy, sx0 + dx:sx1 + dx] = base[sy0:sy1, sx0:sx1]
    return out


def aligned_overlap_matrix(masks):
    """Best directed alignment, later symmetrised between i->j and j->i."""
    n = len(masks)
    x = masks.reshape(n, -1).astype(np.float32)
    ink = x.sum(1)
    best = np.full((n, n), -1.0, dtype=np.float32)
    best_inter = np.zeros((n, n), dtype=np.float32)
    best_other_ink = np.zeros((n, n), dtype=np.float32)
    best_code = np.zeros((n, n), dtype=np.int16)
    codes = []
    code = 0
    for scale in SCALES:
        for dy in SHIFTS:
            for dx in SHIFTS:
                v = np.asarray([transform(m, scale, dy, dx) for m in masks])
                vf = v.reshape(n, -1).astype(np.float32)
                vink = vf.sum(1)
                inter = x @ vf.T
                dice = (2 * inter) / (ink[:, None] + vink[None, :] + EPS)
                take = dice > best
                best[take] = dice[take]
                best_inter[take] = inter[take]
                oi = np.broadcast_to(vink[None, :], (n, n))
                best_other_ink[take] = oi[take]
                best_code[take] = code
                codes.append((scale, dy, dx))
                code += 1

    # For an unordered pair, allow either glyph to be the transformed one.
    reverse_better = best.T > best
    dice = np.where(reverse_better, best.T, best)
    inter = np.where(reverse_better, best_inter.T, best_inter)
    # Directional containment is always row-in-column after correcting which
    # member was transformed.
    row_denom = np.where(reverse_better, best_other_ink.T, ink[:, None])
    col_denom = np.where(reverse_better, ink[None, :], best_other_ink)
    contain = inter / (row_denom + EPS)
    contain_reverse = inter / (col_denom + EPS)
    chosen_code = np.where(reverse_better, -best_code.T - 1, best_code)
    np.fill_diagonal(dice, 1.0)
    np.fill_diagonal(contain, 1.0)
    np.fill_diagonal(contain_reverse, 1.0)
    return dice, contain, contain_reverse, chosen_code, codes


def chamfer_matrix(masks):
    """Centred symmetric chamfer; distance transforms tolerate small offsets."""
    n = len(masks)
    x = masks.reshape(n, -1).astype(np.float32)
    ink = x.sum(1)
    dt = np.asarray([ndimage.distance_transform_edt(~m) for m in masks],
                    dtype=np.float32).reshape(n, -1)
    directed = (x @ dt.T) / (ink[:, None] + EPS)
    sym = (directed + directed.T) / (2 * math.hypot(CANVAS, CANVAS))
    np.fill_diagonal(sym, 0.0)
    return sym.astype(np.float32)


def pairwise(rasters, force=False):
    ids = rasters["ids"]
    if PAIR_CACHE.exists() and not force:
        z = np.load(PAIR_CACHE, allow_pickle=False)
        if np.array_equal(z["ids"], ids):
            return {k: z[k] for k in z.files}
    out = {"ids": ids}
    codes = None
    for name in ("aspect", "stretched"):
        dice, c1, c2, code, these_codes = aligned_overlap_matrix(rasters[name])
        out[f"{name}_dice"] = dice
        out[f"{name}_contain"] = c1
        out[f"{name}_contain_reverse"] = c2
        out[f"{name}_alignment"] = code
        out[f"{name}_chamfer"] = chamfer_matrix(rasters[name])
        codes = these_codes
    out["alignment_codes"] = np.asarray(codes, dtype=np.float32)
    np.savez_compressed(PAIR_CACHE, **out)
    return out


def mixture_cut(values, high_is_match=False):
    """Intersection of a two-Gaussian fit; BIC records whether it earned use."""
    values = np.asarray(values, dtype=float)
    finite = values[np.isfinite(values)].reshape(-1, 1)
    one = GaussianMixture(1, random_state=1379, n_init=5).fit(finite)
    two = GaussianMixture(2, random_state=1379, n_init=10).fit(finite)
    means = two.means_.ravel()
    order = np.argsort(means)
    means, weights = means[order], two.weights_.ravel()[order]
    variances = two.covariances_.reshape(-1)[order]
    # Solve equality of weighted normal densities.  Pick a root between means,
    # or the density-minimum grid point there if numerical roots are awkward.
    lo, hi = means
    grid = np.linspace(lo, hi, 2001)
    dens = []
    for m, v, w in zip(means, variances, weights):
        dens.append(w / math.sqrt(2 * math.pi * v) *
                    np.exp(-0.5 * (grid - m) ** 2 / v))
    idx = int(np.argmin(np.abs(dens[0] - dens[1])))
    cut = float(grid[idx])
    return cut, {
        "method": "two-Gaussian intersection on nearest-neighbour scores",
        "one_component_bic": float(one.bic(finite)),
        "two_component_bic": float(two.bic(finite)),
        "two_component_preferred": bool(two.bic(finite) < one.bic(finite)),
        "component_means": [float(x) for x in means],
        "component_weights": [float(x) for x in weights],
        "component_standard_deviations": [float(math.sqrt(x)) for x in variances],
        "cut": cut,
        "match_side": "above" if high_is_match else "below",
    }


def groups_from_labels(ids, labels):
    out = defaultdict(list)
    for gid, label in zip(ids, labels):
        out[int(label)].append(int(gid))
    return [sorted(v) for v in out.values() if len(v) > 1]


def score_pair(i, j, pair):
    return {
        "dice_aspect": float(pair["aspect_dice"][i, j]),
        "dice_stretched": float(pair["stretched_dice"][i, j]),
        "contain_i_in_j": float(pair["aspect_contain"][i, j]),
        "contain_j_in_i": float(pair["aspect_contain_reverse"][i, j]),
        "chamfer_aspect": float(pair["aspect_chamfer"][i, j]),
        "chamfer_stretched": float(pair["stretched_chamfer"][i, j]),
    }


def allograph_groups(rasters, pair):
    ids = rasters["ids"]
    distance = 1.0 - pair["aspect_dice"]
    np.fill_diagonal(distance, 0)
    nn = np.partition(distance + np.eye(len(ids)) * 10, 0, axis=1)[:, 0]
    cut, criterion = mixture_cut(nn)
    # Complete linkage makes every pair in a proposed equivalence class clear
    # the same image-based threshold; it prevents single-link chains.
    z = linkage(squareform(distance, checks=False), method="complete")
    labels = fcluster(z, t=cut, criterion="distance")
    raw_groups = groups_from_labels(ids, labels)
    index = {int(g): i for i, g in enumerate(ids)}
    desc = {d["id"]: d for d in rasters["descriptors"]}
    groups = []
    for members in raw_groups:
        pairs = []
        for a_pos, a in enumerate(members):
            for b in members[a_pos + 1:]:
                pairs.append(score_pair(index[a], index[b], pair))
        groups.append({
            "members": members,
            "tokens": [int(rasters["freq"][g]) for g in members],
            "min_dice_aspect": min(x["dice_aspect"] for x in pairs),
            "min_dice_stretched": min(x["dice_stretched"] for x in pairs),
            "max_chamfer_aspect": max(x["chamfer_aspect"] for x in pairs),
            "structural_counts": [
                {k: desc[g][k] for k in ("components", "holes", "euler")}
                for g in members],
        })
    groups.sort(key=lambda x: (-len(x["members"]), x["members"]))
    criterion["nearest_neighbour_quantiles"] = {
        str(q): float(np.quantile(nn, q)) for q in (0, .1, .25, .5, .75, .9, 1)
    }
    criterion["linkage"] = "complete"
    return groups, criterion, distance


def directed_containment(pair):
    # The two stored matrices describe row-in-column and column-in-row under
    # the best unordered alignment.
    return pair["aspect_contain"], pair["aspect_contain_reverse"]


def derivational_groups(rasters, pair, allographs):
    ids = rasters["ids"]
    n = len(ids)
    c_ab, c_ba = directed_containment(pair)
    high = np.maximum(c_ab, c_ba)
    asym = np.abs(c_ab - c_ba)
    np.fill_diagonal(high, 0)
    np.fill_diagonal(asym, 0)
    # Fit the upper-containment cut on every sign's best *non-allograph*
    # neighbour.  This targets base-plus-extra-ink relations, not duplicates.
    allo_pairs = set()
    for group in allographs:
        m = group["members"]
        allo_pairs |= {tuple(sorted((a, b))) for p, a in enumerate(m) for b in m[p + 1:]}
    idx = {int(g): i for i, g in enumerate(ids)}
    allowed = high.copy()
    for a, b in allo_pairs:
        allowed[idx[a], idx[b]] = allowed[idx[b], idx[a]] = 0
    nearest = allowed.max(axis=1)
    contain_cut, contain_criterion = mixture_cut(nearest, high_is_match=True)
    # An actual modifier must leave appreciable residual in just one direction.
    # A second mixture determines what counts as appreciable among high-tail
    # containment pairs.
    tri = np.triu_indices(n, 1)
    is_allo = np.asarray([
        tuple(sorted((int(ids[i]), int(ids[j])))) in allo_pairs
        for i, j in zip(*tri)
    ], dtype=bool)
    tail = (high[tri] >= contain_cut) & ~is_allo
    tail_asym = asym[tri][tail]
    # Once exact/near-exact allographs are removed, any visible one-way
    # residual is relevant.  The allograph distance cut is the empirical lower
    # bound separating zero residual from nonzero residual.
    allo_asym = [asym[idx[a], idx[b]] for a, b in allo_pairs]
    max_allo_asym = float(max(allo_asym)) if allo_asym else 0.0
    min_tail_asym = float(tail_asym.min()) if len(tail_asym) else 1.0
    asym_cut = (max_allo_asym + min_tail_asym) / 2
    asym_criterion = {
        "method": "allograph/non-allograph separation",
        "cut": asym_cut,
        "maximum_allograph_asymmetry": max_allo_asym,
        "minimum_high-containment_nonallograph_asymmetry": min_tail_asym,
        "nonallograph_tail_quantiles": {
            str(q): float(np.quantile(tail_asym, q))
            for q in (0, .1, .25, .5, .75, .9, 1)
        } if len(tail_asym) else {},
    }
    # A tiny primitive (especially a single stroke) is contained in scores of
    # unrelated glyphs.  Fit a separate cut to the fraction of the larger sign
    # explained by the proposed base, among high-containment non-allographs.
    tail_coverage = np.minimum(c_ab, c_ba)[tri][tail]
    if len(tail_coverage) >= 10 and np.ptp(tail_coverage) > 1e-6:
        intersection, coverage_criterion = mixture_cut(tail_coverage,
                                                       high_is_match=True)
        # The intersection admits the low-coverage component's upper tail,
        # which is dominated by generic primitives (one stroke inside almost
        # anything).  Use the centre of the high-coverage component as the
        # conservative common-core criterion.
        coverage_cut = coverage_criterion["component_means"][-1]
        coverage_criterion["density_intersection"] = intersection
        coverage_criterion["cut"] = coverage_cut
        coverage_criterion["selection"] = (
            "mean of high-coverage component; excludes generic sub-strokes")
    else:
        coverage_cut = float(np.median(tail_coverage)) if len(tail_coverage) else 1.0
        coverage_criterion = {"method": "median fallback", "cut": coverage_cut}

    edge = ((high >= contain_cut) & (asym >= asym_cut) &
            (np.minimum(c_ab, c_ba) >= coverage_cut))
    np.fill_diagonal(edge, False)
    # Single linkage is deliberate: variants can share a base while differing
    # substantially from one another.  The base-to-member check below removes
    # chains that lack a common contained drawing.
    graph_distance = np.where(edge, 1.0 - high, 1.0)
    np.fill_diagonal(graph_distance, 0)
    z = linkage(squareform(graph_distance, checks=False), method="single")
    labels = fcluster(z, t=1.0 - contain_cut, criterion="distance")
    candidates = groups_from_labels(ids, labels)
    result = []
    desc = {d["id"]: d for d in rasters["descriptors"]}
    for candidate in candidates:
        # Only retain asymmetric edges inside the linkage component.
        candidate = [g for g in candidate if any(
            edge[idx[g], idx[h]] for h in candidate if h != g)]
        if len(candidate) < 2:
            continue
        best_base, best_members, best_quality = None, [], -1.0
        for base in candidate:
            bi = idx[base]
            members = []
            qualities = []
            for member in candidate:
                if member == base:
                    continue
                mi = idx[member]
                base_in_member = c_ab[bi, mi]
                member_in_base = c_ba[bi, mi]
                if (base_in_member >= contain_cut and
                        base_in_member - member_in_base >= asym_cut and
                        member_in_base >= coverage_cut):
                    members.append(member)
                    qualities.append(base_in_member - member_in_base)
            quality = len(members) + (np.mean(qualities) if qualities else 0)
            if quality > best_quality:
                best_base, best_members, best_quality = base, members, quality
        if not best_members:
            continue
        rec_members = []
        for member in sorted(best_members):
            bi, mi = idx[best_base], idx[member]
            rec_members.append({
                "id": member,
                "tokens": int(rasters["freq"][member]),
                "base_in_member": float(c_ab[bi, mi]),
                "member_in_base": float(c_ba[bi, mi]),
                "dice_aspect": float(pair["aspect_dice"][bi, mi]),
                "dice_stretched": float(pair["stretched_dice"][bi, mi]),
                "chamfer_aspect": float(pair["aspect_chamfer"][bi, mi]),
            })
        result.append({
            "base": int(best_base),
            "base_tokens": int(rasters["freq"][best_base]),
            "members": rec_members,
            "base_structure": {k: desc[best_base][k]
                               for k in ("components", "holes", "euler")},
        })
    # A sign should not be claimed in multiple families.  Prefer more members,
    # then the better mean containment.
    result.sort(key=lambda r: (-len(r["members"]),
                               -np.mean([m["base_in_member"] for m in r["members"]]),
                               r["base"]))
    used, disjoint = set(), []
    for family in result:
        members = {family["base"]} | {m["id"] for m in family["members"]}
        if members & used:
            continue
        used |= members
        disjoint.append(family)
    contain_criterion["nearest_neighbour_quantiles"] = {
        str(q): float(np.quantile(nearest, q)) for q in (0, .1, .25, .5, .75, .9, 1)
    }
    contain_criterion["linkage"] = "single, followed by common-base check"
    return disjoint, {"containment": contain_criterion,
                      "asymmetry": asym_criterion,
                      "larger_sign_coverage": coverage_criterion}


def best_alignment(base, member):
    """Place base on member, maximizing Dice; used to extract added ink."""
    best = (-1, None, None)
    # A slightly wider local search is affordable for the selected relations.
    for scale in np.arange(.80, 1.201, .05):
        for dy in range(-6, 7):
            for dx in range(-6, 7):
                moved = transform(base, float(scale), dy, dx)
                inter = np.logical_and(moved, member).sum()
                dice = 2 * inter / (moved.sum() + member.sum() + EPS)
                if dice > best[0]:
                    best = (dice, moved, (float(scale), dy, dx))
    return best


def residuals_and_modifiers(rasters, families):
    idx = {int(g): i for i, g in enumerate(rasters["ids"])}
    residuals, owners = [], []
    for fi, family in enumerate(families):
        base_mask = rasters["aspect"][idx[family["base"]]]
        for member in family["members"]:
            member_mask = rasters["aspect"][idx[member["id"]]]
            dice, aligned_base, params = best_alignment(base_mask, member_mask)
            # One-pixel dilation removes antialias/registration fringes.  What
            # remains is the conservative added-ink image.
            covered = ndimage.binary_dilation(aligned_base, iterations=1)
            residual = member_mask & ~covered
            rcrop = crop_ink(residual)
            if rcrop is None:
                norm = np.zeros((CANVAS, CANVAS), bool)
                components = 0
                bbox = None
            else:
                norm = normalize(rcrop, True)
                components = int(ndimage.label(rcrop, np.ones((3, 3)))[1])
                yy, xx = np.nonzero(residual)
                bbox = [int(xx.min()), int(yy.min()), int(xx.max() + 1), int(yy.max() + 1)]
            ri = len(residuals)
            residuals.append(norm)
            owners.append((fi, member["id"]))
            member.update({
                "residual_index": ri,
                "residual_pixels": int(residual.sum()),
                "residual_components": components,
                "residual_bbox_xyxy": bbox,
                "residual_alignment": {"scale": params[0], "dy": params[1],
                                       "dx": params[2], "dice": float(dice)},
            })
    if not residuals:
        np.savez_compressed(RESIDUAL_CACHE, masks=np.empty((0, CANVAS, CANVAS)),
                            owners=np.empty((0, 2), int))
        return [], []
    residuals = np.asarray(residuals, dtype=bool)
    np.savez_compressed(RESIDUAL_CACHE, masks=residuals.astype(np.uint8),
                        owners=np.asarray(owners, dtype=int))
    valid = np.asarray([m.sum() >= 4 for m in residuals])
    modifier_groups = []
    if valid.sum() >= 3:
        rm = residuals[valid]
        dice, _, _, _, _ = aligned_overlap_matrix(rm)
        distance = 1 - dice
        nn = np.partition(distance + np.eye(len(rm)) * 10, 0, axis=1)[:, 0]
        cut, criterion = mixture_cut(nn)
        z = linkage(squareform(distance, checks=False), method="complete")
        labels = fcluster(z, t=cut, criterion="distance")
        valid_idx = np.flatnonzero(valid)
        for group in groups_from_labels(valid_idx, labels):
            records = []
            bases = set()
            for residual_index in group:
                fi, member = owners[residual_index]
                base = families[fi]["base"]
                bases.add(base)
                records.append({"base": base, "member": member,
                                "residual_index": int(residual_index)})
            if len(bases) >= 2:
                modifier_groups.append({"instances": records,
                                        "distinct_bases": len(bases)})
        modifier_groups.sort(key=lambda x: (-len(x["instances"]),
                                            x["instances"][0]["base"]))
    else:
        criterion = {"method": "too few nonblank residuals"}
    return modifier_groups, criterion


def render_contact_sheet(rasters, allographs, families):
    idx = {int(g): i for i, g in enumerate(rasters["ids"])}
    rows = []
    for g in allographs:
        rows.append(("A", g["members"], None))
    for f in families:
        rows.append(("B", [f["base"]] + [m["id"] for m in f["members"]], f["base"]))
    rows.sort(key=lambda r: (r[0], -len(r[1]), r[1][0]))
    if not rows:
        return
    panel_cols = 3
    panel_rows = math.ceil(len(rows) / panel_cols)
    fig, axes = plt.subplots(panel_rows, panel_cols,
                             figsize=(18, max(4, panel_rows * 1.3)),
                             squeeze=False)
    for ax in axes.ravel(): ax.axis("off")
    for ax, (kind, members, base) in zip(axes.ravel(), rows):
        gap, top = 4, 19
        width = len(members) * (CANVAS + gap) - gap
        mosaic = np.zeros((CANVAS + top, width), dtype=bool)
        for x, gid in enumerate(members):
            x0 = x * (CANVAS + gap)
            mosaic[top:, x0:x0 + CANVAS] = rasters["aspect"][idx[gid]]
            suffix = "*" if gid == base else ""
            ax.text(x0 + CANVAS / 2, 8, f"{gid}{suffix}  n={rasters['freq'][gid]}",
                    ha="center", va="center", fontsize=6.5)
        ax.imshow(mosaic, cmap="gray_r", vmin=0, vmax=1, interpolation="nearest")
        ax.set_title(f"{kind}  ({len(members)} signs)" +
                     ("  * = base" if kind == "B" else ""), fontsize=8, loc="left")
        ax.axis("off")
    fig.suptitle("Shape groups: A = allographs; B = base + added ink", fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, .982))
    fig.savefig(SHEET_PATH, dpi=180, bbox_inches="tight")
    plt.close(fig)


def render_residual_sheet(families):
    if not RESIDUAL_CACHE.exists():
        return
    z = np.load(RESIDUAL_CACHE)
    masks, owners = z["masks"].astype(bool), z["owners"]
    if not len(masks):
        return
    cols = 8
    rows = math.ceil(len(masks) / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 1.25, rows * 1.25),
                             squeeze=False)
    for ax in axes.ravel(): ax.axis("off")
    for i, (mask, (fi, member)) in enumerate(zip(masks, owners)):
        base = families[int(fi)]["base"]
        ax = axes.ravel()[i]
        ax.imshow(mask, cmap="gray_r", vmin=0, vmax=1)
        ax.set_title(f"{base}→{int(member)}", fontsize=8)
    fig.suptitle("Conservative residual ink (member minus dilated aligned base)")
    fig.tight_layout(rect=(0, 0, 1, .98))
    fig.savefig(RESIDUAL_SHEET_PATH, dpi=180, bbox_inches="tight")
    plt.close(fig)


def inventory_counts(freq, excluded, allographs, families, modifier_groups):
    ids = set(freq)
    parent = {g: g for g in ids}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(a, b):
        a, b = find(a), find(b)
        if a != b: parent[b] = a
    for group in allographs:
        for g in group["members"][1:]: union(group["members"][0], g)
    after_a = len({find(g) for g in ids})
    for family in families:
        for m in family["members"]: union(family["base"], m["id"])
    after_ab = len({find(g) for g in ids})
    residual_n = sum(len(f["members"]) for f in families)
    reusable_instances = sum(len(g["instances"]) for g in modifier_groups)
    modifier_types = residual_n - reusable_instances + len(modifier_groups)
    return {
        "attested_ids": len(ids),
        "renderable_ids": len(ids) - len(excluded),
        "excluded_ids": len(excluded),
        "after_allograph_merges": after_a,
        "allograph_reduction": len(ids) - after_a,
        "after_collapsing_derivational_families": after_ab,
        "allograph_plus_family_reduction": len(ids) - after_ab,
        "residual_modifier_instances": residual_n,
        "estimated_modifier_types": modifier_types,
        "factored_primitives_including_modifiers": after_ab + modifier_types,
    }


def build(force=False):
    rasters = render_all(force)
    pair = pairwise(rasters, force)
    allographs, allo_criterion, _ = allograph_groups(rasters, pair)
    families, deriv_criterion = derivational_groups(rasters, pair, allographs)
    modifier_groups, modifier_criterion = residuals_and_modifiers(rasters, families)
    render_contact_sheet(rasters, allographs, families)
    render_residual_sheet(families)
    inventory = inventory_counts(rasters["freq"], rasters["excluded"],
                                 allographs, families, modifier_groups)
    output = {
        "method": {
            "font": str(FONT_PATH.relative_to(ROOT)),
            "render_size_px": RENDER_SIZE,
            "binary_threshold": 96,
            "canvas_px": CANVAS,
            "normalized_ink_box_px": INNER,
            "normalizations": {
                "aspect": "crop ink; scale longer side to 52 px; preserve aspect; centre",
                "stretched": "crop ink; independently scale width and height to 52 px; centre",
            },
            "alignment_search": {
                "scale": list(SCALES), "dx_px": list(SHIFTS), "dy_px": list(SHIFTS),
                "selection": "maximum Dice, allowing either member to be transformed",
            },
            "chamfer": "symmetric mean distance-to-opposite-ink on centred normalized masks, divided by canvas diagonal",
            "allograph_cut": allo_criterion,
            "derivational_cut": deriv_criterion,
            "residual_cut": modifier_criterion,
        },
        "inventory": inventory,
        "excluded": rasters["excluded"],
        "descriptors": rasters["descriptors"],
        "allograph_sets": allographs,
        "derivational_families": families,
        "recurrent_modifiers": modifier_groups,
        "artifacts": {
            "rasters": str(RASTER_CACHE.relative_to(ROOT)),
            "pairwise_scores": str(PAIR_CACHE.relative_to(ROOT)),
            "residual_rasters": str(RESIDUAL_CACHE.relative_to(ROOT)),
            "contact_sheet": str(SHEET_PATH.relative_to(ROOT)),
            "residual_sheet": str(RESIDUAL_SHEET_PATH.relative_to(ROOT)),
        },
    }
    OUT_PATH.write_text(json.dumps(output, indent=2) + "\n")
    return output


def print_summary(out):
    inv = out["inventory"]
    print("=== shape analysis ===")
    print(f"attested ids             : {inv['attested_ids']}")
    print(f"renderable / excluded    : {inv['renderable_ids']} / {inv['excluded_ids']}")
    print(f"allograph sets           : {len(out['allograph_sets'])}")
    print(f"allograph merges         : {inv['allograph_reduction']}")
    print(f"derivational families    : {len(out['derivational_families'])}")
    print(f"recurrent modifier types : {len(out['recurrent_modifiers'])}")
    print(f"inventory before / A / A+B: {inv['attested_ids']} / "
          f"{inv['after_allograph_merges']} / "
          f"{inv['after_collapsing_derivational_families']}")
    print("wrote:")
    for path in (OUT_PATH, RASTER_CACHE, PAIR_CACHE, RESIDUAL_CACHE,
                 SHEET_PATH, RESIDUAL_SHEET_PATH):
        print(f"  {path.relative_to(ROOT)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="rebuild caches")
    args = parser.parse_args()
    print_summary(build(args.force))
