"""Unit `labs-figures-tidy`: give the interactive figures in Labs 1-4 (Levels 0-2) a clean layout.  Run from book/.

Each figure is laid out with qcai.viz.frame, which places the title, menu, legend, subplot
titles and slider in separate bands and adds a stacked layout for phones.  Figure cells are
found by a marker line they contain, so the script can be re-run safely.
"""
import json
import pathlib
import re

BOOK = pathlib.Path(__file__).resolve().parents[1]

CELLS = {}

CELLS[("01-chance", "checkpoints = [10, 20, 50")] = '''checkpoints = [10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000]
fig = go.Figure()
cut0 = int(np.searchsorted(grid, checkpoints[0], side="right"))
for k in range(len(seeds)):
    fig.add_trace(go.Scatter(x=grid.tolist(), y=paths[k, :cut0].round(4).tolist(), mode="lines",
                             line=dict(width=1, color="rgba(52,101,164,0.35)"),
                             name="one seeded run", legendgroup="runs", showlegend=(k == 0),
                             hoverinfo="skip"))
fig.add_trace(go.Scatter(x=grid.tolist(), y=(P + half).clip(0, 1).round(4).tolist(), mode="lines",
                         line=dict(width=0), showlegend=False, hoverinfo="skip"))
fig.add_trace(go.Scatter(x=grid.tolist(), y=(P - half).clip(0, 1).round(4).tolist(), mode="lines",
                         line=dict(width=0), fill="tonexty", fillcolor="rgba(230,126,34,0.25)",
                         name="p ± 1.96·√(p(1−p)/n)",
                         hovertemplate="n=%{x}<br>lower edge %{y:.3f}<extra></extra>"))
fig.add_trace(go.Scatter(x=[1, 10000], y=[P, P], mode="lines", line=dict(color="black", dash="dash"),
                         name="model probability p = 0.5"))

steps = []
for m in checkpoints:
    cut = int(np.searchsorted(grid, m, side="right"))
    steps.append(dict(method="restyle", label=f"{m:,}",
                      args=[{"y": [paths[k, :cut].round(4).tolist() for k in range(len(seeds))]},
                            list(range(len(seeds)))]))
fig.update_layout(template="plotly_white",
                  title="Running frequency of heads in 40 seeded runs",
                  xaxis=dict(title="number of flips n (log scale)", type="log", range=[0, 4]),
                  yaxis=dict(title="relative frequency of heads", range=[0, 1]),
                  sliders=[dict(active=0, steps=steps, currentvalue=dict(prefix="flips shown: "))])
show(frame(fig, height=500))'''

CELLS[("01-chance", "Share with the hidden trait")] = '''fig = make_subplots(rows=1, cols=2, horizontal_spacing=0.16,
                    subplot_titles=("Share with the hidden trait", "Difference in outcome rate"))
r = res[0.0]
fig.add_trace(go.Bar(x=["treated", "untreated"], y=[r["share_t"], r["share_c"]],
                     marker_color=["#3465a4", "#babdb6"], name="trait share",
                     texttemplate="%{y:.2f}", textposition="outside", cliponaxis=False,
                     hovertemplate="%{x}: %{y:.3f}<extra></extra>"), 1, 1)
fig.add_trace(go.Bar(x=["simulated<br>estimate", "population<br>contrast", "true<br>effect"],
                     y=[r["estimate"], r["theory"], TRUE_EFFECT],
                     marker_color=["#e67e22", "#f5b041", "#2e7d32"], name="contrast",
                     texttemplate="%{y:.3f}", textposition="outside", cliponaxis=False,
                     hovertemplate="%{x}: %{y:.3f}<extra></extra>"), 1, 2)
steps = []
for st in strengths:
    r = res[st]
    steps.append(dict(method="restyle", label=f"{st:.2f}",
                      args=[{"y": [[r["share_t"], r["share_c"]],
                                   [r["estimate"], r["theory"], TRUE_EFFECT]]}, [0, 1]]))
fig.update_yaxes(range=[0, 1], title="share of the group", row=1, col=1)
fig.update_yaxes(range=[-0.05, 0.5], title="treated − untreated", row=1, col=2)
fig.update_xaxes(tickangle=0)
fig.update_layout(template="plotly_white", showlegend=False,
                  sliders=[dict(active=0, steps=steps, currentvalue=dict(prefix="self-selection strength: "))])
show(frame(fig, height=460, xticks_lines=2, stack=True))'''

