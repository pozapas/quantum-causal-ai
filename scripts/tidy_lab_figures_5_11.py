"""Unit `labs-figures-tidy`: give the interactive figures in Labs 5-11 a clean layout.  Run from book/.

Each figure is laid out with qcai.viz.frame, which places the title, menu, legend, subplot
titles and slider in separate bands and adds a narrow layout for phones.  qcai.labviz adds a
band for a second slider and lets a figure keep extra room on the right for a colorbar.

A figure cell is found by a marker string it contains.  Everything above the cell's split
line (the computations, prints and asserts) is kept byte for byte; only the figure code from
the split line on is replaced, so the script can be re-run safely.
"""
import json
import pathlib
import re

BOOK = pathlib.Path(__file__).resolve().parents[1]
NBS = ["05-qubit-bloch", "06-entanglement-bell", "07-noise-channels", "08-variational-gradients",
       "09-quantum-switch", "10-classical-shadows", "11-quantum-causal-inference"]

# (notebook, cell marker) -> (split line, new figure code starting with that split line)
TAILS = {}

TAILS[("05-qubit-bloch", "Pure qubit state on the Bloch sphere")] = ("fig.update_layout(\n", r'''fig.update_layout(
    template="plotly_white", showlegend=False, title="Pure qubit state on the Bloch sphere",
    scene=dict(aspectmode="cube", xaxis=dict(range=[-1.4, 1.4], title="x"),
               yaxis=dict(range=[-1.4, 1.4], title="y"), zaxis=dict(range=[-1.4, 1.4], title="z")),
    sliders=[dict(active=t0, currentvalue=dict(prefix="θ = "), steps=theta_steps),
             dict(active=0, currentvalue=dict(prefix="φ = "), steps=phi_steps)])
frame(fig, height=600, xticks_lines=0, axes=False, narrow_plot=340)
tweak(fig, both={"sliders[0].pad.l": 14, "sliders[0].pad.r": 14})
show(second_slider(camera(fig)))''')

TAILS[("05-qubit-bloch", "Estimating p₀ from N shots")] = ("fig.update_layout(", r'''fig.update_layout(template="plotly_white", title="Estimating p₀ from N shots", xaxis_title="θ (degrees)",
                  yaxis_title="probability of outcome 0", yaxis_range=[-0.05, 1.05],
                  sliders=[dict(active=0, currentvalue=dict(prefix="shots N = "), steps=steps)])
show(frame(fig, height=480))''')

TAILS[("05-qubit-bloch", "Random mixed states fill the Bloch ball")] = ("", r'''fig = go.Figure([
    go.Surface(x=np.cos(u) * np.sin(v), y=np.sin(u) * np.sin(v), z=np.cos(v), opacity=0.08, showscale=False,
               colorscale=[[0, "gray"], [1, "gray"]], hoverinfo="skip"),
    go.Scatter3d(x=R[:, 0], y=R[:, 1], z=R[:, 2], mode="markers",
                 marker=dict(size=3, color=pur, colorscale="Viridis", cmin=0.5, cmax=1,
                             colorbar=dict(title="purity", x=0.86, xanchor="left", thickness=12, len=0.8)),
                 text=[f"|r| = {r:.3f}, purity = {p:.3f}" for r, p in zip(radius, pur)], hoverinfo="text"),
])
fig.update_layout(template="plotly_white", showlegend=False, title="Random mixed states fill the Bloch ball",
                  scene=dict(aspectmode="cube", domain=dict(x=[0, 0.84], y=[0, 1])))
show(camera(frame(fig, height=540, xticks_lines=0, axes=False, narrow_plot=320)))''')

TAILS[("06-entanglement-bell", "CHSH value as Bob rotates")] = ("fig.update_layout(", r'''fig.update_layout(template="plotly_white", title="CHSH value as Bob rotates his settings<br>a₀ = 0, a₁ = 90°, b₀ = β, b₁ = −β",
                  xaxis=dict(title="β (degrees)", dtick=90), yaxis=dict(title="S", range=[-3.1, 3.1]),
                  sliders=[dict(active=len(vs) - 1, currentvalue=dict(prefix="visibility v = "), steps=steps)])
show(frame(fig, height=520))''')

