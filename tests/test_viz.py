import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import plotly.graph_objects as go
from qcai.viz import show


def test_show_passes_frames_and_waits_for_plotly():
    fig = go.Figure(go.Scatter(x=[0, 1], y=[0, 1]), frames=[go.Frame(data=[go.Scatter(y=[1, 0])], name="f1")])
    h = show(fig).data
    assert "frames: spec.frames" in h and '"name": "f1"' in h and "window.Plotly" in h
    assert "fig.show" not in h