CELLS[("02-bayes", "def colorscale(cnt)")] = '''COL = {"tp": "#c0392b", "fn": "#f1948a", "fp": "#e67e22", "tn": "#d5d8dc"}
NAMES = {"tp": "has condition, positive", "fn": "has condition, negative",
         "fp": "no condition, positive (false alarm)", "tn": "no condition, negative"}
PRIORS = [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5]
TESTS = [(sens, fp) for sens in (0.80, 0.90, 0.99) for fp in (0.01, 0.05, 0.10)]

def colorscale(cnt):
    # z holds the person index 0..9999; people are ordered tp, fn, fp, tn, so a stepped
    # colorscale with breaks at the cumulative counts colours each group.
    edges = np.cumsum([cnt["tp"], cnt["fn"], cnt["fp"]])
    out, lo = [], 0.0
    for key, edge in zip(("tp", "fn", "fp", "tn"), list(edges) + [N]):
        hi = 1.0 if key == "tn" else min(1.0, max(0.0, (edge - 0.5) / (N - 1)))
        out += [[lo, COL[key]], [hi, COL[key]]]
        lo = hi
    return out

def title(prior, sens, fp):
    cnt = natural_frequencies(prior, sens, fp)
    post = s.bayes(prior, sens, fp)["posterior"]
    return (f"prior {prior:g}, sensitivity {sens:g}, false-positive rate {fp:g}<br>"
            f"{cnt['tp']} true positives and {cnt['fp']} false positives<br>"
            f"P(condition | positive) = {post:.3f}")

def prior_steps(sens, fp):
    return [dict(method="update", label=f"{p:g}",
                 args=[{"colorscale": [colorscale(natural_frequencies(p, sens, fp))]},
                       {"title.text": title(p, sens, fp)}]) for p in PRIORS]

start = PRIORS.index(PRIOR)
z = np.arange(N).reshape(100, 100).tolist()
fig = go.Figure(go.Heatmap(z=z, colorscale=colorscale(c), zmin=0, zmax=N - 1, showscale=False,
                           xgap=0.6, ygap=0.6, hovertemplate="person %{z}<extra></extra>"))
for key in ("tp", "fn", "fp", "tn"):                       # legend entries only
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", name=NAMES[key],
                             marker=dict(symbol="square", size=12, color=COL[key])))
buttons = [dict(method="update", label=f"sensitivity {sn:g}, false-positive {f:g}",
                args=[{"colorscale": [colorscale(natural_frequencies(PRIOR, sn, f))]},
                      {"sliders[0].steps": prior_steps(sn, f), "sliders[0].active": start,
                       "title.text": title(PRIOR, sn, f)}])
           for sn, f in TESTS]
fig.update_layout(template="plotly_white", title=title(PRIOR, SENS, FP),
                  xaxis=dict(visible=False, constrain="domain"),
                  yaxis=dict(visible=False, autorange="reversed", scaleanchor="x", constrain="domain"),
                  sliders=[dict(active=start, steps=prior_steps(SENS, FP),
                                currentvalue=dict(prefix="prior (base rate): "))],
                  updatemenus=[dict(type="dropdown", buttons=buttons, active=TESTS.index((SENS, FP)))])
show(frame(fig, height=720, xticks_lines=0, narrow_plot=340, axes=False))'''