TAILS[("06-entanglement-bell", "Werner state: entanglement vs CHSH")] = ("fig = go.Figure([\n", r'''fig = go.Figure([
    go.Scatter(x=vgrid, y=conc, name="concurrence (3v−1)/2", line=dict(color="#4c78a8", width=3), yaxis="y"),
    go.Scatter(x=vgrid, y=smax, name="max CHSH 2√2·v", line=dict(color="crimson", width=3), yaxis="y2"),
    go.Scatter(x=[0, 1], y=[2, 2], mode="lines", name="local bound 2", line=dict(color="black", dash="dash"), yaxis="y2"),
    go.Scatter(x=[0.5], y=[s.concurrence(w)], mode="markers", marker=dict(size=12, color="#4c78a8"),
               name="selected v (concurrence)", showlegend=False, yaxis="y"),
    go.Scatter(x=[0.5], y=[s.horodecki_max_chsh(w)], mode="markers", marker=dict(size=12, color="crimson"),
               name="selected v (max CHSH)", showlegend=False, yaxis="y2"),
])
steps = []
for v in np.round(np.linspace(0, 1, 21), 2):
    wv = s.werner(float(v))
    steps.append(dict(method="restyle", label=f"{v:.2f}",
                      args=[{"x": [[v], [v]], "y": [[s.concurrence(wv)], [s.horodecki_max_chsh(wv)]]}, [3, 4]]))
fig.update_layout(
    template="plotly_white", title="Werner state: entanglement vs CHSH violation",
    xaxis=dict(title="visibility v", range=[0, 1], domain=[0, 0.83]),
    yaxis=dict(title="concurrence", range=[-0.05, 1.05]),
    yaxis2=dict(title="max CHSH", overlaying="y", side="right", anchor="x", range=[-0.1, 3.2], showgrid=False),
    shapes=[dict(type="rect", xref="x", yref="paper", x0=lo, x1=hi, y0=0, y1=1, fillcolor="gold", opacity=0.2, line_width=0)],
    annotations=[dict(x=(lo + hi) / 2, y=0.98, xref="x", yref="paper", yanchor="top", showarrow=False,
                      text="entangled,<br>no CHSH<br>violation", font=dict(size=11))],
    sliders=[dict(active=10, currentvalue=dict(prefix="v = "), steps=steps)])
frame(fig, height=500)
show(tweak(fig, both={"sliders[0].pad.r": 14}))''')

TAILS[("07-noise-channels", "def closed_form(name, p, R)")] = ("fig = go.Figure(traces)\n", r'''fig = go.Figure(traces)
idx = [1, 2, 3]
steps = []
for p in strengths:
    ims = [imgs[(n, p)] for n in names]
    steps.append(dict(method="restyle", label=f"{p:.1f}",
                      args=[{"x": [im[..., 0].tolist() for im in ims], "y": [im[..., 1].tolist() for im in ims],
                             "z": [im[..., 2].tolist() for im in ims]}, idx]))
buttons = [dict(label=n, method="restyle", args=[{"visible": [j == k for j in range(3)]}, idx]) for k, n in enumerate(names)]
fig.update_layout(template="plotly_white", showlegend=False, title="Bloch sphere after a noise channel",
                  scene=dict(aspectmode="cube", xaxis=dict(range=[-1.1, 1.1]), yaxis=dict(range=[-1.1, 1.1]),
                             zaxis=dict(range=[-1.1, 1.1])),
                  updatemenus=[dict(type="buttons", direction="right", buttons=buttons)],
                  sliders=[dict(active=p_init, currentvalue=dict(prefix="strength p (or γ) = "), steps=steps)])
frame(fig, height=620, xticks_lines=0, axes=False, narrow_plot=340)
show(camera(tweak(fig, both={"sliders[0].pad.l": 14, "sliders[0].pad.r": 14})))''')

TAILS[("07-noise-channels", "def purity_trace(name, p)")] = ("p0i = 2\n", r'''p0i = 2
# depolarizing and dephasing give the same purity for |+>, so one is drawn wide and pale, the other dashed on top
style = {"depolarizing": dict(mode="lines", line=dict(color="rgba(76,120,168,0.4)", width=8)),
         "dephasing": dict(mode="lines+markers", line=dict(color="#1f4e79", width=2, dash="dash"), marker=dict(size=5)),
         "amplitude damping": dict(mode="lines+markers", line=dict(color="#e45756", width=2.5), marker=dict(size=6))}
label = {"depolarizing": "depolarizing", "dephasing": "dephasing (same values)", "amplitude damping": "amplitude damping"}
fig = go.Figure([go.Scatter(x=ns, y=P[(n, ps[p0i])], name=label[n], **style[n]) for n in names])
steps = [dict(method="restyle", label=f"{p:.2f}", args=[{"y": [P[(n, p)] for n in names]}, [0, 1, 2]]) for p in ps]
fig.add_hline(y=0.5, line_dash="dot", annotation_text="maximally mixed", annotation_position="bottom right")
fig.update_layout(template="plotly_white", title="Purity of |+⟩ after n uses of the channel",
                  xaxis_title="number of applications n", yaxis_title="purity Tr ρ²", yaxis_range=[0.45, 1.02],
                  sliders=[dict(active=p0i, currentvalue=dict(prefix="strength = "), steps=steps)])
show(frame(fig, height=500))''')

TAILS[("08-variational-gradients", "def loss_grad(t)")] = ("fig = go.Figure([\n", r'''fig = go.Figure([
    go.Heatmap(x=grid, y=grid, z=Lgrid, colorscale="Viridis",
               colorbar=dict(title="loss", x=0.87, xanchor="left", thickness=12),
               hovertemplate="θ0=%{x:.2f}<br>θ1=%{y:.2f}<br>loss=%{z:.3f}<extra></extra>"),
    go.Scatter(x=path[:, 0], y=path[:, 1], mode="lines+markers",
               marker=dict(size=5, color="white", line=dict(color="black", width=1)),
               line=dict(color="white"), name="gradient-descent path"),
    go.Scatter(x=[theta_star[0]], y=[theta_star[1]], mode="markers", marker=dict(symbol="x", size=12, color="red"), name="θ*"),
])
fig.update_layout(template="plotly_white", title="Loss L(θ0, θ1) and the training path",
                  xaxis=dict(title="θ0", domain=[0, 0.85]), yaxis_title="θ1")
show(frame(fig, height=560, narrow_plot=300))''')

TAILS[("08-variational-gradients", "def fit_curve(t)")] = ("fig = make_subplots(", r'''fig = make_subplots(rows=1, cols=2, horizontal_spacing=0.14, subplot_titles=("Model vs data", "Training loss (log scale)"))
fig.add_trace(go.Scatter(x=xs, y=ys, mode="markers", name="data", marker=dict(color="black", size=8)), 1, 1)
fig.add_trace(go.Scatter(x=xx, y=fit_curve(path[0]), mode="lines", name="model", line=dict(color="crimson", width=3)), 1, 1)
fig.add_trace(go.Scatter(x=[0], y=[losses[0]], mode="lines+markers", name="loss", line=dict(color="#4c78a8")), 1, 2)
steps = [dict(method="restyle", label=str(i),
              args=[{"x": [xx.tolist(), list(range(i + 1))], "y": [fit_curve(path[i]), losses[: i + 1].tolist()]}, [1, 2]])
         for i in frames_idx]
fig.update_xaxes(title_text="x", row=1, col=1); fig.update_yaxes(range=[-1.1, 1.1], title_text="f(x)", row=1, col=1)
fig.update_xaxes(range=[-2, len(path)], title_text="step", row=1, col=2)
fig.update_yaxes(type="log", range=[-9, 0.5], dtick=3, exponentformat="power", title_text="loss", row=1, col=2)
fig.update_layout(template="plotly_white", title="Training with exact parameter-shift gradients",
                  sliders=[dict(active=0, currentvalue=dict(prefix="step "), steps=steps)])
show(frame(fig, height=520, stack=True))''')