CELLS[("02-bayes", "def sankey_args(prior)")] = '''def sankey_args(prior):
    cnt = natural_frequencies(prior, SENS, FP)
    vals = [cnt["sick"], cnt["healthy"], cnt["tp"], cnt["fn"], cnt["fp"], cnt["tn"]]
    labels = ["10,000<br>people", f"condition<br>{cnt['sick']:,}", f"no condition<br>{cnt['healthy']:,}",
              f"positive<br>{cnt['tp'] + cnt['fp']:,}", f"negative<br>{cnt['fn'] + cnt['tn']:,}"]
    # node centres (0 = top): the condition and positive groups stay on top at every prior
    f, gap = 0.93, 0.07
    sick, pos = cnt["sick"] / N * f, (cnt["tp"] + cnt["fp"]) / N * f
    ys = [0.5, max(sick / 2, 0.045), sick + gap + (f - sick) / 2, max(pos / 2, 0.045), pos + gap + (f - pos) / 2]
    return vals, labels, ys

vals, labels, ys = sankey_args(PRIOR)
link_colors = ["rgba(192,57,43,0.5)", "rgba(127,140,141,0.4)", "rgba(192,57,43,0.7)",
               "rgba(241,148,138,0.6)", "rgba(230,126,34,0.7)", "rgba(213,216,220,0.7)"]
fig = go.Figure(go.Sankey(arrangement="fixed", textfont=dict(size=12, color="#1e1b4b", shadow="auto"),
    node=dict(label=labels, pad=22, thickness=16, x=[0.001, 0.5, 0.5, 0.999, 0.999], y=ys,
              color=["#566573", "#c0392b", "#7f8c8d", "#e67e22", "#aab7b8"],
              hovertemplate="%{label}<extra></extra>"),
    link=dict(source=[0, 0, 1, 1, 2, 2], target=[1, 2, 3, 4, 3, 4], value=vals, color=link_colors,
              hovertemplate="%{value:,} people<extra></extra>")))
steps = []
for p in PRIORS:
    v, lab, y = sankey_args(p)
    cnt = natural_frequencies(p, SENS, FP)
    steps.append(dict(method="update", label=f"{p:g}",
                      args=[{"link.value": [v], "node.label": [lab], "node.y": [y]},
                            {"title.text": f"P(condition | positive) = {cnt['tp']} / {cnt['tp'] + cnt['fp']} "
                                           f"= {s.bayes(p, SENS, FP)['posterior']:.3f}"}]))
fig.update_layout(title=steps[start]["args"][1]["title.text"],
                  sliders=[dict(active=start, steps=steps, currentvalue=dict(prefix="prior: "))])
show(frame(fig, height=500, xticks_lines=0, narrow_plot=340, axes=False))'''

CELLS[("02-bayes", "def post_curve(sens, fp)")] = '''prior_grid = np.logspace(-4, np.log10(0.5), 120)
SENS_GRID = [0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99]
FP_GRID = [0.001, 0.01, 0.05, 0.1, 0.2]

def post_curve(sens, fp):
    return [round(s.bayes(float(p), sens, fp)["posterior"], 5) for p in prior_grid]

def sens_steps(fp):
    return [dict(method="update", label=f"{sn:g}",
                 args=[{"y": [post_curve(sn, fp)]},
                       {"title.text": f"sensitivity {sn:g}, false-positive rate {fp:g}"}, [0]])
            for sn in SENS_GRID]

s0 = SENS_GRID.index(SENS)
fig = go.Figure()
fig.add_trace(go.Scatter(x=prior_grid.tolist(), y=post_curve(SENS, FP), mode="lines",
                         line=dict(color="#c0392b", width=3), name="P(condition | positive)",
                         hovertemplate="prior %{x:.4f}<br>posterior %{y:.3f}<extra></extra>"))
fig.add_trace(go.Scatter(x=prior_grid.tolist(), y=prior_grid.tolist(), mode="lines", hoverinfo="skip",
                         line=dict(color="gray", dash="dash"), name="posterior = prior"))
fig.update_layout(template="plotly_white",
                  title=f"sensitivity {SENS:g}, false-positive rate {FP:g}",
                  xaxis=dict(title="prior P(condition) (log scale)", type="log"),
                  yaxis=dict(title="posterior", range=[0, 1.02]),
                  sliders=[dict(active=s0, steps=sens_steps(FP), currentvalue=dict(prefix="sensitivity: "))],
                  updatemenus=[dict(type="dropdown", active=FP_GRID.index(FP),
                                    buttons=[dict(method="update", label=f"false-positive rate {f:g}",
                                                  args=[{"y": [post_curve(SENS, f)]},
                                                        {"sliders[0].steps": sens_steps(f), "sliders[0].active": s0,
                                                         "title.text": f"sensitivity {SENS:g}, false-positive rate {f:g}"},
                                                        [0]])
                                             for f in FP_GRID])])
show(frame(fig, height=520))'''