TAILS[("08-variational-gradients", "Gradient error vs shots per circuit")] = ("fig.update_layout(", r'''fig.update_layout(template="plotly_white", title="Gradient error vs shots per circuit<br>(4000 repetitions per point)",
                  xaxis=dict(type="log", dtick=1, title="shots per circuit N"),
                  yaxis=dict(type="log", dtick=1, title="RMSE of the gradient estimate"),
                  sliders=[dict(active=1, currentvalue=dict(prefix="finite-difference step h = "), steps=steps)])
show(frame(fig, height=520))''')

TAILS[("09-quantum-switch", "def switch_image(p)")] = ("fig = go.Figure([\n", r'''fig = go.Figure([
    go.Scatter3d(x=R0[..., 0].ravel(), y=R0[..., 1].ravel(), z=R0[..., 2].ravel(), mode="markers",
                 marker=dict(size=1.5, color="lightgray"), hoverinfo="skip", name="input sphere"),
    go.Surface(x=im[..., 0], y=im[..., 1], z=im[..., 2], colorscale="Purples", showscale=False, opacity=0.9,
               name="switch, control outcome +", showlegend=True),
    go.Scatter3d(x=dfi[..., 0].ravel(), y=dfi[..., 1].ravel(), z=dfi[..., 2].ravel(), mode="markers",
                 marker=dict(size=2.5, color="black"), name="definite order"),
])
steps = [dict(method="restyle", label=f"{p:.1f}",
              args=[{"x": [imgs[p][..., 0].tolist(), defs[p][..., 0].ravel().tolist()],
                     "y": [imgs[p][..., 1].tolist(), defs[p][..., 1].ravel().tolist()],
                     "z": [imgs[p][..., 2].tolist(), defs[p][..., 2].ravel().tolist()]}, [1, 2]]) for p in ps]
fig.update_layout(template="plotly_white", title="Target Bloch ball: the switch (control<br>outcome +) vs a definite order",
                  scene=dict(aspectmode="cube", xaxis=dict(range=[-1, 1]), yaxis=dict(range=[-1, 1]),
                             zaxis=dict(range=[-1, 1])),
                  sliders=[dict(active=p0, currentvalue=dict(prefix="depolarizing p (both) = "), steps=steps)])
frame(fig, height=640, xticks_lines=0, axes=False, narrow_plot=340)
show(camera(tweak(fig, both={"sliders[0].pad.l": 14, "sliders[0].pad.r": 14})))''')

TAILS[("09-quantum-switch", "Quantum switch of two depolarizing channels")] = ("keys = list(Z)\n", r'''keys = list(Z)
short = ["⟨X_c⟩", "D_switch", "D_definite"]

def ztitle(k):
    return f"Quantum switch of two depolarizing channels<br>shown: {k}"

fig = go.Figure(go.Heatmap(x=pa, y=pa, z=Z[keys[0]], zmin=0, zmax=1, colorscale="Magma",
                           colorbar=dict(x=0.87, xanchor="left", thickness=12),
                           hovertemplate="p_A=%{x:.2f}<br>p_B=%{y:.2f}<br>value=%{z:.3f}<extra></extra>"))
fig.update_layout(template="plotly_white", title=ztitle(keys[0]),
                  xaxis=dict(title="p_A", domain=[0, 0.85]), yaxis_title="p_B",
                  updatemenus=[dict(type="buttons", direction="right",
                                    buttons=[dict(label=b, method="update", args=[{"z": [Z[k]]}, {"title.text": ztitle(k)}])
                                             for b, k in zip(short, keys)])])
show(frame(fig, height=560, narrow_plot=300))''')

TAILS[("10-classical-shadows", "One set of random-Pauli shots")] = ('cols = ["#4c78a8", "#59a14f", "crimson"]\n', r'''cols = ["#4c78a8", "#59a14f", "crimson"]
fig = go.Figure()
for i, lab in enumerate("XYZ"):
    fig.add_trace(go.Scatter(x=ns + 1, y=running[ns, i], mode="lines", name=f"⟨{lab}⟩", legendgroup=lab,
                             line=dict(color=cols[i])))
    fig.add_trace(go.Scatter(x=[1, shots], y=[truth[i]] * 2, mode="lines", name=f"true ⟨{lab}⟩", legendgroup=lab,
                             showlegend=False, line=dict(color=cols[i], dash="dot")))
vis = lambda i: [j // 2 == i for j in range(6)]
fig.update_layout(template="plotly_white",
                  title="One set of random-Pauli shots, three observables<br>solid: running estimate, dotted: true value",
                  xaxis=dict(type="log", dtick=1, title="number of shots"),
                  yaxis=dict(title="estimate", range=[-1.6, 1.6]),
                  updatemenus=[dict(type="buttons", direction="right", buttons=
                                    [dict(label="all", method="restyle", args=[{"visible": [True] * 6}])] +
                                    [dict(label=f"⟨{lab}⟩", method="restyle", args=[{"visible": vis(i)}]) for i, lab in enumerate("XYZ")])])
show(frame(fig, height=520))''')

TAILS[("10-classical-shadows", "Shadow estimation error vs shots")] = ('colors = {1: "#4c78a8"', r'''colors = {1: "#4c78a8", 2: "#59a14f", 3: "#f28e2b", 4: "crimson"}
fig = go.Figure()
for k in chosen:
    fig.add_trace(go.Scatter(x=Ns, y=rmse[k], mode="markers+lines", name=f"weight {k}", legendgroup=str(k),
                             line=dict(color=colors[k])))
    fig.add_trace(go.Scatter(x=Ns, y=theory[k], mode="lines", name=f"weight {k}, theory", legendgroup=str(k),
                             showlegend=False, line=dict(color=colors[k], dash="dot")))
buttons = [dict(label="all", method="restyle", args=[{"visible": [True] * 8}])]
buttons += [dict(label=f"k = {k}", method="restyle", args=[{"visible": [j // 2 == k - 1 for j in range(8)]}]) for k in chosen]
fig.update_layout(template="plotly_white",
                  title=(f"Shadow estimation error vs shots<br>({n} qubits, {R} repetitions; solid: simulated)<br>"
                         "dotted: theory √((3<sup>k</sup> − ⟨P⟩²)/N)"),
                  xaxis=dict(type="log", dtick=1, title="shots N"), yaxis=dict(type="log", dtick=1, title="RMSE"),
                  updatemenus=[dict(type="buttons", direction="right", buttons=buttons)])
show(frame(fig, height=560))''')

TAILS[("11-quantum-causal-inference", "def chsh_from_local_model(")] = ("fig = go.Figure([\n", r'''fig = go.Figure([
    go.Histogram(x=S_classical, nbinsx=80, name="classical common causes", marker_color="#4c78a8"),
    go.Scatter(x=[S_quantum[1.0]] * 2, y=[0, 400], mode="lines", name="quantum, Werner state",
               line=dict(color="crimson", width=4)),
    go.Scatter(x=[2, 2, None, -2, -2], y=[0, 400, None, 0, 400], mode="lines", name="classical bound |S| = 2",
               line=dict(color="black", dash="dash")),
])
steps = [dict(method="restyle", label=f"{v:.2f}", args=[{"x": [[S_quantum[v]] * 2]}, [1]]) for v in vs]
fig.update_layout(template="plotly_white", title="CHSH: classical vs quantum common causes",
                  xaxis=dict(title="S", range=[-3, 3]), yaxis_title="count",
                  sliders=[dict(active=len(vs) - 1, currentvalue=dict(prefix="Werner visibility v = "), steps=steps)])
show(frame(fig, height=500))''')