CELLS[("03-causal-inference", "def panel(cf)")] = '''CONF = [round(0.05 * i, 2) for i in range(15)]          # 0.00 ... 0.70 keeps every probability in [0, 1]

def panel(cf):
    r = s.causal(confound=cf)
    return [r["treated"], r["untreated"], r["do1"], r["do0"]], [r["observed"], r["ate"], r["observed"] - r["ate"]]

left, right = panel(0.5)
fig = make_subplots(rows=1, cols=2, column_widths=[0.58, 0.42], horizontal_spacing=0.12,
                    subplot_titles=("Seeing vs doing: P(Y = 1)", "Contrasts"))
fig.add_trace(go.Bar(x=["seeing<br>X=1", "seeing<br>X=0", "doing<br>do(X=1)", "doing<br>do(X=0)"],
                     y=left, marker_color=["#e67e22", "#f5cba7", "#2e86c1", "#aed6f1"],
                     texttemplate="%{y:.2f}", textposition="outside", cliponaxis=False,
                     hovertemplate="%{x}: %{y:.3f}<extra></extra>"), 1, 1)
fig.add_trace(go.Bar(x=["observed", "ATE", "bias"], y=right, marker_color=["#e67e22", "#2e86c1", "#c0392b"],
                     texttemplate="%{y:.2f}", textposition="outside", cliponaxis=False,
                     hovertemplate="%{x}: %{y:.3f}<extra></extra>"), 1, 2)
steps = []
for cf in CONF:
    l, r = panel(cf)
    steps.append(dict(method="restyle", label=f"{cf:.2f}", args=[{"y": [l, r]}, [0, 1]]))
fig.update_yaxes(range=[0, 1], title="probability", row=1, col=1)
fig.update_yaxes(range=[0, 0.8], title="difference", row=1, col=2)
fig.update_xaxes(tickangle=0, tickfont=dict(size=11))
fig.update_layout(template="plotly_white", showlegend=False,
                  sliders=[dict(active=CONF.index(0.5), steps=steps,
                                currentvalue=dict(prefix="confounding strength (Z → Y): "))])
show(frame(fig, height=470, xticks_lines=2, stack=True))'''

CELLS[("03-causal-inference", "GRAPHS = {")] = '''GRAPHS = {
    "Confounder": (nx.DiGraph([("Z", "X"), ("Z", "Y"), ("X", "Y")]),
                   {"Z": (0.5, 1.0), "X": (0.0, 0.0), "Y": (1.0, 0.0)}, set()),
    "Front-door": (nx.DiGraph([("U", "X"), ("U", "Y"), ("X", "M"), ("M", "Y")]),
                   {"U": (0.5, 1.0), "X": (0.0, 0.0), "M": (0.5, 0.0), "Y": (1.0, 0.0)}, {"U"}),
    "Collider": (nx.DiGraph([("X", "C"), ("Y", "C")]),
                 {"X": (0.0, 1.0), "Y": (1.0, 1.0), "C": (0.5, 0.0)}, set()),
}
for G, _, _ in GRAPHS.values():
    assert nx.is_directed_acyclic_graph(G)

def arrows(G, pos):
    # standoff (in pixels) stops each arrow at the edge of the 46-pixel node, at any zoom
    return [dict(x=pos[b][0], y=pos[b][1], ax=pos[a][0], ay=pos[a][1], xref="x", yref="y", axref="x", ayref="y",
                 showarrow=True, arrowhead=3, arrowsize=1.4, arrowwidth=2, arrowcolor="#34495e", text="",
                 standoff=26, startstandoff=26) for a, b in G.edges]

fig = go.Figure()
names = list(GRAPHS)
for name in names:
    G, pos, hidden = GRAPHS[name]
    nodes = list(G.nodes)
    fig.add_trace(go.Scatter(
        x=[pos[n][0] for n in nodes], y=[pos[n][1] for n in nodes], mode="markers+text", text=nodes,
        textfont=dict(size=18, color="white"), visible=(name == names[0]), hoverinfo="text",
        hovertext=[f"{n} (hidden)" if n in hidden else n for n in nodes],
        marker=dict(size=46, color=["#95a5a6" if n in hidden else "#2c3e50" for n in nodes],
                    line=dict(width=3, color=["#566573" if n in hidden else "#2c3e50" for n in nodes]),
                    symbol=["circle-dot" if n in hidden else "circle" for n in nodes])))
buttons = []
for i, name in enumerate(names):
    G, pos, _ = GRAPHS[name]
    buttons.append(dict(label=name, method="update",
                        args=[{"visible": [j == i for j in range(len(names))]},
                              {"annotations": arrows(G, pos), "title.text": f"{name} graph"}]))
G0, pos0, _ = GRAPHS[names[0]]
fig.update_layout(template="plotly_white", showlegend=False, title=f"{names[0]} graph",
                  annotations=arrows(G0, pos0),
                  xaxis=dict(visible=False, range=[-0.2, 1.2]), yaxis=dict(visible=False, range=[-0.25, 1.25]),
                  updatemenus=[dict(type="buttons", direction="right", buttons=buttons)])
show(frame(fig, height=400, xticks_lines=0, narrow_plot=260, axes=False))'''