TAILS[("11-quantum-causal-inference", "def tetra_mesh(")] = ("Vcc, Vce = ", r'''Vcc, Vce = list(bell_vertices.values()), list(unitary_vertices.values())
traces = [
    go.Scatter3d(x=cc_pts[:, 0], y=cc_pts[:, 1], z=cc_pts[:, 2], mode="markers", marker=dict(size=2, color="#4c78a8"),
                 name="common cause: random ρ_AB", hovertemplate="c=(%{x:.2f}, %{y:.2f}, %{z:.2f})"),
    tetra_mesh(Vcc, "#4c78a8", "T_cc (Bell states)"), tetra_edges(Vcc, "#4c78a8"),
    go.Scatter3d(x=ce_pts[:, 0], y=ce_pts[:, 1], z=ce_pts[:, 2], mode="markers", marker=dict(size=2, color="crimson"),
                 name="cause–effect: random E", hovertemplate="c=(%{x:.2f}, %{y:.2f}, %{z:.2f})"),
    tetra_mesh(Vce, "crimson", "T_ce (Pauli unitaries)"), tetra_edges(Vce, "crimson"),
    go.Scatter3d(x=[v[0] for v in Vcc + Vce], y=[v[1] for v in Vcc + Vce], z=[v[2] for v in Vcc + Vce], mode="text",
                 text=["Φ+", "Φ−", "Ψ+", "Ψ−", "I", "X", "Y", "Z"], showlegend=False, hoverinfo="skip"),
]
fig = go.Figure(traces)
show_cc = [True, True, True, False, False, False, True]
show_ce = [False, False, False, True, True, True, True]
fig.update_layout(template="plotly_white", title="Pauli correlations (c_x, c_y, c_z):<br>common cause vs cause–effect",
                  scene=dict(aspectmode="cube", xaxis_title="c_x", yaxis_title="c_y", zaxis_title="c_z"),
                  updatemenus=[dict(type="buttons", direction="right", buttons=[
                      dict(label="both", method="restyle", args=[{"visible": [True] * 7}]),
                      dict(label="common cause", method="restyle", args=[{"visible": show_cc}]),
                      dict(label="cause–effect", method="restyle", args=[{"visible": show_ce}])])])
show(camera(frame(fig, height=680, xticks_lines=0, axes=False, narrow_plot=340)))''')

TAILS[("11-quantum-causal-inference", "Three research programs")] = ("posm = ", r'''posm = {}   # two columns: causal models and Bell on the left, machine learning and causal order on the right
LEFT = ["SCMs & do-calculus", "Causal discovery", "Bell / CHSH", "Lab 6", "Quantum common causes",
        "Quantum causal models (unitary)", "Entropic constraints", "Causally neutral inference", "Causal tomography",
        "Lab 11", "PDM causal inference", "Process-based QCM"]
RIGHT = ["Lab 10", "Classical shadows", "Data & advantage", "QML overview", "Quantum kernels", "Circuit learning",
         "Parameter shift", "Lab 8", "Barren plateaus", None, "Quantum combs", "Quantum switch", "Lab 9",
         "Causal witnesses", "Process matrices"]
XL, XR, ROWS = 0.42, 0.58, len(RIGHT) - 1
for k, n in enumerate(LEFT):
    posm[n] = (XL, -k * ROWS / (len(LEFT) - 1))
for k, n in enumerate(RIGHT):
    if n:
        posm[n] = (XR, -k)
assert set(posm) == set(nodes)
SHOWN = {"Quantum common causes": "Quantum common<br>causes", "Quantum causal models (unitary)": "Unitary quantum<br>causal models",
         "Causally neutral inference": "Causally neutral<br>inference"}

def edge_xy(a, b):
    """A straight line between the columns; within a column, an arc that bends towards the middle."""
    (x1, y1), (x2, y2) = posm[a], posm[b]
    if x1 != x2:
        return [x1, x2, None], [y1, y2, None]
    bend = (1 if x1 < 0.5 else -1) * min(0.075, 0.02 * abs(y1 - y2))
    t = np.linspace(0, 1, 17)
    return (list(x1 + 2 * bend * t * (1 - t)) + [None]), (list(y1 + (y2 - y1) * t) + [None])

ex, ey = [], []
for a, b in edges:
    xs_, ys_ = edge_xy(a, b)
    ex += xs_; ey += ys_
traces = [go.Scatter(x=ex, y=ey, mode="lines", line=dict(color="#c8ccd0", width=1.5), hoverinfo="skip", showlegend=False)]
labels = {"classical": "classical causal inference", "QCM": "quantum causal models", "ICO": "indefinite causal order",
          "QML": "quantum machine learning", "bridge": "bridge (Bell)", "lab": "labs in this book"}
order = list(PROG)
for prog in order:
    ns = [n for n, (p, _) in nodes.items() if p == prog]
    traces.append(go.Scatter(x=[posm[n][0] for n in ns], y=[posm[n][1] for n in ns], mode="markers+text",
                             text=[SHOWN.get(n, n) for n in ns], cliponaxis=False,
                             textposition=["middle left" if posm[n][0] < 0.5 else "middle right" for n in ns],
                             marker=dict(size=15, color=PROG[prog], line=dict(color="black", width=1)),
                             hovertext=[f"{n}<br>{nodes[n][1]}" for n in ns], hoverinfo="text", name=labels[prog]))
fig = go.Figure(traces)
def highlight(prog):
    return [1.0] + [1.0 if p == prog or prog == "all" else 0.15 for p in order]
fig.update_layout(template="plotly_white", title="Three research programs and how this<br>book's labs connect to them",
                  xaxis=dict(visible=False, range=[-0.01, 1.01]), yaxis=dict(visible=False, range=[-ROWS - 0.6, 0.6]),
                  updatemenus=[dict(type="dropdown", buttons=
                                    [dict(label="highlight: all programs", method="restyle", args=[{"opacity": highlight("all")}])] +
                                    [dict(label=f"highlight: {labels[p]}", method="restyle", args=[{"opacity": highlight(p)}])
                                     for p in ("QCM", "ICO", "QML")])])
frame(fig, height=700, xticks_lines=0, axes=False, narrow_plot=430)
show(tweak(fig, wide={"font.size": 12}, narrow={"font.size": 10}))''')