CELLS[("03-causal-inference", "def kept_flags(t)")] = '''show_idx = np.random.default_rng(4).choice(n, 1500, replace=False)
xs, ys_, ss = Xc[show_idx], Yc[show_idx], S[show_idx]

def kept_flags(t):
    return (ss > t).astype(int).tolist()          # 1 = kept (red), 0 = dropped (grey)

def fit_line(t):
    sel = S > t
    b, a = np.polyfit(Xc[sel], Yc[sel], 1)
    return dict(type="line", x0=-3.5, x1=3.5, y0=a - 3.5 * b, y1=a + 3.5 * b, line=dict(color="#c0392b", width=3))

def title(t):
    return (f"keep a record if X + Y + noise > {t:+.1f} ({kept[t]:.0%} kept)<br>"
            f"correlation {r_sel[t]:+.2f} among kept, {r_all:+.3f} in all records<br>"
            f"red line: best fit through the kept records")

t0 = 1.0
fig = go.Figure(go.Scatter(x=xs.round(3).tolist(), y=ys_.round(3).tolist(), mode="markers",
                           marker=dict(size=5, color=kept_flags(t0), cmin=0, cmax=1,
                                       colorscale=[[0, "rgba(160,160,160,0.35)"], [1, "#c0392b"]]),
                           hovertemplate="X=%{x:.2f}, Y=%{y:.2f}<extra></extra>"))
steps = [dict(method="update", label=f"{t:+.1f}",
              args=[{"marker.color": [kept_flags(t)]}, {"shapes": [fit_line(t)], "title.text": title(t)}])
         for t in THRESH]
fig.update_layout(template="plotly_white", title=title(t0),
                  shapes=[fit_line(t0)],
                  xaxis=dict(title="X", range=[-3.5, 3.5], constrain="domain"),
                  yaxis=dict(title="Y", range=[-3.5, 3.5], scaleanchor="x", constrain="domain"),
                  sliders=[dict(active=THRESH.index(t0), steps=steps,
                                currentvalue=dict(prefix="selection threshold t: "))])
show(frame(fig, height=640, narrow_plot=330))'''

CELLS[("04-interference", "def arrow_data(phi)")] = '''PH = np.linspace(0, 2 * math.pi, 37)
curve_x = np.linspace(0, 2 * math.pi, 181)
fig = make_subplots(rows=1, cols=2, column_widths=[0.42, 0.58], horizontal_spacing=0.12,
                    subplot_titles=("Amplitudes to detector 0", "P(detector 0) vs phase"))

def arrow_data(phi):
    a = contributions(phi)
    tip1, tot = a[0], a.sum()
    return ([0, tip1.real], [0, tip1.imag]), ([tip1.real, tot.real], [tip1.imag, tot.imag]), \\
           ([0, tot.real], [0, tot.imag]), abs(tot)**2

circ = 0.5 + 0.5 * np.exp(1j * curve_x)
fig.add_trace(go.Scatter(x=circ.real.round(4).tolist(), y=circ.imag.round(4).tolist(), mode="lines",
                         line=dict(color="lightgray", dash="dot"), hoverinfo="skip", showlegend=False), 1, 1)
(a1x, a1y), (a2x, a2y), (tx, ty), p = arrow_data(PH[0])
fig.add_trace(go.Scatter(x=a1x, y=a1y, mode="lines+markers", line=dict(color="#2e86c1", width=4),
                         name="path 1 amplitude ½"), 1, 1)
fig.add_trace(go.Scatter(x=a2x, y=a2y, mode="lines+markers", line=dict(color="#e67e22", width=4),
                         name="path 2 amplitude ½·e<sup>iφ</sup>"), 1, 1)
fig.add_trace(go.Scatter(x=tx, y=ty, mode="lines+markers", line=dict(color="#c0392b", width=3, dash="dash"),
                         name="sum (length² = probability)"), 1, 1)
fig.add_trace(go.Scatter(x=curve_x.round(4).tolist(),
                         y=[round(s.interference(float(v))["p0"], 5) for v in curve_x],
                         mode="lines", line=dict(color="#c0392b"), name="quantum: (1 + cos φ)/2"), 1, 2)
fig.add_trace(go.Scatter(x=[0, 2 * math.pi], y=[0.5, 0.5], mode="lines", line=dict(color="gray", dash="dash"),
                         name="adding path probabilities: ½"), 1, 2)
fig.add_trace(go.Scatter(x=[PH[0]], y=[p], mode="markers", marker=dict(size=13, color="#c0392b"),
                         showlegend=False), 1, 2)
steps = []
for phi in PH:
    (a1x, a1y), (a2x, a2y), (tx, ty), p = arrow_data(phi)
    steps.append(dict(method="restyle", label=f"{math.degrees(phi):.0f}°",
                      args=[{"x": [a2x, tx, [float(phi)]], "y": [[round(v, 5) for v in a2y],
                                                              [round(v, 5) for v in ty], [round(p, 5)]]},
                            [2, 3, 6]]))
fig.update_xaxes(range=[-0.15, 1.15], title="real part", constrain="domain", row=1, col=1)
fig.update_yaxes(range=[-0.65, 0.65], title="imaginary part", scaleanchor="x", constrain="domain", row=1, col=1)
fig.update_xaxes(title="phase φ (radians)", row=1, col=2)
fig.update_yaxes(range=[-0.02, 1.02], title="probability", row=1, col=2)
fig.update_layout(template="plotly_white",
                  sliders=[dict(active=0, steps=steps, currentvalue=dict(prefix="phase φ = "))])
show(frame(fig, height=520, stack=True))'''

CELLS[("04-interference", "mz_dephased(float(v), 0.0)[0], 5)")] = '''def deph_title(p):
    return f"dephasing p = {p:.1f}<br>coherence |ρ01| = {(1 - p) / 2:.2f}, visibility = {vis_deph[p]:.2f}"

fig = go.Figure()
fig.add_trace(go.Scatter(x=curve_x.round(4).tolist(), y=[round(mz_dephased(float(v), 0.0)[0], 5) for v in curve_x],
                         mode="lines", line=dict(color="#c0392b", width=3), name="P(detector 0)"))
fig.add_trace(go.Scatter(x=curve_x.round(4).tolist(), y=[round(1 - mz_dephased(float(v), 0.0)[0], 5) for v in curve_x],
                         mode="lines", line=dict(color="#2e86c1", width=3), name="P(detector 1)"))
fig.add_trace(go.Scatter(x=[0, 2 * math.pi], y=[0.5, 0.5], mode="lines", line=dict(color="gray", dash="dash"),
                         name="classical mixture of paths"))
steps = []
for p in DEPH:
    y0 = [round(mz_dephased(float(v), p)[0], 5) for v in curve_x]
    steps.append(dict(method="update", label=f"{p:.1f}",
                      args=[{"y": [y0, [round(1 - v, 5) for v in y0]]}, {"title.text": deph_title(p)}, [0, 1]]))
fig.update_layout(template="plotly_white", title=deph_title(DEPH[0]),
                  xaxis=dict(title="phase φ (radians)"), yaxis=dict(title="probability", range=[-0.02, 1.02]),
                  sliders=[dict(active=0, steps=steps, currentvalue=dict(prefix="dephasing strength p = "))])
show(frame(fig, height=500))'''