PROSE = {"11-quantum-causal-inference": [("Use the buttons to highlight one program.", "Use the menu to highlight one program.")]}

# static matplotlib figures: (notebook, old, new); a pair is skipped once `new` is in the cell
STATIC = [
    # Lab 5: the two panels one above the other, so they stay readable on a phone
    ("05-qubit-bloch", "fig, ax = plt.subplots(1, 2, figsize=(10, 4))", "fig, ax = plt.subplots(2, 1, figsize=(5.6, 8.6))"),
    # Lab 6: four joint tables in a 2 x 2 grid instead of one row, white numbers on dark cells
    ("06-entanglement-bell", "fig, axes = plt.subplots(1, 4, figsize=(13, 3.3))", "fig, axes = plt.subplots(2, 2, figsize=(7.4, 6.6))"),
    ("06-entanglement-bell", "    ax = axes[k]\n", "    ax = axes.flat[k]\n"),
    ("06-entanglement-bell", 'ax.text(j, i, f"{P[i, j]:.3f}", ha="center", va="center")',
     'ax.text(j, i, f"{P[i, j]:.3f}", ha="center", va="center", fontsize=11,\n'
     '                    color="white" if P[i, j] > 0.3 else "black")'),
    ("06-entanglement-bell", 'ax.set_title(f"x={x}, y={y}:  E = {E:+.3f}")', 'ax.set_title(f"x = {x}, y = {y}:  E = {E:+.3f}")'),
    ("06-entanglement-bell", 'plt.suptitle("Joint outcome tables for |Φ+⟩ at the optimal CHSH settings (marginals all 1/2)")',
     'plt.suptitle("Joint outcome tables for |Φ+⟩ at the optimal CHSH settings\\n(every marginal is 1/2)")'),
    # Lab 7: horizontal two-line tick labels, a two-line title, and a count where eigenvalues coincide
    ("07-noise-channels", "ax.set_xticks(range(len(labels)), labels, rotation=10)",
     'ax.set_xticks(range(len(labels)), [lab.replace(" ", "\\n", 1) if len(lab) > 12 else lab for lab in labels])'),
    ("07-noise-channels", 'ax.set_title("CP test: all Choi eigenvalues ≥ 0 (channels at strength 0.5) vs the transpose map")',
     'ax.set_title("CP test: Choi eigenvalues of three channels at strength 0.5 and of the transpose map\\n"\n'
     '             "(a map is completely positive when all its Choi eigenvalues are ≥ 0)", fontsize=10)'),
    ("07-noise-channels",
     '    ax.scatter([k] * 4, eigs[lab], s=60, color="crimson" if eigs[lab].min() < 0 else "#4c78a8", zorder=3)\n',
     '    ax.scatter([k] * 4, eigs[lab], s=60, color="crimson" if eigs[lab].min() < 0 else "#4c78a8", zorder=3)\n'
     '    vals, counts = np.unique(np.round(eigs[lab], 9), return_counts=True)\n'
     '    for val, cnt in zip(vals, counts):          # repeated eigenvalues sit on one dot\n'
     '        if cnt > 1:\n'
     '            ax.annotate(f"×{cnt}", (k, val), xytext=(9, 0), textcoords="offset points", va="center", fontsize=9)\n'),
    ("07-noise-channels", "fig, ax = plt.subplots(figsize=(9, 3.6))", "fig, ax = plt.subplots(figsize=(7.4, 3.9))"),
    # Lab 8: legend off the reference line
    ("08-variational-gradients", "ax.legend(); plt.tight_layout(); plt.show()", 'ax.legend(loc="lower left"); plt.tight_layout(); plt.show()'),
    # Lab 9: the two matrices one above the other, readable numbers on dark cells, no "-0.000", a two-line title
    ("09-quantum-switch", "fig, ax = plt.subplots(1, 2, figsize=(9, 4))", "fig, ax = plt.subplots(2, 1, figsize=(4.8, 8.8))"),
    ("09-quantum-switch", '            a.text(j, i, f"{np.real(M[i, j]):.3f}", ha="center", va="center", fontsize=9)\n',
     '            v = float(np.real(M[i, j]))\n'
     '            a.text(j, i, f"{0.0 if abs(v) < 5e-4 else v:.3f}", ha="center", va="center", fontsize=9,\n'
     '                   color="white" if v > 0.18 else "black")\n'),
    ("09-quantum-switch", 'plt.suptitle("Joint (control ⊗ target) output for input |0⟩, both channels completely depolarizing")',
     'plt.suptitle("Joint (control ⊗ target) output for input |0⟩,\\nboth channels completely depolarizing")'),
    # Lab 11: room around the nodes so no circle is cut and the title clears the top row
    ("11-quantum-causal-inference", "fig, ax = plt.subplots(figsize=(6, 2.6))", "fig, ax = plt.subplots(figsize=(6, 3.1))"),
    ("11-quantum-causal-inference", 'ax.set_title("Bell scenario as a causal graph (Λ hidden)"); ax.axis("off")\n',
     'ax.set_title("Bell scenario as a causal graph (Λ hidden)"); ax.axis("off")\n'
     'ax.set_xlim(-0.35, 3.35); ax.set_ylim(-0.3, 1.3)\n'),
]

LABVIZ = {"05-qubit-bloch": "tweak, second_slider, camera", "06-entanglement-bell": "tweak", "07-noise-channels": "tweak, camera",
          "09-quantum-switch": "tweak, camera", "11-quantum-causal-inference": "tweak, camera"}  # names used from qcai.labviz


def main():
    done = 0
    for nb in NBS:
        f = BOOK / "labs" / f"{nb}.ipynb"
        d = json.loads(f.read_text(encoding="utf-8"))
        for c in d["cells"]:
            src = "".join(c["source"])
            if c["cell_type"] == "code":
                new = "from qcai.viz import show, frame" + (rf"\nfrom qcai.labviz import {LABVIZ[nb]}" if nb in LABVIZ else "")
                src = re.sub(r"^from qcai\.viz import show(, frame)?(\nfrom qcai\.labviz import .*)?$", new, src, flags=re.M)
                for (book, marker), (split, tail) in TAILS.items():
                    if book == nb and marker in src and "show(" in src:
                        assert tail.startswith(split), (nb, marker)
                        cut = src.index(split) if split else 0
                        src = src[:cut] + tail
                        done += 1
                for book, a, b in STATIC:
                    if book == nb and b not in src:
                        src = src.replace(a, b)
            if c["cell_type"] == "markdown":
                for a, b in PROSE.get(nb, []):
                    src = src.replace(a, b)
            lines = src.split("\n")
            c["source"] = [ln + "\n" for ln in lines[:-1]] + [lines[-1]]
        f.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    assert done == len(TAILS), (done, len(TAILS))
    print(f"rewrote {done} figure cells")


if __name__ == "__main__":
    main()