CELLS[("04-interference", "mz_tagged(float(v), 0.0), 5)")] = '''fig = make_subplots(rows=1, cols=2, column_widths=[0.55, 0.45], horizontal_spacing=0.12,
                    subplot_titles=("P(detector 0) vs phase", "Visibility and path record"))
fig.add_trace(go.Scatter(x=curve_x.round(4).tolist(), y=[round(mz_tagged(float(v), 0.0), 5) for v in curve_x],
                         mode="lines", line=dict(color="#c0392b", width=3), name="tagged interferometer"), 1, 1)
fig.add_trace(go.Scatter(x=[0, 2 * math.pi], y=[0.5, 0.5], mode="lines", line=dict(color="gray", dash="dash"),
                         name="classical mixture"), 1, 1)
fig.add_trace(go.Bar(x=["V<br>visibility", "D<br>path info", "V² + D²<br>total"], y=[1, 0, 1],
                     marker_color=["#c0392b", "#2e86c1", "#7f8c8d"], showlegend=False,
                     texttemplate="%{y:.2f}", textposition="outside", cliponaxis=False,
                     hovertemplate="%{x}: %{y:.3f}<extra></extra>"), 1, 2)
steps = []
for th in THETAS:
    w = wp[float(th)]
    y0 = [round(mz_tagged(float(v), float(th)), 5) for v in curve_x]
    steps.append(dict(method="restyle", label=f"{math.degrees(th):.0f}°",
                      args=[{"y": [y0, [round(w["V"], 4), round(w["D"], 4), round(w["V"]**2 + w["D"]**2, 4)]]}, [0, 2]]))
fig.update_yaxes(range=[-0.02, 1.02], title="probability", row=1, col=1)
fig.update_yaxes(range=[0, 1.15], row=1, col=2)
fig.update_xaxes(title="phase φ (radians)", row=1, col=1)
fig.update_xaxes(tickangle=0, tickfont=dict(size=11), row=1, col=2)
fig.update_layout(template="plotly_white",
                  sliders=[dict(active=0, steps=steps, currentvalue=dict(prefix="tag rotation θ (180° = full record): "))])
show(frame(fig, height=500, xticks_lines=2, stack=True))'''

PROSE = {"03-causal-inference": [("The left panel", "The first panel"), ("the right panel", "the second panel"),
                                 ("The right panel", "The second panel")],
         "04-interference": [("The left panel", "The first panel"), ("The right panel", "The second panel"),
                             ("the right panel", "the second panel")]}

# static matplotlib summary figures: move legends off the data, split a crowded title
STATIC = [
    ("01-chance", 'ax[0].legend(frameon=False, loc="upper right", fontsize=8)',
     'ax[0].legend(frameon=False, loc="lower right", fontsize=8)'),
    ("04-interference", 'ax[0].legend(frameon=False, fontsize=8, loc="upper center", ncol=4)',
     'ax[0].legend(frameon=False, fontsize=8, loc="lower left", ncol=2)'),
    ("03-causal-inference",
     'ax.set_title("(A) measured confounder, n = 20,000   (B) hidden confounder + mediator, n = 20,000", fontsize=9)',
     'ax.set_title("Estimates with 95% bootstrap intervals (blue: valid, orange: biased)\\n"\n'
     '             "(A) measured confounder   (B) hidden confounder and mediator; n = 20,000 each", fontsize=9)\n'
     'ax.axhline(2.5, color="#d5d8dc", lw=0.8)'),
]


def main():
    done = 0
    for nb in ["01-chance", "02-bayes", "03-causal-inference", "04-interference"]:
        f = BOOK / "labs" / f"{nb}.ipynb"
        d = json.loads(f.read_text(encoding="utf-8"))
        for c in d["cells"]:
            src = "".join(c["source"])
            if c["cell_type"] == "code" and "from qcai.viz import show\n" in src + "\n":
                src = re.sub(r"from qcai\.viz import show$", "from qcai.viz import show, frame", src, flags=re.M)
            if c["cell_type"] == "code":
                for (book, marker), new in CELLS.items():
                    if book == nb and marker in src and "show(" in src:
                        src = new
                        done += 1
            if c["cell_type"] == "code":
                for book, a, b in STATIC:
                    if book == nb:
                        src = src.replace(a, b)
            if c["cell_type"] == "markdown":
                for a, b in PROSE.get(nb, []):
                    src = src.replace(a, b)
            lines = src.split("\n")
            c["source"] = [ln + "\n" for ln in lines[:-1]] + [lines[-1]]
        f.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    assert done == len(CELLS), (done, len(CELLS))
    print(f"rewrote {done} figure cells")


if __name__ == "__main__":
    main()
