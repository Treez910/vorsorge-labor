"""Vorsorge-Labor: Altersvorsorge mit echten Marktdaten verstehen.

Kein Finanzrat, keine Kaufempfehlungen. Die App prüft, ob ein Wertpapier
zu einem Risikoprofil passt, und erklärt, warum.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

import base64
from pathlib import Path

import tempfile

# Logo und App-Symbol stecken direkt im Code, damit die App ohne Extra-Dateien läuft
LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48" xmlns:c2pa="http://c2pa.org/manifest">
  <style>
    .ring { stroke-dasharray: 120; stroke-dashoffset: 120; animation: zeichnen 0.9s ease-out forwards; }
    .linie { stroke-dasharray: 53; stroke-dashoffset: 53; animation: zeichnen 0.8s ease-in-out 0.5s forwards; }
    .punkt { transform-origin: 38.5px 9.5px; transform: scale(0); animation: auftauchen 0.35s ease-out 1.25s forwards; }
    @keyframes zeichnen { to { stroke-dashoffset: 0; } }
    @keyframes auftauchen { 60% { transform: scale(1.4); } to { transform: scale(1); } }
    @media (prefers-reduced-motion: reduce) {
      .ring, .linie { animation: none; stroke-dashoffset: 0; }
      .punkt { animation: none; transform: none; }
    }
  </style>
  <circle class="ring" cx="24" cy="24" r="19" fill="none" stroke="#1B1B18" stroke-width="2.2"
          transform="rotate(-90 24 24)"/>
  <path class="linie" d="M10.5 15 C 15 23, 18.5 33.5, 22.5 33.5 C 27 33.5, 31 21, 38.5 9.5" fill="none" stroke="#F7F6F2" stroke-width="8" stroke-linecap="round"/>
  <path class="linie" d="M10.5 15 C 15 23, 18.5 33.5, 22.5 33.5 C 27 33.5, 31 21, 38.5 9.5" fill="none" stroke="#1F4E5F" stroke-width="3.4" stroke-linecap="round"/>
  <circle class="punkt" cx="38.5" cy="9.5" r="3.1" fill="#1F4E5F"/>
<metadata><c2pa:manifest>AAAWgmp1bWIAAAAeanVtZGMycGEAEQAQgAAAqgA4m3EDYzJwYQAAABZcanVtYgAAAEdqdW1kYzJtYQARABCAAACqADibcQN1cm46YzJwYTozOTI5MGUwNy1mM2QwLTQ5YTktOTgzZi0zZTdjOTdmOWNiOGUAAAADl2p1bWIAAAApanVtZGMyYXMAEQAQgAAAqgA4m3EDYzJwYS5hc3NlcnRpb25zAAAAALxqdW1iAAAARGp1bWRjYm9yABEAEIAAAKoAOJtxE2MycGEuaW5ncmVkaWVudC52MwAAAAAYYzJzaDCJQ8471eE7rcAEvEQVUe8AAABwY2JvcqNpZGM6Zm9ybWF0bWltYWdlL3N2Zyt4bWxqaW5zdGFuY2VJRHgseG1wOmlpZDplMWRlYzg3Zi1jMWQxLTRhNGItYTAxMC02MWNkOGExODY0NzFscmVsYXRpb25zaGlwaHBhcmVudE9mAAAB4mp1bWIAAABBanVtZGNib3IAEQAQgAAAqgA4m3ETYzJwYS5hY3Rpb25zLnYyAAAAABhjMnNoVOUxe2d9A13k+jSjX/tC1wAAAZljYm9yomdhY3Rpb25zgqJmYWN0aW9ua2MycGEub3BlbmVkanBhcmFtZXRlcnOha2luZ3JlZGllbnRzgaJjdXJseC1zZWxmI2p1bWJmPWMycGEuYXNzZXJ0aW9ucy9jMnBhLmluZ3JlZGllbnQudjNkaGFzaFggbv+KT+9UcwYpChfyTxeo6BIqKwQleCfMBeo15xHRYiOkZmFjdGlvbngdY29tLmFudGhyb3BpYy5jbGF1ZGUucHJvdmlkZWRqcGFyYW1ldGVyc6F4H2NvbS5hbnRocm9waWMub3JpZ2luLWNvbmZpZGVuY2VndW5rbm93bmtkZXNjcmlwdGlvbnhmQ2xhdWRlIHByb3ZpZGVkIHRoaXMgZmlsZSBhdCB0aGUgcmVxdWVzdCBvZiBhIHVzZXIgYW5kIG1heSBoYXZlIGNyZWF0ZWQgb3IgbW9kaWZpZWQgdGhlIGZpbGUgY29udGVudHMubXNvZnR3YXJlQWdlbnShZG5hbWVmQ2xhdWRlcmFsbEFjdGlvbnNJbmNsdWRlZPUAAADIanVtYgAAAEBqdW1kY2JvcgARABCAAACqADibcRNjMnBhLmhhc2guZGF0YQAAAAAYYzJzaGHmXzwKE6IVV0NaJhlOJ50AAACAY2JvcqVjYWxnZnNoYTI1NmNwYWRMAAAAAAAAAAAAAAAAZGhhc2hYIKoX48uTs3zEiMVb+HtNspPRwGh+ZVUsLtfTxODaituVZG5hbWVuanVtYmYgbWFuaWZlc3RqZXhjbHVzaW9uc4GiZXN0YXJ0GQVGZmxlbmd0aBkeBAAAAj5qdW1iAAAAJ2p1bWRjMmNsABEAEIAAAKoAOJtxA2MycGEuY2xhaW0udjIAAAACD2Nib3KlY2FsZ2ZzaGEyNTZpc2lnbmF0dXJleE1zZWxmI2p1bWJmPS9jMnBhL3VybjpjMnBhOjM5MjkwZTA3LWYzZDAtNDlhOS05ODNmLTNlN2M5N2Y5Y2I4ZS9jMnBhLnNpZ25hdHVyZWppbnN0YW5jZUlEeCx4bXA6aWlkOjU2NGFhNmZmLTU5MDktNGQ0MC05YWVmLWM0MDIzMDE2OGQ0ZnJjcmVhdGVkX2Fzc2VydGlvbnODomN1cmx4LXNlbGYjanVtYmY9YzJwYS5hc3NlcnRpb25zL2MycGEuaW5ncmVkaWVudC52M2RoYXNoWCBu/4pP71RzBikKF/JPF6joEiorBCV4J8wF6jXnEdFiI6JjdXJseCpzZWxmI2p1bWJmPWMycGEuYXNzZXJ0aW9ucy9jMnBhLmFjdGlvbnMudjJkaGFzaFgg+8mQv66TrKJH0cyk2jg7Jp427OALmDSTbQmVrrquAb+iY3VybHgpc2VsZiNqdW1iZj1jMnBhLmFzc2VydGlvbnMvYzJwYS5oYXNoLmRhdGFkaGFzaFggWJ4aw1D+OOl8jtqPvcQ94v7bsl6K88F/L3yApJu+BG10Y2xhaW1fZ2VuZXJhdG9yX2luZm+jZG5hbWVvQW50aHJvcGljIEZpbGVzZ3ZlcnNpb25lMS4wLjBrc3BlY1ZlcnNpb25lMi40LjAAABA4anVtYgAAAChqdW1kYzJjcwARABCAAACqADibcQNjMnBhLnNpZ25hdHVyZQAAABAIY2JvctKEWQISogEmGCFZAgowggIGMIIBjaADAgECAhRA5aAK7sI50L64g/oGQgU9Z1UTADAKBggqhkjOPQQDAzBJMRcwFQYDVQQKEw5BbnRocm9waWMsIFBCQzEuMCwGA1UEAxMlQW50aHJvcGljIENvbnRlbnQgQ3JlZGVudGlhbHMgUm9vdCBDQTAeFw0yNjA4MDcxODQzNTZaFw0yODA4MDYxOTQzNTZaMEQxFzAVBgNVBAoTDkFudGhyb3BpYywgUEJDMSkwJwYDVQQDEyBBbnRocm9waWMgQ2xhdWRlIENvbnRlbnQgU2lnbmluZzBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IABJh6CmvLUBgFFNU0vUKlOVtE6djd17L5SuwX0LemFisBM3dkd/3cyjxFA3Qo5S46fX0/ihY0VZ7mfb9KF703t5OjWDBWMA4GA1UdDwEB/wQEAwIHgDAVBgNVHSUEDjAMBgorBgEEAYPoXgIBMAwGA1UdEwEB/wQCMAAwHwYDVR0jBBgwFoAUzlHiBIFOZFsj+OPEz5o+nMHXXMIwCgYIKoZIzj0EAwMDZwAwZAIwMXMdFJ4BetLLVY7ORuE9noqbbAZOZn/aArXyTwFAZfKrPzxF2vPoJNf1+UCdg1XGAjBwX1zd9WGqYkqmL5SFqw1QySjr1zJfpJM9+1rdDwSPLMOPOjKuiXjoU/pUUeG9RwmhY3BhZFkNngAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPZYQFO929xtEk1vlU25xP2HT1ny+5xilu/InFkTceTavY32wqQ74ijazYi23N7rxhIOXdKjsuNKGW/MMm+UyoSW7nQ=</c2pa:manifest></metadata></svg>"""
ICON_PNG_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAIAAABMXPacAAAWfmNhQlgAABZ+anVtYgAAAB5qdW1kYzJwYQARABCAAACqADibcQNjMnBhAAAAFlhqdW1iAAAAR2p1bWRjMm1hABEAEIAAAKoAOJtxA3VybjpjMnBhOjliZDMyYTIzLTUyYjItNDYyMS04NTU5LTVlNjQ0NWNkYTI4OQAAAAOTanVtYgAAAClqdW1kYzJhcwARABCAAACqADibcQNjMnBhLmFzc2VydGlvbnMAAAAAuGp1bWIAAABEanVtZGNib3IAEQAQgAAAqgA4m3ETYzJwYS5pbmdyZWRpZW50LnYzAAAAABhjMnNoGwzFy3Mt3JRcXpebZZyIOwAAAGxjYm9yo2lkYzpmb3JtYXRpaW1hZ2UvcG5namluc3RhbmNlSUR4LHhtcDppaWQ6OTcxM2UyNzctYjllMi00NTFkLTg4NjgtZjVmNmQwMGVjMGM3bHJlbGF0aW9uc2hpcGhwYXJlbnRPZgAAAeJqdW1iAAAAQWp1bWRjYm9yABEAEIAAAKoAOJtxE2MycGEuYWN0aW9ucy52MgAAAAAYYzJzaLczjoiBb0YWkjgjf91Sl50AAAGZY2JvcqJnYWN0aW9uc4KiZmFjdGlvbmtjMnBhLm9wZW5lZGpwYXJhbWV0ZXJzoWtpbmdyZWRpZW50c4GiY3VybHgtc2VsZiNqdW1iZj1jMnBhLmFzc2VydGlvbnMvYzJwYS5pbmdyZWRpZW50LnYzZGhhc2hYII10MFQrX9ErOLhZLRLRNN9IQnB29f2CMgJPiTZ2zFXhpGZhY3Rpb254HWNvbS5hbnRocm9waWMuY2xhdWRlLnByb3ZpZGVkanBhcmFtZXRlcnOheB9jb20uYW50aHJvcGljLm9yaWdpbi1jb25maWRlbmNlZ3Vua25vd25rZGVzY3JpcHRpb254ZkNsYXVkZSBwcm92aWRlZCB0aGlzIGZpbGUgYXQgdGhlIHJlcXVlc3Qgb2YgYSB1c2VyIGFuZCBtYXkgaGF2ZSBjcmVhdGVkIG9yIG1vZGlmaWVkIHRoZSBmaWxlIGNvbnRlbnRzLm1zb2Z0d2FyZUFnZW50oWRuYW1lZkNsYXVkZXJhbGxBY3Rpb25zSW5jbHVkZWT1AAAAyGp1bWIAAABAanVtZGNib3IAEQAQgAAAqgA4m3ETYzJwYS5oYXNoLmRhdGEAAAAAGGMyc2g8fckkJeiXfVd3N4I35WxjAAAAgGNib3KlY2FsZ2ZzaGEyNTZjcGFkTQAAAAAAAAAAAAAAAABkaGFzaFggVoaXz0ImqAcwuu+qwiD9HMzeapBcbkLmv7vNBejFN2JkbmFtZW5qdW1iZiBtYW5pZmVzdGpleGNsdXNpb25zgaJlc3RhcnQYIWZsZW5ndGgZFooAAAI+anVtYgAAACdqdW1kYzJjbAARABCAAACqADibcQNjMnBhLmNsYWltLnYyAAAAAg9jYm9ypWNhbGdmc2hhMjU2aXNpZ25hdHVyZXhNc2VsZiNqdW1iZj0vYzJwYS91cm46YzJwYTo5YmQzMmEyMy01MmIyLTQ2MjEtODU1OS01ZTY0NDVjZGEyODkvYzJwYS5zaWduYXR1cmVqaW5zdGFuY2VJRHgseG1wOmlpZDozMGYxNzk5Ny00MGY1LTQwZjctYjMyMC1mNWY2YzY2MDJkODFyY3JlYXRlZF9hc3NlcnRpb25zg6JjdXJseC1zZWxmI2p1bWJmPWMycGEuYXNzZXJ0aW9ucy9jMnBhLmluZ3JlZGllbnQudjNkaGFzaFggjXQwVCtf0Ss4uFktEtE030hCcHb1/YIyAk+JNnbMVeGiY3VybHgqc2VsZiNqdW1iZj1jMnBhLmFzc2VydGlvbnMvYzJwYS5hY3Rpb25zLnYyZGhhc2hYIFLYdEMcegGldEN0i/oDAMpwzMaChFerLDN3fH0Nf+ofomN1cmx4KXNlbGYjanVtYmY9YzJwYS5hc3NlcnRpb25zL2MycGEuaGFzaC5kYXRhZGhhc2hYIO1qXYqbI9teYp/FHdt/3DRw2J9rihYlDe94dkzaQybJdGNsYWltX2dlbmVyYXRvcl9pbmZvo2RuYW1lb0FudGhyb3BpYyBGaWxlc2d2ZXJzaW9uZTEuMC4wa3NwZWNWZXJzaW9uZTIuNC4wAAAQOGp1bWIAAAAoanVtZGMyY3MAEQAQgAAAqgA4m3EDYzJwYS5zaWduYXR1cmUAAAAQCGNib3LShFkCEqIBJhghWQIKMIICBjCCAY2gAwIBAgIUQOWgCu7COdC+uIP6BkIFPWdVEwAwCgYIKoZIzj0EAwMwSTEXMBUGA1UEChMOQW50aHJvcGljLCBQQkMxLjAsBgNVBAMTJUFudGhyb3BpYyBDb250ZW50IENyZWRlbnRpYWxzIFJvb3QgQ0EwHhcNMjYwODA3MTg0MzU2WhcNMjgwODA2MTk0MzU2WjBEMRcwFQYDVQQKEw5BbnRocm9waWMsIFBCQzEpMCcGA1UEAxMgQW50aHJvcGljIENsYXVkZSBDb250ZW50IFNpZ25pbmcwWTATBgcqhkjOPQIBBggqhkjOPQMBBwNCAASYegpry1AYBRTVNL1CpTlbROnY3dey+UrsF9C3phYrATN3ZHf93Mo8RQN0KOUuOn19P4oWNFWe5n2/She9N7eTo1gwVjAOBgNVHQ8BAf8EBAMCB4AwFQYDVR0lBA4wDAYKKwYBBAGD6F4CATAMBgNVHRMBAf8EAjAAMB8GA1UdIwQYMBaAFM5R4gSBTmRbI/jjxM+aPpzB11zCMAoGCCqGSM49BAMDA2cAMGQCMDFzHRSeAXrSy1WOzkbhPZ6Km2wGTmZ/2gK18k8BQGXyqz88Rdrz6CTX9flAnYNVxgIwcF9c3fVhqmJKpi+UhasNUMko69cyX6STPfta3Q8EjyzDjzoyrol46FP6VFHhvUcJoWNwYWRZDZ4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA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"
ASSETS = Path(tempfile.gettempdir()) / "vorsorge_labor_assets"
ASSETS.mkdir(exist_ok=True)
(ASSETS / "logo.svg").write_text(LOGO_SVG, encoding="utf-8")
(ASSETS / "icon.png").write_bytes(base64.b64decode(ICON_PNG_BASE64))
st.set_page_config(page_title="Vorsorge-Labor", page_icon=str(ASSETS / "icon.png"), layout="wide")
st.logo(str(ASSETS / "logo.svg"), size="large")
# Für die Startseite: das animierte Logo als eingebettetes Bild
LOGO_INLINE = ("<img alt='' width='76' height='76' src='data:image/svg+xml;base64,"
               + base64.b64encode(LOGO_SVG.encode()).decode() + "'>")

# --- Farben & Typografie ----------------------------------------------------
TINTE, GEDAEMPFT, LINIE = "#1B1B18", "#6B6A63", "#E2DFD6"
AKZENT, GRUEN, GELB, ROT = "#1F4E5F", "#2F7D4F", "#B7791F", "#B23A3A"
VERGLEICH = "#9A988F"

st.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&family=IBM+Plex+Sans:wght@400;500;600&display=swap');
html, body, .stApp, .stMarkdown, p, li, label, input, button, textarea, select,
[data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
  font-family: 'IBM Plex Sans', system-ui, sans-serif !important;
}
h1, h2, h3, .serif { font-family: 'Source Serif 4', Georgia, serif !important;
  font-weight: 600 !important; letter-spacing: -0.01em; color: #1B1B18; }
h1 { font-size: 2.5rem !important; line-height: 1.15 !important; }
.block-container { padding-top: 4.5rem; max-width: 1150px; }
.kicker { text-transform: uppercase; letter-spacing: .08em; font-size: .75rem;
  color: #6B6A63; font-weight: 600; margin-bottom: .2rem; }
.lead { font-size: 1.12rem; color: #3A3A35; line-height: 1.6; max-width: 46rem; }
.karte { background: #FFFFFF; border: 1px solid #E2DFD6; border-radius: 6px;
  padding: 1.1rem 1.3rem; height: 100%; }
.karte h3 { margin: 0 0 .3rem 0; font-size: 1.2rem; }
.karte p { margin: 0; color: #4A4A44; font-size: .95rem; line-height: 1.5; }
.status { font-size: .75rem; color: #6B6A63; margin-top: .6rem; }
.ampel { display: grid; grid-template-columns: 14px 1.2fr 1fr 2.4fr; gap: .4rem 1rem;
  align-items: baseline; padding: .75rem 0; border-bottom: 1px solid #E2DFD6; }
.punkt { width: 11px; height: 11px; border-radius: 50%; display: inline-block; }
.ampel .krit { font-weight: 600; } .ampel .wert { font-variant-numeric: tabular-nums; }
.ampel .warum { color: #4A4A44; font-size: .93rem; }
.urteil { border-left: 4px solid; padding: .9rem 1.2rem; background: #FFFFFF;
  border-radius: 0 6px 6px 0; margin: .5rem 0 1rem 0; }
.urteil h3 { margin: 0 0 .25rem 0; } .urteil p { margin: 0; color: #3A3A35; }
.hinweis { font-size: .82rem; color: #6B6A63; border-top: 1px solid #E2DFD6;
  margin-top: 3rem; padding-top: .8rem; }
[data-testid="stMetricValue"] { font-variant-numeric: tabular-nums; }

/* ---------- Bewegung ---------- */
@keyframes einblenden { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
@keyframes wachsen { from { transform: scaleX(0); } to { transform: scaleX(1); } }
.block-container [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"],
.block-container [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"],
.block-container [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"] {
  animation: einblenden .55s cubic-bezier(.2,.7,.2,1) both;
}
.block-container [data-testid="stVerticalBlock"] > *:nth-child(2) { animation-delay: .04s; }
.block-container [data-testid="stVerticalBlock"] > *:nth-child(3) { animation-delay: .08s; }
.block-container [data-testid="stVerticalBlock"] > *:nth-child(4) { animation-delay: .12s; }
.block-container [data-testid="stVerticalBlock"] > *:nth-child(5) { animation-delay: .16s; }
.block-container [data-testid="stVerticalBlock"] > *:nth-child(6) { animation-delay: .20s; }
.block-container [data-testid="stVerticalBlock"] > *:nth-child(7) { animation-delay: .24s; }
.block-container [data-testid="stVerticalBlock"] > *:nth-child(n+8) { animation-delay: .28s; }
.ampel { animation: einblenden .45s ease-out both; }
.ampel:nth-child(2) { animation-delay: .06s; } .ampel:nth-child(3) { animation-delay: .12s; }
.ampel:nth-child(4) { animation-delay: .18s; } .ampel:nth-child(5) { animation-delay: .24s; }
.ampel:nth-child(n+6) { animation-delay: .30s; }
.balken { transform-origin: left center; animation: wachsen .8s cubic-bezier(.2,.7,.2,1) .2s both; }
.urteil { transition: box-shadow .25s ease; }
.urteil:hover { box-shadow: 0 2px 14px rgba(27,27,24,.06); }
[class*="st-key-karte_"] { position: relative; background: #FFFFFF; border-radius: 6px !important;
  border-color: #E2DFD6 !important; height: 100%;
  transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease; }
[class*="st-key-karte_"]:hover { transform: translateY(-3px); border-color: #1F4E5F !important;
  box-shadow: 0 6px 18px rgba(31,78,95,.10); }
[class*="st-key-karte_"]:active { transform: translateY(-1px) scale(.99); }
/* Innerhalb der Karte keine eigene Animation: sonst bildet jedes Element einen eigenen
   Rahmen, und der über die Karte gespannte Link greift nicht */
[class*="st-key-karte_"] [data-testid="stElementContainer"] { position: static !important; animation: none !important; }
[class*="st-key-karte_"] [data-testid="stPageLink"] a::after { content: ""; position: absolute; inset: 0; z-index: 1; }
[class*="st-key-karte_"] [data-testid="stPageLink"] a { padding-left: 0; }
[class*="st-key-karte_"] [data-testid="stPageLink"] p { color: #1F4E5F; font-size: .85rem; font-weight: 600;
  transition: letter-spacing .2s ease; }
[class*="st-key-karte_"]:hover [data-testid="stPageLink"] p { letter-spacing: .03em; }
.nummer { font-size: .75rem; color: #6B6A63; letter-spacing: .08em; font-weight: 600; }
.karten-titel { margin: .2rem 0 .3rem 0 !important; font-size: 1.2rem !important; }
.karten-text { margin: 0; color: #4A4A44; font-size: .95rem; line-height: 1.5; }
button, [data-testid="stBaseButton-pills"], [data-testid="stBaseButton-pillsActive"] {
  transition: transform .12s ease, background-color .2s ease !important; }
button:active { transform: scale(.97); }
.held { display: flex; align-items: center; gap: 1.1rem; margin-bottom: .4rem; }
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; }
}
@media (max-width: 700px) {
  .ampel { grid-template-columns: 14px 1fr; }
  .ampel .wert, .ampel .warum { grid-column: 2; }
}
</style>
""")

# --- Risikoprofile ----------------------------------------------------------
PROFILE = {
    "vorsichtig": {"titel": "Vorsichtig", "vol": 12, "dd": 25, "erholung": 3,
                   "text": "Stabilität ist dir wichtiger als hohe Rendite. Größere Verluste würden "
                           "dich stark belasten, oder du brauchst das Geld in wenigen Jahren."},
    "ausgewogen": {"titel": "Ausgewogen", "vol": 18, "dd": 40, "erholung": 6,
                   "text": "Du willst langfristig Vermögen aufbauen und hältst zwischenzeitliche "
                           "Verluste aus, solange sie nicht extrem werden."},
    "mutig": {"titel": "Mutig", "vol": 30, "dd": 60, "erholung": 10,
              "text": "Du hast viel Zeit und hältst auch heftige Crashs aus, ohne zu verkaufen. "
                      "Dafür nimmst du große Schwankungen in Kauf."},
}
REAKTIONEN = ["Ich verkaufe, bevor es noch weiter fällt", "Ich halte, schlafe aber schlecht",
              "Ich halte gelassen, das gehört dazu", "Ich kaufe nach, weil es jetzt günstiger ist"]
HORIZONT_JAHRE = {"Weniger als 3 Jahre": 2, "3 bis 10 Jahre": 7,
                  "10 bis 20 Jahre": 15, "Mehr als 20 Jahre": 30}


def aktuelles_profil():
    if "profil" not in st.session_state:
        p = st.query_params.get("profil")
        h = st.query_params.get("horizont")
        if p in PROFILE:
            st.session_state["profil"] = p
            st.session_state["horizont"] = int(h) if h and h.isdigit() else 15
    if st.session_state.get("profil"):
        st.query_params["profil"] = st.session_state["profil"]
        st.query_params["horizont"] = str(st.session_state.get("horizont", 15))
    return st.session_state.get("profil"), st.session_state.get("horizont", 15)


def kopf(kicker, titel, lead=""):
    st.html(f"<div class='kicker'>{kicker}</div><h1 style='margin:0 0 .6rem 0'>{titel}</h1>"
            + (f"<p class='lead'>{lead}</p>" if lead else ""))


TYPEN = {"EQUITY": "Aktie", "ETF": "ETF", "INDEX": "Index", "MUTUALFUND": "Fonds",
         "CRYPTOCURRENCY": "Kryptowährung"}


def hinweis():
    st.html("<div class='hinweis'>Das Vorsorge-Labor ist ein Lernprojekt und keine Anlageberatung. "
            "Es gibt keine Kauf- oder Verkaufsempfehlungen. Vergangene Entwicklungen sind keine "
            "Garantie für die Zukunft. Kursdaten: Yahoo Finance, ohne Gewähr.</div>")


def layout(fig, hoehe=380):
    fig.update_layout(template="plotly_white", height=hoehe, margin=dict(l=0, r=0, t=10, b=0),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(family="IBM Plex Sans, sans-serif", color=TINTE, size=13),
                      legend=dict(orientation="h", y=1.02, yanchor="bottom", x=0),
                      hovermode="x unified", separators=",.")
    fig.update_xaxes(showgrid=False, linecolor=LINIE)
    fig.update_yaxes(gridcolor="#ECEAE3", zeroline=False)
    return fig


def de(x, n=1):
    return f"{x:,.{n}f}".replace(",", "X").replace(".", ",").replace("X", ".").replace("-", "−")


# --- Daten ------------------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def kurse(kuerzel: str) -> pd.DataFrame:
    h = yf.Ticker(kuerzel).history(period="max", auto_adjust=True)
    if h is None or h.empty:
        raise ValueError("keine Kursdaten gefunden")
    if h.index.tz is not None:
        h.index = h.index.tz_localize(None)
    return h[h["Close"] > 0]


@st.cache_data(ttl=86400, show_spinner=False)
def stammdaten(kuerzel: str) -> dict:
    try:
        i = yf.Ticker(kuerzel).info or {}
    except Exception:
        i = {}
    return {"name": i.get("longName") or i.get("shortName") or kuerzel,
            "typ": (i.get("quoteType") or "").upper(),
            "waehrung": i.get("currency") or ""}


def kennzahlen(h: pd.DataFrame) -> dict:
    c = h["Close"]
    jahre = (c.index[-1] - c.index[0]).days / 365.25
    tages = c.pct_change().dropna()
    spitze = c.cummax()
    unterwasser = c / spitze - 1

    # längste Erholungszeit: vom alten Hoch bis es wieder erreicht wurde (oder bis heute)
    laengste, laufend, start = 0.0, False, None
    for zeit, wert in unterwasser.items():
        if wert < 0 and start is None:
            start = zeit
        elif wert >= 0 and start is not None:
            laengste = max(laengste, (zeit - start).days / 365.25)
            start = None
    if start is not None:
        dauer = (c.index[-1] - start).days / 365.25
        laufend = dauer >= laengste
        laengste = max(laengste, dauer)

    def cagr(n):
        if jahre < n:
            return None
        alt = c[c.index <= c.index[-1] - pd.DateOffset(years=n)].iloc[-1]
        return ((c.iloc[-1] / alt) ** (1 / n) - 1) * 100

    monat = c.resample("ME").last()
    zehn = (monat / monat.shift(120) - 1).dropna()
    jahr = c.resample("YE").last().pct_change().dropna() * 100
    tief = unterwasser.idxmin()
    return {
        "jahre": jahre, "start": c.index[0],
        "r5": cagr(5), "r10": cagr(10), "r20": cagr(20),
        "vol": tages.std() * np.sqrt(252) * 100,
        "dd": unterwasser.min() * 100, "dd_datum": tief,
        "erholung": laengste, "erholung_laeuft": laufend,
        "zehn_plus": (zehn > 0).mean() * 100 if len(zehn) else None,
        "zehn_schlecht": ((1 + zehn.min()) ** 0.1 - 1) * 100 if len(zehn) else None,
        "schlechtestes_jahr": jahr.min() if len(jahr) else None,
        "schlechtestes_jahr_wann": jahr.idxmin().year if len(jahr) else None,
        "unterwasser": unterwasser,
    }


def bewerten(k: dict, typ: str, profil: str, horizont: int):
    g = PROFILE[profil]
    zeilen = []

    def stufe(wert, grenze):
        return "gruen" if wert <= grenze else ("gelb" if wert <= grenze * 1.25 else "rot")

    s = stufe(k["vol"], g["vol"])
    zeilen.append((s, "Schwankung", f"{de(k['vol'])} % pro Jahr",
                   f"Für dein Profil sind bis etwa {g['vol']} % angemessen." if s == "gruen" else
                   f"Deutlich unruhiger als die rund {g['vol']} %, die zu deinem Profil passen."))

    s = stufe(-k["dd"], g["dd"])
    zeilen.append((s, "Größter Absturz", f"{de(k['dd'], 0)} % ({k['dd_datum']:%Y})",
                   f"Liegt im Rahmen. Dein Profil verträgt Rückgänge bis etwa {g['dd']} %." if s == "gruen" else
                   f"Aus 10.000 € wären zwischenzeitlich {de(10000 * (1 + k['dd'] / 100), 0)} € "
                   f"geworden. Dein Profil verträgt etwa −{g['dd']} %."))

    grenze = min(g["erholung"], max(horizont / 2, 1))
    s = stufe(k["erholung"], grenze)
    laeuft = " (läuft noch)" if k["erholung_laeuft"] else ""
    zeilen.append((s, "Erholungszeit", f"{de(k['erholung'])} Jahre{laeuft}",
                   "So lange lag der Kurs im schlimmsten Fall unter seinem alten Höchststand. "
                   + ("Das passt zu deiner Anlagedauer." if s == "gruen" else
                      f"Bei {horizont} Jahren Anlagedauer ist das ein spürbarer Teil davon.")))

    if typ == "PORTFOLIO":
        zeilen.append(("gruen", "Streuung", "Mischung",
                       "Mehrere Anlageklassen, die sich in Krisen unterschiedlich verhalten."))
    elif typ in ("ETF", "INDEX", "MUTUALFUND"):
        zeilen.append(("gruen", "Streuung", "Fonds/Index",
                       "Viele Unternehmen in einem Produkt. Pleiten einzelner Firmen fallen kaum ins Gewicht."))
    elif typ == "CRYPTOCURRENCY":
        zeilen.append(("rot", "Streuung", "Kryptowährung",
                       "Kein Unternehmen, keine Erträge. Für die Altersvorsorge höchstens eine sehr kleine Beimischung."))
    else:
        zeilen.append(("rot", "Streuung", "Einzelaktie",
                       "Klumpenrisiko: Das Schicksal hängt an einer Firma. Auch große Namen können "
                       "dauerhaft abstürzen. Für die Vorsorge höchstens als Beimischung."))

    drin = [name for name, beginn in KRISEN if k["start"] <= pd.Timestamp(beginn)]
    fehlt = [name for name, beginn in KRISEN if k["start"] > pd.Timestamp(beginn)]
    krisen_text = ("Enthalten: " + ", ".join(drin) + "." if drin else "") + (
        " Nicht enthalten: " + ", ".join(fehlt) + "." if fehlt else "")
    if k["jahre"] >= 7 and "Finanzkrise 2008" in drin:
        zeilen.append(("gruen", "Datenlage", f"{de(k['jahre'], 0)} Jahre Historie",
                       krisen_text.strip()))
    elif k["jahre"] >= 7:
        zeilen.append(("gelb", "Datenlage", f"{de(k['jahre'], 0)} Jahre Historie",
                       krisen_text.strip() + " Ohne die Finanzkrise 2008 wirkt das Risiko "
                       "vermutlich harmloser, als es ist."))
    else:
        zeilen.append(("rot", "Datenlage", f"{de(k['jahre'], 1)} Jahre Historie",
                       "Zu kurz, um das Risiko verlässlich einzuschätzen."))

    if k["zehn_plus"] is not None:
        s = "gruen" if k["zehn_plus"] >= 90 else ("gelb" if k["zehn_plus"] >= 70 else "rot")
        zeilen.append((s, "Langfristig im Plus", f"{de(k['zehn_plus'], 0)} % der 10-Jahres-Zeiträume",
                       f"Im schlechtesten 10-Jahres-Zeitraum: {de(k['zehn_schlecht'])} % pro Jahr."))

    risiko_rot = any(z[0] == "rot" for z in zeilen[:3])
    if zeilen[4][0] == "rot":
        urteil = ("gelb", "Zu wenig Daten für ein Urteil",
                  "Die Kurshistorie ist zu kurz. Ohne erlebte Krisen lässt sich das Risiko nicht seriös einschätzen.")
    elif risiko_rot:
        extra = (" Als Teil einer Mischung mit sicheren Anlagen kann ein breiter Fonds trotzdem "
                 "passen, weil die Mischung weniger stark fällt." if typ in ("ETF", "INDEX", "MUTUALFUND") else "")
        urteil = ("rot", "Passt eher nicht zu deinem Profil",
                  "Mindestens ein zentrales Risikomerkmal liegt klar über dem, was zu deinem Profil passt." + extra)
    elif zeilen[3][0] == "rot":
        urteil = ("gelb", "Passt höchstens als kleine Beimischung",
                  "Die Schwankungen wären für dein Profil tragbar, aber es fehlt die Streuung. "
                  "Als Basis einer Altersvorsorge eignen sich breit gestreute Fonds besser.")
    elif any(z[0] == "gelb" for z in zeilen):
        urteil = ("gelb", "Passt mit Abstrichen",
                  "Grundsätzlich im Rahmen deines Profils, aber einzelne Punkte solltest du dir genauer ansehen.")
    elif (profil != "vorsichtig" and horizont >= 10
          and k["vol"] < g["vol"] * 0.5 and -k["dd"] < g["dd"] * 0.5):
        urteil = ("blau", "Vorsichtiger als nötig",
                  "Bleibt weit unter den Grenzen deines Profils. Das ist sicher, kostet bei deiner "
                  "langen Anlagedauer aber wahrscheinlich viel Rendite.")
    else:
        urteil = ("gruen", "Passt zu deinem Profil",
                  "Schwankung, Abstürze und Erholungszeiten lagen bisher im Rahmen deines Profils.")
    return zeilen, urteil


FARBE = {"gruen": GRUEN, "gelb": GELB, "rot": ROT, "blau": AKZENT}
KRISEN = [("Dotcom-Crash 2000", "2000-03-01"), ("Finanzkrise 2008", "2007-10-01"),
          ("Corona 2020", "2020-02-01"), ("Zinswende 2022", "2022-01-01")]


# --- Seiten -----------------------------------------------------------------
def start():
    profil, horizont = aktuelles_profil()
    st.html(f"<div class='held'>{LOGO_INLINE}<div><div class='kicker'>Vorsorge-Labor</div>"
            "<div class='serif' style='font-size:1.05rem;color:#4A4A44'>Absturz, Erholung, Geduld.</div></div></div>"
            "<h1 style='margin:.4rem 0 .6rem 0'>Altersvorsorge verstehen, mit echten Zahlen.</h1>"
            "<p class='lead'>Wie riskant ist ein ETF oder eine Aktie wirklich? Wie lange dauert es, bis sich "
            "ein Crash erholt? Und was wird aus 50 € im Monat in 40 Jahren? Hier kannst du das selbst "
            "nachprüfen, ohne Verkaufsgespräch und ohne Versprechen.</p>")
    st.write("")
    if profil:
        p = PROFILE[profil]
        st.html(f"<div class='urteil' style='border-color:{AKZENT}'><h3>Dein Profil: {p['titel']}</h3>"
                f"<p>{p['text']} Anlagedauer: etwa {horizont} Jahre.</p></div>")
    else:
        st.html(f"<div class='urteil' style='border-color:{AKZENT}'><h3>Fang mit deinem Risikoprofil an</h3>"
                "<p>Fünf kurze Fragen. Danach bewerten alle Bereiche der App Wertpapiere "
                "passend zu dir.</p></div>")
        st.page_link(SEITE_PROFIL, label="Zum Risikoprofil →")
    st.write("")
    module = [
        ("profil", "Risikoprofil", "Wie viel Schwankung passt zu dir und deiner Anlagedauer?"),
        ("check", "Aktien- & ETF-Check", "Kürzel eingeben und sehen, ob ein Wertpapier zu deinem Profil passt, und warum."),
        ("portfolio", "Portfolio-Baukasten", "Aktien, Anleihen, Tagesgeld und Gold mischen und durch echte Crashs schicken."),
        ("sparplan", "Sparplan-Simulator", "Wie wäre ein Sparplan in jedem echten Startjahr gelaufen?"),
        ("kosten", "Kosten-Rechner", "Was 1 % Gebühr gegenüber 0,2 % über Jahrzehnte ausmacht."),
        ("inflation", "Inflation & Zinseszins", "Warum früh anfangen so viel bringt und was Geld an Wert verliert."),
    ]
    for reihe in range(0, len(module), 3):
        for nr, (spalte, (pfad, titel, text)) in enumerate(zip(st.columns(3), module[reihe:reihe + 3]),
                                                           start=reihe + 1):
            # Karte als Container mit Seiten-Link: schaltet ohne Neuladen um, die ganze
            # Karte ist per CSS klickbar (der Link wird über die Karte gespannt)
            with spalte.container(border=True, key=f"karte_{pfad}"):
                st.html(f"<div class='nummer'>{nr:02d}</div><h3 class='karten-titel'>{titel}</h3>"
                        f"<p class='karten-text'>{text}</p>")
                st.page_link(SEITEN[pfad], label="Öffnen →")
        st.write("")
    hinweis()


def risikoprofil():
    kopf("Schritt 1", "Dein Risikoprofil",
         "Es gibt keine richtigen oder falschen Antworten. Antworte so, wie du dich wirklich "
         "verhalten würdest, nicht so, wie du es gern würdest.")
    with st.form("profil_form"):
        horizont = st.radio("1. Wann brauchst du das Geld voraussichtlich?",
                            list(HORIZONT_JAHRE), index=3)
        reaktion = st.radio("2. Dein Depot ist in drei Monaten um 30 % gefallen. Was tust du?",
                            REAKTIONEN, index=None)
        verlust = st.radio("3. Welchen Verlust in einem schlechten Jahr hältst du aus, ohne zu verkaufen?",
                           ["Höchstens 10 %", "Etwa 20 %", "Etwa 35 %", "50 % und mehr"], index=None)
        erfahrung = st.radio("4. Hast du schon einmal einen größeren Verlust mit Geldanlagen erlebt?",
                             ["Nein", "Ja, und ich habe verkauft", "Ja, und ich habe durchgehalten"],
                             index=None)
        notgroschen = st.radio("5. Hast du einen Notgroschen von mindestens drei Monatsausgaben, "
                               "den du nicht anlegst?", ["Ja", "Nein"], index=None)
        fertig = st.form_submit_button("Profil berechnen", type="primary")

    if fertig:
        if None in (reaktion, verlust, erfahrung, notgroschen):
            st.warning("Bitte beantworte alle Fragen.")
            return
        punkte = (list(HORIZONT_JAHRE).index(horizont)
                  + REAKTIONEN.index(reaktion)
                  + ["Höchstens 10 %", "Etwa 20 %", "Etwa 35 %", "50 % und mehr"].index(verlust)
                  + {"Nein": 1, "Ja, und ich habe verkauft": 0, "Ja, und ich habe durchgehalten": 2}[erfahrung])
        profil = "vorsichtig" if punkte <= 4 else ("ausgewogen" if punkte <= 8 else "mutig")
        jahre = HORIZONT_JAHRE[horizont]
        if jahre <= 2 or verlust == "Höchstens 10 %" or reaktion.startswith("Ich verkaufe"):
            profil = "vorsichtig"
        st.session_state["profil"], st.session_state["horizont"] = profil, jahre
        st.query_params["profil"], st.query_params["horizont"] = profil, str(jahre)
        st.session_state["notgroschen"] = notgroschen

    profil, jahre = aktuelles_profil()
    if profil:
        p = PROFILE[profil]
        st.html(f"<div class='urteil' style='border-color:{AKZENT}'><h3>{p['titel']}</h3>"
                f"<p>{p['text']}</p></div>")
        a, b, c = st.columns(3)
        a.metric("Verträgliche Schwankung", f"bis ca. {p['vol']} % p. a.")
        b.metric("Verträglicher Absturz", f"bis ca. −{p['dd']} %")
        c.metric("Anlagedauer", f"ca. {jahre} Jahre")
        if jahre <= 2:
            st.info("Bei weniger als drei Jahren Anlagedauer sind Aktien generell kaum geeignet, "
                    "weil ein Crash nicht mehr ausgesessen werden kann.")
        if st.session_state.get("notgroschen") == "Nein":
            st.warning("Ohne Notgroschen musst du im Ernstfall vielleicht genau dann verkaufen, wenn die "
                       "Kurse unten sind. Viele bauen deshalb zuerst einen Notgroschen auf Tagesgeld auf.")
        st.caption("Tipp: Die Adresse dieser Seite enthält jetzt dein Profil. Speicher sie als "
                   "Lesezeichen, dann ist es beim nächsten Besuch wieder da.")
        st.page_link(SEITE_CHECK, label="Weiter zum Aktien- & ETF-Check →")
    hinweis()


BEISPIELE = {"MSCI World": "EUNL.DE", "S&P 500": "^GSPC", "DAX": "^GDAXI",
             "Apple": "AAPL", "Nvidia": "NVDA", "SAP": "SAP.DE", "Bitcoin": "BTC-USD"}


def check():
    profil, horizont = aktuelles_profil()
    kopf("Schritt 2", "Aktien- & ETF-Check",
         "Gib das Börsenkürzel ein, wie es bei Yahoo Finance heißt. Deutsche Werte enden meist "
         "auf <b>.DE</b>, zum Beispiel <b>SAP.DE</b>. Indizes beginnen mit <b>^</b>.")
    if not profil:
        st.info("Du hast noch kein Risikoprofil. Bis dahin rechnet der Check mit „Ausgewogen“ "
                "und 15 Jahren Anlagedauer.")
        profil, horizont = "ausgewogen", 15

    if "kuerzel" not in st.session_state:
        st.session_state["kuerzel"] = "EUNL.DE"
    def beispiel_gewaehlt():
        wahl = st.session_state.get("beispiel")
        if wahl:
            st.session_state["kuerzel"] = BEISPIELE[wahl]
    st.pills("Beispiele", list(BEISPIELE), key="beispiel", on_change=beispiel_gewaehlt)
    kuerzel = st.text_input("Börsenkürzel", key="kuerzel").strip().upper()
    if not kuerzel:
        return

    try:
        with st.spinner("Lade Kursdaten …"):
            h = kurse(kuerzel)
    except Exception:
        st.error(f"Für „{kuerzel}“ wurden keine Kursdaten gefunden. Prüf die Schreibweise "
                 "auf finance.yahoo.com.")
        hinweis()
        return
    info = stammdaten(kuerzel)
    k = kennzahlen(h)
    zeilen, (farbe, titel, text) = bewerten(k, info["typ"], profil, horizont)

    st.write("")
    st.html(f"<div class='kicker'>{kuerzel} · {TYPEN.get(info['typ'], 'Wertpapier')} · "
            f"Daten seit {k['start']:%Y}</div><h2 style='margin-top:0'>{info['name']}</h2>")
    st.html(f"<div class='urteil' style='border-color:{FARBE[farbe]}'><h3 style='color:{FARBE[farbe]}'>"
            f"{titel}</h3><p>{text} Profil: {PROFILE[profil]['titel']}, ca. {horizont} Jahre.</p></div>")

    m = st.columns(4)
    for spalte, (label, wert) in zip(m, [("Rendite p. a. · 5 J.", k["r5"]),
                                         ("Rendite p. a. · 10 J.", k["r10"]),
                                         ("Rendite p. a. · 20 J.", k["r20"]),
                                         ("Schlechtestes Kalenderjahr", k["schlechtestes_jahr"])]):
        spalte.metric(label, "–" if wert is None else f"{de(wert)} %")
    if k["schlechtestes_jahr_wann"]:
        m[3].caption(f"im Jahr {k['schlechtestes_jahr_wann']}")

    st.markdown("### Die Prüfung im Einzelnen")
    html = ""
    for stufe, krit, wert, warum in zeilen:
        html += (f"<div class='ampel'><span class='punkt' style='background:{FARBE[stufe]}'></span>"
                 f"<span class='krit'>{krit}</span><span class='wert'>{wert}</span>"
                 f"<span class='warum'>{warum}</span></div>")
    st.html(html)

    st.markdown("### Kursverlauf")
    zeitraum = st.segmented_control("Zeitraum", ["5 Jahre", "10 Jahre", "20 Jahre", "Alles"],
                                    default="10 Jahre", label_visibility="collapsed")
    jahre_sicht = {"5 Jahre": 5, "10 Jahre": 10, "20 Jahre": 20, "Alles": 200}[zeitraum or "10 Jahre"]
    ab = h.index[-1] - pd.DateOffset(years=jahre_sicht)
    teil = h[h.index >= ab]["Close"]
    norm = teil / teil.iloc[0] * 10000
    fig = go.Figure(go.Scatter(x=norm.index, y=norm, name=kuerzel, line=dict(color=AKZENT, width=2)))
    if kuerzel != "EUNL.DE":
        try:
            w = kurse("EUNL.DE")["Close"]
            w = w[w.index >= max(ab, w.index[0])]
            if len(w) > 20:
                start_wert = norm[norm.index >= w.index[0]].iloc[0]
                fig.add_trace(go.Scatter(x=w.index, y=w / w.iloc[0] * start_wert,
                                         name="Weltmarkt (MSCI World ETF)",
                                         line=dict(color=VERGLEICH, width=1.5)))
        except Exception:
            pass
    waehrung = {"EUR": "€", "USD": "$"}.get(info["waehrung"], info["waehrung"] or "")
    zusatz = "ohne Dividenden" if info["typ"] == "INDEX" else "mit Dividenden"
    fig.update_yaxes(title=f"Wert von 10.000 {waehrung} ({zusatz})", tickformat=",.0f")
    st.plotly_chart(layout(fig), width="stretch", key="kurs", config={"displayModeBar": False})
    notizen = []
    if info["typ"] == "INDEX":
        notizen.append("Indizes wie der S&P 500 werden ohne Dividenden geführt. Ein ETF darauf "
                       "hätte zusätzlich etwa 1,5 bis 2 % pro Jahr an Dividenden gebracht.")
    if info["waehrung"] and info["waehrung"] != "EUR":
        notizen.append(f"Kurse in {info['waehrung']}. Der Weltmarkt-Vergleich läuft in Euro, "
                       "ein Teil des Unterschieds kann also am Wechselkurs liegen.")
    if notizen:
        st.caption(" ".join(notizen))

    st.markdown("### Unter Wasser")
    st.caption("Wie weit lag der Kurs unter seinem bisherigen Höchststand? Je tiefer und länger, "
               "desto härter für die Nerven.")
    uw = k["unterwasser"][k["unterwasser"].index >= ab] * 100
    fig2 = go.Figure(go.Scatter(x=uw.index, y=uw, fill="tozeroy", line=dict(color=ROT, width=1),
                                fillcolor="rgba(178,58,58,0.18)", name="Abstand zum Hoch",
                                hovertemplate="%{y:.1f} % unter dem Hoch<extra></extra>"))
    fig2.update_yaxes(title="% unter dem Hoch", ticksuffix=" %")
    st.plotly_chart(layout(fig2, 260), width="stretch", key="unterwasser",
                    config={"displayModeBar": False})

    st.caption("Wie das Urteil zustande kommt: Schwankung, größter Absturz und Erholungszeit werden "
               "mit den Grenzen deines Profils verglichen. Einzelaktien gelten wegen des Klumpenrisikos "
               "nie als Basis. Das ist eine Einordnung, keine Kaufempfehlung.")
    hinweis()


# --- Portfolio-Baukasten ----------------------------------------------------
DATENSAETZE = {
    "Lange Historie (US-Fonds, Dollar)": {
        "aktien": ("Aktien (S&P 500 mit Dividenden)", ["^SP500TR", "VFINX"]),
        "anleihen": ("Anleihen (US-Gesamtmarkt)", ["VBMFX", "VBTLX", "AGG"]),
        "gold": ("Gold", ["GC=F", "GLD"]),
        "waehrung": "$",
        "info": "Reicht bis etwa 2000 zurück und enthält damit Dotcom-Crash und Finanzkrise. "
                "Gerechnet in US-Dollar, für Euro-Anleger kämen Wechselkursschwankungen dazu.",
    },
    "Euro-ETFs (kürzer, Euro)": {
        "aktien": ("Aktien Welt (MSCI World ETF)", ["EUNL.DE", "IWDA.AS"]),
        "anleihen": ("Euro-Staatsanleihen (ETF)", ["EUNH.DE", "IBGS.AS", "EXHA.DE"]),
        "gold": ("Gold (Xetra-Gold)", ["4GLD.DE", "EWG2.DE"]),
        "waehrung": "€",
        "info": "Echte ETFs, wie man sie in Deutschland kaufen kann. Die Daten beginnen aber "
                "erst um 2009, die Finanzkrise fehlt also.",
    },
}
KRISEN_FENSTER = [("Dotcom-Crash", "2000-03-24", "2002-10-09"),
                  ("Finanzkrise", "2007-10-09", "2009-03-09"),
                  ("Corona-Crash", "2020-02-19", "2020-03-23"),
                  ("Zinswende", "2022-01-03", "2022-10-12")]
BEISPIEL_MISCHUNGEN = {"Nur Aktien": (100, 0, 0), "80 / 20": (80, 20, 0), "60 / 40": (60, 40, 0),
                       "40 / 60": (40, 60, 0), "Mit Gold": (60, 25, 15), "Sehr vorsichtig": (20, 40, 0)}


@st.cache_data(ttl=3600, show_spinner=False)
def erste_verfuegbare(kandidaten: tuple):
    fehler = []
    for k in kandidaten:
        try:
            return k, kurse(k)["Close"]
        except Exception as e:
            fehler.append(k)
    raise ValueError(", ".join(fehler))


def simuliere(renditen: pd.DataFrame, gewichte: dict, rebalancing: bool, start=10000.0) -> pd.Series:
    gewichte = {k: v for k, v in gewichte.items() if v > 0}
    if not gewichte:
        return pd.Series(start, index=renditen.index)
    r = renditen[list(gewichte)]
    w = np.array([gewichte[k] for k in gewichte]) / 100
    gruppen = r.groupby(r.index.year) if rebalancing else [(None, r)]
    teile, wert = [], start
    for _, seg in gruppen:
        wachstum = (1 + seg).cumprod().to_numpy()
        verlauf = wert * (wachstum * w).sum(axis=1)
        teile.append(pd.Series(verlauf, index=seg.index))
        wert = verlauf[-1]
    return pd.concat(teile)


def kurz_kennzahlen(wert: pd.Series) -> dict:
    jahre = (wert.index[-1] - wert.index[0]).days / 365.25
    return {"cagr": ((wert.iloc[-1] / wert.iloc[0]) ** (1 / jahre) - 1) * 100,
            "dd": (wert / wert.cummax() - 1).min() * 100}


@st.cache_data(show_spinner=False)
def mischungs_kurve(renditen: pd.DataFrame, rebalancing: bool) -> list:
    """Alle Mischungen Aktien/Anleihen in 10er-Schritten (zwischengespeichert, damit die Seite flott bleibt)."""
    punkte = []
    for anteil in range(0, 101, 10):
        kz = kurz_kennzahlen(simuliere(renditen, {"aktien": anteil, "anleihen": 100 - anteil}, rebalancing))
        punkte.append((anteil, -kz["dd"], kz["cagr"]))
    return punkte


def mischung_setzen():
    wahl = st.session_state.get("mischung_wahl")
    if wahl:
        a, b, g = BEISPIEL_MISCHUNGEN[wahl]
        st.session_state["w_aktien"], st.session_state["w_anleihen"], st.session_state["w_gold"] = a, b, g


def portfolio():
    profil, horizont = aktuelles_profil()
    kopf("Schritt 3", "Portfolio-Baukasten",
         "Kaum jemand legt alles in eine Aktie. Mische Anlageklassen und schick sie durch echte "
         "Krisen, oder stell dir ein eigenes Depot aus Aktien und ETFs zusammen.")
    if not profil:
        st.info("Du hast noch kein Risikoprofil. Bis dahin rechnet der Baukasten mit „Ausgewogen“ "
                "und 15 Jahren Anlagedauer.")
        profil, horizont = "ausgewogen", 15

    modus = st.segmented_control("Modus", ["Anlageklassen mischen", "Eigenes Depot"],
                                 default="Anlageklassen mischen", key="pf_modus",
                                 label_visibility="collapsed")
    if modus == "Eigenes Depot":
        eigenes_depot(profil, horizont)
        return

    basis = st.segmented_control("Datenbasis", list(DATENSAETZE), default=list(DATENSAETZE)[0])
    satz = DATENSAETZE[basis or list(DATENSAETZE)[0]]
    st.caption(satz["info"])

    for key, wert in (("w_aktien", 60), ("w_anleihen", 40), ("w_gold", 0)):
        st.session_state.setdefault(key, wert)
    st.pills("Beispiel-Mischungen", list(BEISPIEL_MISCHUNGEN), key="mischung_wahl",
             on_change=mischung_setzen)
    s1, s2, s3, s4 = st.columns(4)
    w_a = s1.slider("Aktien %", 0, 100, step=5, key="w_aktien")
    w_b = s2.slider("Anleihen %", 0, 100, step=5, key="w_anleihen")
    w_g = s3.slider("Gold %", 0, 100, step=5, key="w_gold")
    w_t = 100 - w_a - w_b - w_g
    s4.metric("Tagesgeld %", f"{w_t} %" if w_t >= 0 else "–")
    if w_t < 0:
        st.error(f"Zusammen sind es {100 - w_t} %. Bitte so einstellen, dass höchstens 100 % herauskommen. "
                 "Der Rest landet automatisch im Tagesgeld.")
        hinweis()
        return
    o1, o2 = st.columns([1, 2])
    zins = o1.number_input("Zins aufs Tagesgeld (% pro Jahr)", 0.0, 6.0, 2.0, 0.25,
                           help="Vereinfachung: ein fester Zins über die ganze Zeit. In Wirklichkeit "
                                "lag er mal bei 0 %, mal bei 4 %.")
    rebalancing = o2.toggle("Einmal im Jahr zurück auf die Zielgewichte (Rebalancing)", value=True,
                            help="Ohne Rebalancing wächst der Aktienanteil in guten Jahren immer weiter, "
                                 "und die Mischung wird mit der Zeit riskanter.")

    try:
        with st.spinner("Lade Kursdaten …"):
            reihen, namen = {}, {}
            # Gold nur laden, wenn es gebraucht wird: Die Gold-Daten sind kürzer und würden
            # sonst den Zeitraum für alle beschneiden (z. B. den Dotcom-Crash abschneiden).
            klassen = ("aktien", "anleihen", "gold") if w_g > 0 else ("aktien", "anleihen")
            for klasse in klassen:
                name, kandidaten = satz[klasse]
                kuerzel, reihe = erste_verfuegbare(tuple(kandidaten))
                reihen[klasse], namen[klasse] = reihe, f"{name} · {kuerzel}"
    except ValueError as fehler:
        st.error(f"Für diese Datenbasis konnten keine Kurse geladen werden (versucht: {fehler}). "
                 "Probier die andere Datenbasis.")
        hinweis()
        return

    preise = pd.concat(reihen, axis=1).sort_index().ffill().dropna()
    renditen = preise.pct_change().dropna()
    tage_pro_jahr = len(renditen) / ((renditen.index[-1] - renditen.index[0]).days / 365.25)
    renditen["tagesgeld"] = (1 + zins / 100) ** (1 / tage_pro_jahr) - 1
    gewichte = {"aktien": w_a, "anleihen": w_b, "gold": w_g, "tagesgeld": w_t}
    if w_g == 0:
        gewichte.pop("gold")
    wert = simuliere(renditen, gewichte, rebalancing)
    nur_aktien = simuliere(renditen, {"aktien": 100}, rebalancing)
    w = satz["waehrung"]

    k = kennzahlen(pd.DataFrame({"Close": wert}))
    k_a = kennzahlen(pd.DataFrame({"Close": nur_aktien}))
    zeilen, (farbe, titel, text) = bewerten(k, "PORTFOLIO", profil, horizont)
    jahre = (wert.index[-1] - wert.index[0]).days / 365.25
    cagr = ((wert.iloc[-1] / wert.iloc[0]) ** (1 / jahre) - 1) * 100
    cagr_a = ((nur_aktien.iloc[-1] / nur_aktien.iloc[0]) ** (1 / jahre) - 1) * 100
    punkte = mischungs_kurve(renditen[["aktien", "anleihen"]], rebalancing)
    if farbe == "rot":
        text = "Mindestens ein zentrales Risikomerkmal liegt klar über dem, was zu deinem Profil passt."
    elif farbe == "blau":
        mit = 10000 * (1 + cagr / 100) ** horizont
        ohne = 10000 * (1 + cagr_a / 100) ** horizont
        noch_ok = max((p[0] for p in punkte if p[1] <= PROFILE[profil]["dd"]), default=0)
        text += (f" Deine Mischung brachte {de(cagr)} % pro Jahr, reine Aktien {de(cagr_a)} %. "
                 f"Würde es {horizont} Jahre so weiterlaufen (was niemand weiß), würden aus 10.000 "
                 f"{satz['waehrung']} etwa {de(mit, 0)} statt {de(ohne, 0)}. Laut der Kurve unten hätten bis etwa "
                 f"{noch_ok} % Aktien (Rest Anleihen) noch in die Absturz-Grenze deines Profils gepasst.")
    st.write("")
    st.html(f"<div class='kicker'>Deine Mischung · {w_a} % Aktien · {w_b} % Anleihen · {w_g} % Gold · "
            f"{w_t} % Tagesgeld · {preise.index[0]:%Y} bis heute</div>"
            f"<div class='urteil' style='border-color:{FARBE[farbe]}'><h3 style='color:{FARBE[farbe]}'>"
            f"{titel}</h3><p>{text} Profil: {PROFILE[profil]['titel']}, ca. {horizont} Jahre.</p></div>")

    def diff(x, einheit, n=1):   # Streamlit erkennt die Richtung nur am normalen Minuszeichen
        return f"{'+' if x >= 0 else '-'}{de(abs(x), n)} {einheit}"
    m = st.columns(4)
    m[0].metric("Rendite pro Jahr", f"{de(cagr)} %", diff(cagr - cagr_a, "Pkt."))
    m[1].metric("Schwankung", f"{de(k['vol'])} %", diff(k["vol"] - k_a["vol"], "Pkt."),
                delta_color="inverse")
    m[2].metric("Größter Absturz", f"{de(k['dd'], 0)} %", diff(k["dd"] - k_a["dd"], "Pkt.", 0))
    m[3].metric("Längste Erholung", f"{de(k['erholung'])} J.", diff(k["erholung"] - k_a["erholung"], "J."),
                delta_color="inverse")
    st.caption("Kleine Zahlen: Unterschied zu 100 % Aktien. Grün heißt besser, rot heißt schlechter.")

    st.markdown("### Die Prüfung im Einzelnen")
    st.html("".join(
        f"<div class='ampel'><span class='punkt' style='background:{FARBE[s]}'></span>"
        f"<span class='krit'>{kr}</span><span class='wert'>{wt}</span><span class='warum'>{wa}</span></div>"
        for s, kr, wt, wa in zeilen))

    st.markdown("### So hätten sich 10.000 entwickelt")
    log = st.toggle("Logarithmische Skala", value=True,
                    help="Bei langen Zeiträumen besser lesbar: Gleiche Prozent-Bewegungen sehen gleich groß aus.")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=nur_aktien.index, y=nur_aktien, name="Nur Aktien",
                             line=dict(color=VERGLEICH, width=1.5)))
    fig.add_trace(go.Scatter(x=wert.index, y=wert, name="Deine Mischung", line=dict(color=AKZENT, width=2.5)))
    fig.update_yaxes(title=f"Wert in {w}", tickformat=",.0f", type="log" if log else "linear")
    if log:   # nur gut lesbare Stufen (1, 2, 5, 10, 20, 50 …) statt jedem Zwischenwert
        tief, hoch = min(wert.min(), nur_aktien.min()), max(wert.max(), nur_aktien.max())
        stufen = [m * 10 ** e for e in range(2, 9) for m in (1, 2, 5) if tief * 0.8 <= m * 10 ** e <= hoch * 1.25]
        fig.update_yaxes(tickvals=stufen)
    st.plotly_chart(layout(fig), width="stretch", key="pf_verlauf", config={"displayModeBar": False})
    st.caption(f"Endwert: {de(wert.iloc[-1], 0)} {w} mit deiner Mischung, "
               f"{de(nur_aktien.iloc[-1], 0)} {w} nur mit Aktien. Ohne Kosten und Steuern.")

    st.markdown("### In den großen Krisen")
    zeilen_html = ""
    for name, von, bis in KRISEN_FENSTER:
        von, bis = pd.Timestamp(von), pd.Timestamp(bis)
        if von < wert.index[0]:
            continue
        def veraenderung(reihe):
            return (reihe[reihe.index <= bis].iloc[-1] / reihe[reihe.index <= von].iloc[-1] - 1) * 100
        p, a = veraenderung(wert), veraenderung(nur_aktien)
        breite_p, breite_a = min(abs(p), 100), min(abs(a), 100)
        zeilen_html += (
            f"<div style='display:grid;grid-template-columns:9rem 1fr 4.5rem;gap:.3rem 1rem;"
            f"align-items:center;padding:.6rem 0;border-bottom:1px solid {LINIE}'>"
            f"<div><b>{name}</b><br><span style='color:{GEDAEMPFT};font-size:.82rem'>"
            f"{von:%m/%Y} – {bis:%m/%Y}</span></div>"
            f"<div><div class='balken' style='height:10px;background:{AKZENT};width:{breite_p}%;border-radius:2px'></div>"
            f"<div class='balken' style='height:10px;background:{VERGLEICH};width:{breite_a}%;border-radius:2px;margin-top:4px'></div></div>"
            f"<div style='text-align:right;font-variant-numeric:tabular-nums'><b>{'+' if p > 0 else ''}{de(p, 0)} %</b><br>"
            f"<span style='color:{GEDAEMPFT}'>{'+' if a > 0 else ''}{de(a, 0)} %</span></div></div>")
    if zeilen_html:
        st.html(f"<div style='font-size:.85rem;color:{GEDAEMPFT};margin-bottom:.3rem'>"
                f"<span style='color:{AKZENT}'>■</span> Deine Mischung &nbsp; "
                f"<span style='color:{VERGLEICH}'>■</span> Nur Aktien · Veränderung vom Hoch bis zum Tief</div>"
                + zeilen_html)
        st.caption("Achte auf die Zinswende 2022: Damals fielen Aktien und Anleihen gleichzeitig. "
                   "Mischen schützt oft, aber nicht immer.")

    st.markdown("### Alle Mischungen aus Aktien und Anleihen im Vergleich")
    st.caption("Jeder Punkt ist eine Mischung von 0 % bis 100 % Aktien (Rest Anleihen). Weiter rechts "
               "heißt tiefere Abstürze, weiter oben heißt mehr Rendite. Mehr Rendite gibt es fast nie "
               "ohne mehr Risiko.")
    eigen = kurz_kennzahlen(wert)
    kurve = go.Figure()
    kurve.add_trace(go.Scatter(x=[p[1] for p in punkte], y=[p[2] for p in punkte],
                               mode="lines+markers+text", text=[f"{p[0]} %" for p in punkte],
                               textposition="top left", textfont=dict(size=11, color=GEDAEMPFT),
                               line=dict(color=VERGLEICH, width=1.5), marker=dict(size=7, color=VERGLEICH),
                               name="Aktien-Anteil",
                               hovertemplate="%{text} Aktien · Absturz −%{x:.0f} % · Rendite %{y:.1f} % p. a.<extra></extra>"))
    kurve.add_trace(go.Scatter(x=[-eigen["dd"]], y=[eigen["cagr"]], mode="markers", name="Deine Mischung",
                               marker=dict(size=14, color=AKZENT, line=dict(color="white", width=2)),
                               hovertemplate="Deine Mischung · Absturz −%{x:.0f} % · Rendite %{y:.1f} % p. a.<extra></extra>"))
    grenze = PROFILE[profil]["dd"]
    kurve.add_vrect(x0=grenze, x1=max(p[1] for p in punkte) + 5, fillcolor=ROT, opacity=0.06, line_width=0)
    kurve.add_vline(x=grenze, line_dash="dot", line_color=ROT,
                    annotation_text=f"Grenze deines Profils (−{grenze} %)", annotation_position="top")
    kurve.update_xaxes(title="Größter Absturz (%)", ticksuffix=" %")
    kurve.update_yaxes(title="Rendite pro Jahr (%)", ticksuffix=" %")
    kurve.update_layout(hovermode="closest")
    st.plotly_chart(layout(kurve, 420), width="stretch", key="pf_kurve", config={"displayModeBar": False})

    st.caption("Verwendete Daten: " + " · ".join(namen.values()) + f" · Tagesgeld mit festem Zins von {de(zins, 2)} %.")
    hinweis()


# --- Sparplan-Simulator -----------------------------------------------------
# --- Eigenes Depot ----------------------------------------------------------
STANDARD_DEPOT = pd.DataFrame({"Kürzel": ["EUNL.DE", "AAPL", "SAP.DE"],
                               "Betrag (€)": [6000.0, 2000.0, 2000.0]})


@st.cache_data(ttl=3600, show_spinner=False)
def kurse_in_euro(kuerzel: str):
    """Schlusskurse in Euro. Andere Währungen werden mit dem Tageskurs umgerechnet."""
    c = kurse(kuerzel)["Close"].copy()
    waehrung = stammdaten(kuerzel)["waehrung"] or "EUR"
    if waehrung in ("GBp", "GBX"):          # Londoner Kurse in Pence
        c, waehrung = c / 100, "GBP"
    if waehrung.upper() != "EUR":
        fx = kurse(f"{waehrung.upper()}EUR=X")["Close"]
        fx = fx.reindex(c.index.union(fx.index)).ffill().reindex(c.index)
        c = (c * fx).dropna()
    return c, waehrung


def eigenes_depot(profil, horizont):
    st.html("<p class='lead' style='margin-top:.5rem'>Gib dein Startkapital und ein Kaufdatum ein und "
            "verteile das Geld auf Aktien und ETFs. Die App kauft alles an diesem Tag und zeigt, was "
            "bis heute daraus geworden wäre.</p>")
    e1, e2 = st.columns(2)
    kapital = e1.number_input("Startkapital (€)", 100, 10_000_000, 10_000, 500)
    heute = pd.Timestamp.today().normalize()
    start = pd.Timestamp(e2.date_input("Kaufdatum", (heute - pd.DateOffset(years=10)).date(),
                                       min_value=pd.Timestamp("1990-01-01").date(),
                                       max_value=(heute - pd.DateOffset(months=6)).date(),
                                       format="DD.MM.YYYY"))

    st.caption("Kürzel wie bei Yahoo Finance, z. B. EUNL.DE (MSCI World ETF), AAPL (Apple), SAP.DE, "
               "MSFT, ALV.DE (Allianz). Zeilen kannst du unten hinzufügen und links markieren und löschen.")
    tabelle = st.data_editor(
        STANDARD_DEPOT, num_rows="dynamic", hide_index=True, width="stretch", key="depot_editor",
        column_config={
            "Kürzel": st.column_config.TextColumn(required=True, max_chars=15),
            "Betrag (€)": st.column_config.NumberColumn(min_value=0.0, step=100.0, format="%.0f €",
                                                        required=True),
        })
    pos = tabelle.dropna()
    pos = pos.assign(Kürzel=pos["Kürzel"].astype(str).str.strip().str.upper())
    pos = pos[(pos["Kürzel"] != "") & (pos["Betrag (€)"] > 0)].groupby("Kürzel", as_index=False).sum()
    investiert = float(pos["Betrag (€)"].sum())
    bar = kapital - investiert
    b1, b2 = st.columns(2)
    b1.metric("Investiert", f"{de(investiert, 0)} €")
    b2.metric("Bleibt als Bargeld", f"{de(bar, 0)} €" if bar >= 0 else "–")
    if bar < 0:
        st.error(f"Du hast {de(-bar, 0)} € mehr verteilt, als du Startkapital hast.")
        hinweis()
        return
    if pos.empty:
        st.info("Trag mindestens eine Aktie oder einen ETF mit Betrag ein.")
        hinweis()
        return

    reihen, infos, fehlt, waehrungen = {}, {}, [], set()
    with st.spinner("Lade Kursdaten …"):
        for k in pos["Kürzel"]:
            try:
                reihen[k], w = kurse_in_euro(k)
                infos[k] = stammdaten(k)
                waehrungen.add(w)
            except Exception:
                fehlt.append(k)
    if fehlt:
        st.error("Keine Kursdaten gefunden für: " + ", ".join(fehlt) + ". Prüf die Schreibweise "
                 "auf finance.yahoo.com. Diese Zeilen werden ignoriert.")
        pos = pos[~pos["Kürzel"].isin(fehlt)]
        if pos.empty:
            hinweis()
            return

    erster = max(r.index[0] for r in reihen.values())
    if erster > start:
        juengster = max(reihen, key=lambda k: reihen[k].index[0])
        st.warning(f"{juengster} gibt es erst seit {erster:%d.%m.%Y}. Die Rechnung beginnt deshalb "
                   f"an diesem Tag statt am {start:%d.%m.%Y}.")
        start = erster
    preise = pd.concat(reihen, axis=1).sort_index().ffill()
    preise = preise[preise.index >= start].dropna()
    if len(preise) < 60:
        st.warning("Der Zeitraum ist zu kurz für eine sinnvolle Auswertung.")
        hinweis()
        return

    stueck = {r["Kürzel"]: r["Betrag (€)"] / preise[r["Kürzel"]].iloc[0] for _, r in pos.iterrows()}
    werte = pd.DataFrame({k: preise[k] * n for k, n in stueck.items()})
    depot = werte.sum(axis=1) + bar
    try:
        welt, _ = kurse_in_euro("EUNL.DE")
        welt = welt.reindex(depot.index.union(welt.index)).ffill().reindex(depot.index)
        vergleich = investiert * welt / welt.iloc[0] + bar   # gleicher Betrag investiert, gleiches Bargeld
    except Exception:
        vergleich = None

    k = kennzahlen(pd.DataFrame({"Close": depot}))
    einzelaktien = [x for x in stueck if infos[x]["typ"] not in ("ETF", "INDEX", "MUTUALFUND")]
    groesster = max(stueck, key=lambda x: werte[x].iloc[-1])
    anteil_max = werte[groesster].iloc[-1] / depot.iloc[-1] * 100
    typ = "PORTFOLIO" if len(stueck) >= 3 or not einzelaktien else "EQUITY"
    zeilen, (farbe, titel, text) = bewerten(k, typ, profil, horizont)
    if einzelaktien and anteil_max > 30 and infos[groesster]["typ"] not in ("ETF", "INDEX", "MUTUALFUND"):
        zeilen[3] = ("rot", "Streuung", f"{groesster}: {de(anteil_max, 0)} %",
                     "Eine einzelne Aktie macht über 30 % des Depots aus. Läuft es für diese Firma "
                     "schlecht, trifft es das ganze Depot.")
        if farbe == "gruen":
            farbe, titel, text = ("gelb", "Passt mit Abstrichen",
                                  "Die Schwankungen lagen im Rahmen, aber das Depot hängt stark an einer Firma.")

    jahre = (depot.index[-1] - depot.index[0]).days / 365.25
    cagr = ((depot.iloc[-1] / kapital) ** (1 / jahre) - 1) * 100
    st.write("")
    st.html(f"<div class='kicker'>Dein Depot · {len(stueck)} Positionen · gekauft am {depot.index[0]:%d.%m.%Y}"
            f"</div><div class='urteil' style='border-color:{FARBE[farbe]}'><h3 style='color:{FARBE[farbe]}'>"
            f"{titel}</h3><p>{text} Profil: {PROFILE[profil]['titel']}, ca. {horizont} Jahre.</p></div>")
    m = st.columns(4)
    gewinn = depot.iloc[-1] - kapital
    m[0].metric("Wert heute", f"{de(depot.iloc[-1], 0)} €",
                f"{'+' if gewinn >= 0 else '-'}{de(abs(gewinn), 0)} €")
    m[1].metric("Rendite pro Jahr", f"{de(cagr)} %")
    m[2].metric("Größter Absturz", f"{de(k['dd'], 0)} %")
    if vergleich is not None:
        m[3].metric("Weltmarkt (MSCI World)", f"{de(vergleich.iloc[-1], 0)} €")
        m[3].caption("gleicher Betrag investiert, gleiches Datum" + (", gleiches Bargeld" if bar > 0 else ""))

    st.markdown("### Die Prüfung im Einzelnen")
    st.html("".join(
        f"<div class='ampel'><span class='punkt' style='background:{FARBE[s_]}'></span>"
        f"<span class='krit'>{kr}</span><span class='wert'>{wt}</span><span class='warum'>{wa}</span></div>"
        for s_, kr, wt, wa in zeilen))

    st.markdown("### Wertentwicklung")
    fig = go.Figure()
    if vergleich is not None:
        fig.add_trace(go.Scatter(x=vergleich.index, y=vergleich, name="Weltmarkt (MSCI World ETF)",
                                 line=dict(color=VERGLEICH, width=1.5),
                                 hovertemplate="%{y:,.0f} €<extra>Weltmarkt</extra>"))
    fig.add_trace(go.Scatter(x=depot.index, y=depot, name="Dein Depot", line=dict(color=AKZENT, width=2.5),
                             hovertemplate="%{y:,.0f} €<extra>Dein Depot</extra>"))
    fig.add_hline(y=kapital, line_dash="dot", line_color=ROT, annotation_text="Startkapital",
                  annotation_position="bottom right")
    gross = depot.max() / kapital > 8
    log = st.toggle("Logarithmische Skala", value=gross, key="depot_log",
                    help="Bei sehr starken Anstiegen besser lesbar: Gleiche Prozent-Bewegungen sehen gleich groß aus.")
    fig.update_yaxes(title="Wert in €", tickformat=",.0f", type="log" if log else "linear")
    st.plotly_chart(layout(fig, 400), width="stretch", key="depot_verlauf", config={"displayModeBar": False})

    st.markdown("### Woraus dein Depot besteht")
    palette = [AKZENT, "#5B8A72", "#B7791F", "#7A5C8E", "#3E7CB1", "#A0522D", "#6B8E23", "#8C6A5D"]
    flaeche = go.Figure()
    for i, x in enumerate(sorted(stueck, key=lambda x: -werte[x].iloc[-1])):
        flaeche.add_trace(go.Scatter(x=werte.index, y=werte[x], name=x, stackgroup="eins", mode="lines",
                                     line=dict(width=0.5, color=palette[i % len(palette)]),
                                     hovertemplate=f"{x}: " + "%{y:,.0f} €<extra></extra>"))
    flaeche.update_yaxes(title="Wert in €", tickformat=",.0f")
    st.plotly_chart(layout(flaeche, 340), width="stretch", key="depot_flaeche", config={"displayModeBar": False})

    zeilen_html = ""
    for x in sorted(stueck, key=lambda x: -werte[x].iloc[-1]):
        rein = float(pos.loc[pos["Kürzel"] == x, "Betrag (€)"].iloc[0])
        jetzt = werte[x].iloc[-1]
        veraenderung = (jetzt / rein - 1) * 100
        farbe_v = GRUEN if veraenderung >= 0 else ROT
        zeilen_html += (
            f"<div class='ampel' style='grid-template-columns:1.6fr 1fr 1fr .8fr .7fr'>"
            f"<span><b>{x}</b><br><span style='color:{GEDAEMPFT};font-size:.85rem'>"
            f"{infos[x]['name'] if len(infos[x]['name']) <= 42 else infos[x]['name'][:40].rstrip() + ' …'}</span></span>"
            f"<span class='wert'>{de(rein, 0)} €</span><span class='wert'>{de(jetzt, 0)} €</span>"
            f"<span class='wert' style='color:{farbe_v}'>{'+' if veraenderung >= 0 else ''}{de(veraenderung, 0)} %</span>"
            f"<span class='wert'>{de(jetzt / depot.iloc[-1] * 100, 0)} %</span></div>")
    st.html(f"<div class='ampel' style='grid-template-columns:1.6fr 1fr 1fr .8fr .7fr;color:{GEDAEMPFT};"
            f"font-size:.82rem;border-bottom:2px solid {LINIE}'><span>Position</span><span>Gekauft für</span>"
            f"<span>Wert heute</span><span>Veränderung</span><span>Anteil</span></div>" + zeilen_html)
    hinweise = ["Gekauft wird einmalig am Startdatum, danach wird nichts mehr umgeschichtet (Buy-and-Hold)."]
    if waehrungen - {"EUR"}:
        hinweise.append("Kurse in " + ", ".join(sorted(waehrungen - {"EUR"})) + " wurden mit dem jeweiligen "
                        "Tageskurs in Euro umgerechnet. Ein Teil der Entwicklung kann also am Wechselkurs liegen.")
    hinweise.append("Ohne Kauf- und Depotgebühren und ohne Steuern. Dividenden sind enthalten, wo Yahoo sie "
                    "in die Kurse einrechnet.")
    st.caption(" ".join(hinweise))
    st.caption("Achtung Rückschau: Wer heute ein Depot aus Firmen zusammenstellt, die man heute kennt, "
               "wählt fast automatisch die Gewinner der Vergangenheit. Vor 10 Jahren hätte man nicht "
               "gewusst, welche das sind.")
    hinweis()


def sparplan_ergebnisse(niveau: pd.Series, rate: float, monate: int) -> pd.DataFrame:
    """Endwert eines Sparplans für jeden möglichen Startmonat.
    Jeden Monat wird `rate` zum Monatsende-Niveau investiert und bis zum Ende gehalten."""
    L = niveau.to_numpy()
    kum = np.concatenate([[0.0], np.cumsum(1 / L)])   # kum[i] = Summe 1/L[0..i-1]
    zeilen = []
    for s in range(0, len(L) - monate):
        e = s + monate
        zeilen.append({"start": niveau.index[s], "ende": niveau.index[e],
                       "endwert": rate * L[e] * (kum[e] - kum[s])})
    return pd.DataFrame(zeilen)


def sparplan_verlauf(niveau: pd.Series, rate: float, start: int, monate: int) -> pd.Series:
    L = niveau.to_numpy()[start:start + monate + 1]
    anteile = np.cumsum(rate / L[:-1])
    return pd.Series(np.concatenate([[0.0], anteile * L[1:]]), index=niveau.index[start:start + monate + 1])


def sparplan():
    profil, horizont = aktuelles_profil()
    kopf("Schritt 4", "Sparplan-Simulator",
         "Die meisten sparen nicht einmalig, sondern jeden Monat. Hier siehst du, was aus einem "
         "Sparplan geworden wäre, und zwar nicht nur für einen Durchschnitt, sondern für jeden "
         "echten Startmonat. Mal hatte man Glück, mal Pech.")

    basis = st.segmented_control("Datenbasis", list(DATENSAETZE), default=list(DATENSAETZE)[0],
                                 key="sp_basis")
    satz = DATENSAETZE[basis or list(DATENSAETZE)[0]]
    w = satz["waehrung"]

    e1, e2, e3, e4 = st.columns(4)
    rate = e1.number_input(f"Rate pro Monat ({w})", 10, 5000, 100, 10)
    standard_aktien = int(st.session_state.get("w_aktien", 80)) if st.session_state.get("w_gold", 0) == 0 else 80
    aktien = e2.slider("Aktienanteil % (Rest Anleihen)", 0, 100, standard_aktien, 10)
    ter = e3.number_input("Laufende Kosten (% pro Jahr)", 0.0, 3.0, 0.2, 0.05,
                          help="Die jährliche Gebühr des Fonds (TER). Breite ETFs liegen oft bei 0,1 bis "
                               "0,3 %, aktiv gemanagte Fonds oft bei 1,5 bis 2 %.")
    zins = e4.number_input("Tagesgeld zum Vergleich (% p. a.)", 0.0, 6.0, 2.0, 0.25)

    try:
        with st.spinner("Lade Kursdaten …"):
            reihen = {k: erste_verfuegbare(tuple(satz[k][1]))[1] for k in ("aktien", "anleihen")}
    except ValueError as fehler:
        st.error(f"Für diese Datenbasis konnten keine Kurse geladen werden (versucht: {fehler}).")
        hinweis()
        return
    preise = pd.concat(reihen, axis=1).sort_index().ffill().dropna()
    renditen = preise.pct_change().dropna()
    taeglich = simuliere(renditen, {"aktien": aktien, "anleihen": 100 - aktien}, True, start=1.0)
    monatlich = taeglich.resample("ME").last()
    monatlich = monatlich * (1 - ter / 100) ** (np.arange(len(monatlich)) / 12)   # laufende Kosten
    max_jahre = int((len(monatlich) - 13) / 12)

    laufzeit = st.slider("Laufzeit in Jahren", 5, max(max_jahre, 6), min(20, max_jahre), 1,
                         help=f"Mit dieser Datenbasis sind bis zu {max_jahre} Jahre möglich. Je länger die "
                              "Laufzeit, desto weniger verschiedene Startmonate gibt es zum Vergleichen.")
    monate = laufzeit * 12
    erg = sparplan_ergebnisse(monatlich, rate, monate)
    if len(erg) < 12:
        st.warning("Für diese Laufzeit gibt es weniger als ein Jahr an verschiedenen Startmonaten. "
                   "Die Ergebnisse sind dann kaum aussagekräftig, wähle eine kürzere Laufzeit.")
    if erg.empty:
        hinweis()
        return

    eingezahlt = rate * monate
    q = (1 + zins / 100) ** (1 / 12)
    tagesgeld = rate * sum(q ** k for k in range(1, monate + 1))
    median = erg["endwert"].median()
    schlecht, gut = erg.loc[erg["endwert"].idxmin()], erg.loc[erg["endwert"].idxmax()]
    verlust_quote = (erg["endwert"] < eingezahlt).mean() * 100
    unter_tg = (erg["endwert"] < tagesgeld).mean() * 100

    st.write("")
    st.html(f"<div class='kicker'>{de(rate, 0)} {w} im Monat · {laufzeit} Jahre · {aktien} % Aktien · "
            f"{len(erg)} verschiedene Startmonate von {erg['start'].iloc[0]:%m/%Y} bis "
            f"{erg['start'].iloc[-1]:%m/%Y}</div>")
    m = st.columns(4)
    m[0].metric("Eingezahlt", f"{de(eingezahlt, 0)} {w}")
    m[1].metric("Typisches Ergebnis", f"{de(median, 0)} {w}", f"{'+' if median >= eingezahlt else '-'}"
                f"{de(abs(median / eingezahlt - 1) * 100, 0)} % auf die Einzahlungen")
    m[2].metric("Schlechtester Fall", f"{de(schlecht['endwert'], 0)} {w}")
    m[2].caption(f"Start {schlecht['start']:%m/%Y}")
    m[3].metric("Bester Fall", f"{de(gut['endwert'], 0)} {w}")
    m[3].caption(f"Start {gut['start']:%m/%Y}")

    if verlust_quote == 0:
        satz_verlust = f"In <b>keinem</b> der {len(erg)} Zeiträume lag man am Ende unter den Einzahlungen."
    else:
        satz_verlust = (f"In <b>{de(verlust_quote, 0)} %</b> der Zeiträume lag man am Ende sogar "
                        f"<b>unter</b> den Einzahlungen.")
    st.html(f"<div class='urteil' style='border-color:{AKZENT}'><h3>Was das heißt</h3><p>"
            f"Typischerweise wurden aus {de(eingezahlt, 0)} {w} etwa {de(median, 0)} {w}. {satz_verlust} "
            f"Mit Tagesgeld zu {de(zins, 2)} % wären es immer {de(tagesgeld, 0)} {w} gewesen. "
            f"Der Sparplan lag in {de(100 - unter_tg, 0)} % der Fälle darüber.</p></div>")

    st.markdown("### Ergebnis je nach Startmonat")
    st.caption("Jeder Punkt der Linie ist ein Sparplan, der in diesem Monat begann und "
               f"{laufzeit} Jahre lief. Gleicher Plan, sehr unterschiedliches Ergebnis, nur wegen des Zeitpunkts.")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=erg["start"], y=erg["endwert"], name="Endwert Sparplan",
                             line=dict(color=AKZENT, width=2), fill="tozeroy",
                             fillcolor="rgba(31,78,95,0.08)",
                             hovertemplate="Start %{x|%m/%Y}: %{y:,.0f}<extra></extra>"))
    fig.add_hline(y=eingezahlt, line_color=ROT, line_dash="dot",
                  annotation_text="Eingezahlt", annotation_position="bottom right")
    fig.add_hline(y=tagesgeld, line_color=VERGLEICH, line_dash="dash",
                  annotation_text="Tagesgeld", annotation_position="top right")
    fig.update_yaxes(title=f"Endwert in {w}", tickformat=",.0f", rangemode="tozero")
    fig.update_xaxes(title="Startmonat des Sparplans")
    st.plotly_chart(layout(fig, 400), width="stretch", key="sp_start", config={"displayModeBar": False})

    st.markdown("### Drei Sparpläne im Verlauf")
    st.caption("Wie sich der Kontostand Monat für Monat entwickelt hätte, im besten, typischen und "
               "schlechtesten Fall. Achte darauf, wie stark es zwischendurch schwankt.")
    pos_median = int((erg["endwert"] - median).abs().idxmin())
    faelle = [("Bester Fall", int(gut.name), GRUEN), ("Typischer Fall", pos_median, AKZENT),
              ("Schlechtester Fall", int(schlecht.name), ROT)]
    fig2 = go.Figure()
    for name, pos, farbe in faelle:
        v = sparplan_verlauf(monatlich, rate, pos, monate)
        fig2.add_trace(go.Scatter(x=np.arange(len(v)) / 12, y=v.to_numpy(),
                                  name=f"{name} (Start {erg['start'].iloc[pos]:%m/%Y})",
                                  line=dict(color=farbe, width=2),
                                  hovertemplate="Jahr %{x:.1f}: %{y:,.0f}<extra></extra>"))
    fig2.add_trace(go.Scatter(x=np.arange(monate + 1) / 12, y=rate * np.arange(monate + 1),
                              name="Eingezahlt", line=dict(color=VERGLEICH, dash="dot", width=1.5)))
    fig2.update_xaxes(title="Jahre seit Start", hoverformat=".1f")
    fig2.update_yaxes(title=f"Kontostand in {w}", tickformat=",.0f")
    st.plotly_chart(layout(fig2, 400), width="stretch", key="sp_verlauf", config={"displayModeBar": False})

    st.caption("Alle Beträge nominal, also ohne die Inflation herauszurechnen, und ohne Steuern. "
               f"Laufende Kosten von {de(ter, 2)} % pro Jahr sind abgezogen. Die Zeiträume überlappen sich, "
               "deshalb sind die Startmonate nicht unabhängig voneinander.")
    hinweis()


# --- Kosten-Rechner ---------------------------------------------------------
RENDITE_HINWEIS = ("Das ist eine Annahme, keine Vorhersage. Zum Vergleich: Im Sparplan-Simulator brachte "
                   "der S&P 500 mit Dividenden seit 1988 rund 11 % pro Jahr, das war aber eine besonders "
                   "gute Phase. Viele rechnen für die Zukunft vorsichtiger mit 5 bis 7 %.")


def kosten_verlauf(einmal, rate, jahre, rendite, ter, aufschlag, fix):
    """Monatliche Simulation. Gibt Kontostand am Ende jedes Jahres zurück (Index 0 = Start)."""
    g = (1 + rendite / 100) ** (1 / 12)
    k = (1 - ter / 100) ** (1 / 12)
    wert = einmal * (1 - aufschlag / 100)
    werte = [wert]
    for monat in range(1, jahre * 12 + 1):
        wert = (wert + max(rate - fix, 0) * (1 - aufschlag / 100)) * g * k
        if monat % 12 == 0:
            werte.append(wert)
    return np.array(werte)


def kosten():
    kopf("Schritt 5", "Kosten-Rechner",
         "Gebühren sehen klein aus: 1,5 % hier, 5 % Ausgabeaufschlag da. Über Jahrzehnte fressen sie "
         "aber einen großen Teil deines Vermögens. Vergleiche hier zwei Produkte.")

    a1, a2, a3, a4 = st.columns(4)
    einmal = a1.number_input("Einmalbetrag zum Start (€)", 0, 1_000_000, 0, 500)
    rate = a2.number_input("Sparrate pro Monat (€)", 0, 10_000, 100, 10)
    jahre = a3.slider("Laufzeit (Jahre)", 5, 50, 30)
    rendite = a4.number_input("Rendite vor Kosten (% p. a.)", 0.0, 12.0, 6.0, 0.5, help=RENDITE_HINWEIS)
    if einmal == 0 and rate == 0:
        st.info("Gib einen Einmalbetrag oder eine Sparrate ein.")
        hinweis()
        return

    st.write("")
    pa, pb = st.columns(2)
    with pa:
        st.markdown("**Produkt A**")
        name_a = st.text_input("Name A", "Günstiger ETF", label_visibility="collapsed")
        ter_a = st.number_input("Laufende Kosten A (% p. a.)", 0.0, 5.0, 0.2, 0.05,
                                help="TER: die jährliche Fondsgebühr, steht im Datenblatt des Fonds.")
        auf_a = st.number_input("Ausgabeaufschlag A (%)", 0.0, 10.0, 0.0, 0.5,
                                help="Einmalige Gebühr auf jede Einzahlung, typisch bei Fonds von Banken.")
        fix_a = st.number_input("Gebühr pro Sparrate A (€)", 0.0, 10.0, 0.0, 0.5)
    with pb:
        st.markdown("**Produkt B**")
        name_b = st.text_input("Name B", "Teurer Bankfonds", label_visibility="collapsed")
        ter_b = st.number_input("Laufende Kosten B (% p. a.)", 0.0, 5.0, 1.8, 0.05)
        auf_b = st.number_input("Ausgabeaufschlag B (%)", 0.0, 10.0, 5.0, 0.5)
        fix_b = st.number_input("Gebühr pro Sparrate B (€)", 0.0, 10.0, 0.0, 0.5)

    va = kosten_verlauf(einmal, rate, jahre, rendite, ter_a, auf_a, fix_a)
    vb = kosten_verlauf(einmal, rate, jahre, rendite, ter_b, auf_b, fix_b)
    v0 = kosten_verlauf(einmal, rate, jahre, rendite, 0, 0, 0)
    eingezahlt = einmal + rate * 12 * jahre
    luecke = va[-1] - vb[-1]

    def effektiv(v):
        """Jährliche Rendite nach allen Kosten (interne Verzinsung, gerechnet über die Zahlungen)."""
        tief, hoch = -0.5, 0.5
        for _ in range(60):
            mitte = (tief + hoch) / 2
            g = (1 + mitte) ** (1 / 12)
            wert = einmal
            for _m in range(jahre * 12):
                wert = (wert + rate) * g
            tief, hoch = (mitte, hoch) if wert < v else (tief, mitte)
        return mitte * 100

    st.write("")
    teurer, guenstiger = (name_b, name_a) if luecke >= 0 else (name_a, name_b)
    st.html(f"<div class='urteil' style='border-color:{ROT}'><h3>{de(abs(luecke), 0)} € Unterschied</h3>"
            f"<p>Bei gleicher Rendite vor Kosten hätte „{teurer}“ nach {jahre} Jahren {de(abs(luecke), 0)} € "
            f"weniger als „{guenstiger}“. Das sind "
            + (f"so viel wie {de(abs(luecke) / rate / 12, 1)} Jahre Sparraten. " if rate > 0 else "")
            + f"Ohne jede Gebühr wären es {de(v0[-1], 0)} € gewesen.</p></div>")
    m = st.columns(4)
    m[0].metric("Eingezahlt", f"{de(eingezahlt, 0)} €")
    m[1].metric(name_a, f"{de(va[-1], 0)} €")
    m[1].caption(f"Rendite nach Kosten: {de(effektiv(va[-1]))} % p. a.")
    m[2].metric(name_b, f"{de(vb[-1], 0)} €")
    m[2].caption(f"Rendite nach Kosten: {de(effektiv(vb[-1]))} % p. a.")
    m[3].metric("Ohne Kosten", f"{de(v0[-1], 0)} €")

    st.markdown("### Wie die Lücke wächst")
    st.caption("Kosten wirken wie ein umgekehrter Zinseszins: Was du an Gebühren zahlst, kann nicht "
               "mehr für dich arbeiten. Deshalb wird die Lücke von Jahr zu Jahr schneller größer.")
    x = np.arange(jahre + 1)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=vb, name=name_b, line=dict(color=ROT, width=2),
                             hovertemplate="Jahr %{x}: %{y:,.0f} €<extra></extra>"))
    fig.add_trace(go.Scatter(x=x, y=va, name=name_a, line=dict(color=AKZENT, width=2.5), fill="tonexty",
                             fillcolor="rgba(178,58,58,0.10)",
                             hovertemplate="Jahr %{x}: %{y:,.0f} €<extra></extra>"))
    fig.add_trace(go.Scatter(x=x, y=einmal + rate * 12 * x, name="Eingezahlt",
                             line=dict(color=VERGLEICH, dash="dot", width=1.5),
                             hovertemplate="Jahr %{x}: %{y:,.0f} €<extra></extra>"))
    fig.update_xaxes(title="Jahre", hoverformat="d")
    fig.update_yaxes(title="Kontostand in €", tickformat=",.0f")
    st.plotly_chart(layout(fig, 400), width="stretch", key="kosten_chart", config={"displayModeBar": False})

    st.markdown("### Was 1 % mehr Kosten bedeutet")
    zeilen = ""
    for t in (0.1, 0.2, 0.5, 1.0, 1.5, 2.0):
        e = kosten_verlauf(einmal, rate, jahre, rendite, t, 0, 0)[-1]
        anteil = (1 - e / v0[-1]) * 100
        zeilen += (f"<div style='display:grid;grid-template-columns:7rem 1fr 7rem;gap:1rem;align-items:center;"
                   f"padding:.45rem 0;border-bottom:1px solid {LINIE}'><span>{de(t, 1)} % p. a.</span>"
                   f"<div class='balken' style='height:10px;background:{ROT};opacity:.75;width:{min(anteil, 100):.1f}%;"
                   f"border-radius:2px'></div><span style='text-align:right;font-variant-numeric:tabular-nums'>"
                   f"−{de(anteil, 0)} %</span></div>")
    st.html(f"<div style='font-size:.85rem;color:{GEDAEMPFT};margin-bottom:.3rem'>Laufende Kosten · "
            f"so viel weniger Endvermögen als ohne Kosten ({jahre} Jahre)</div>" + zeilen)
    st.caption("Vereinfachte Rechnung mit gleichmäßiger Rendite, ohne Steuern. Echte Märkte schwanken, "
               "die Kosten fallen aber immer an, auch in schlechten Jahren.")
    hinweis()


# --- Inflation & Zinseszins -------------------------------------------------
def inflation():
    kopf("Schritt 6", "Inflation & Zinseszins",
         "Zwei Kräfte arbeiten über Jahrzehnte: Die Inflation frisst Kaufkraft, der Zinseszins vermehrt "
         "Vermögen. Wer früh anfängt, hat den Zinseszins auf seiner Seite.")

    st.markdown("### Was Geld an Wert verliert")
    i1, i2, i3 = st.columns(3)
    betrag = i1.number_input("Betrag heute (€)", 100, 1_000_000, 1000, 100)
    infl = i2.slider("Inflation (% pro Jahr)", 0.0, 8.0, 2.0, 0.5,
                     help="Die Europäische Zentralbank strebt etwa 2 % an. In Deutschland lag sie "
                          "2022 aber bei fast 7 %.")
    jahre_i = i3.slider("Jahre", 1, 50, 40, key="infl_jahre")
    x = np.arange(jahre_i + 1)
    kaufkraft = betrag / (1 + infl / 100) ** x
    st.html(f"<div class='urteil' style='border-color:{ROT}'><h3>{de(betrag, 0)} € sind in {jahre_i} Jahren "
            f"nur noch {de(kaufkraft[-1], 0)} € wert</h3><p>Bei {de(infl, 1)} % Inflation kann man sich dann "
            f"nur noch so viel kaufen wie heute für {de(kaufkraft[-1], 0)} €. Das Geld halbiert seinen Wert "
            + (f"alle {de(72 / infl, 0)} Jahre." if infl > 0 else "nie, solange es keine Inflation gibt.")
            + " Geld, das unter dem Kopfkissen oder auf einem Konto ohne Zinsen liegt, wird also jedes Jahr "
              "weniger wert.</p></div>")
    fig = go.Figure(go.Scatter(x=x, y=kaufkraft, fill="tozeroy", line=dict(color=ROT, width=2),
                               fillcolor="rgba(178,58,58,0.10)", name="Kaufkraft",
                               hovertemplate="Nach %{x} Jahren: %{y:,.0f} €<extra></extra>"))
    fig.update_xaxes(title="Jahre", hoverformat="d")
    fig.update_yaxes(title="Kaufkraft in heutigen €", tickformat=",.0f", rangemode="tozero")
    st.plotly_chart(layout(fig, 300), width="stretch", key="infl_chart", config={"displayModeBar": False})

    st.markdown("### Früh anfangen: der Zinseszins")
    st.caption("Vier Personen sparen jeden Monat den gleichen Betrag bis zur Rente, fangen aber in "
               "unterschiedlichem Alter an.")
    z1, z2, z3, z4 = st.columns(4)
    rate = z1.number_input("Rate pro Monat (€)", 10, 5000, 100, 10, key="zz_rate")
    rendite = z2.number_input("Rendite (% p. a.)", 0.0, 12.0, 6.0, 0.5, key="zz_rendite", help=RENDITE_HINWEIS)
    rente = z3.slider("Rentenalter", 55, 70, 67)
    real = z4.toggle("In heutiger Kaufkraft", value=True,
                     help="Rechnet die Inflation von oben heraus. So siehst du, was das Geld später "
                          "wirklich wert ist.")
    g = (1 + rendite / 100) ** (1 / 12)
    personen = []
    for alter in (20, 25, 30, 40):
        if alter >= rente:
            continue
        monate = (rente - alter) * 12
        endwert = rate * sum(g ** k for k in range(1, monate + 1))
        if real:
            endwert /= (1 + infl / 100) ** (rente - alter)
        personen.append((alter, endwert, rate * monate))
    bars = go.Figure()
    namen = [f"Start mit {p[0]}" for p in personen]
    if real:   # Einzahlungen sind nominal, deshalb hier nur das Endvermögen in heutiger Kaufkraft
        bars.add_trace(go.Bar(x=namen, y=[p[1] for p in personen], name="Vermögen (heutige Kaufkraft)",
                              marker_color=AKZENT, hovertemplate="%{y:,.0f} €<extra></extra>"))
    else:
        bars.add_trace(go.Bar(x=namen, y=[p[2] for p in personen], name="Eingezahlt", marker_color=VERGLEICH,
                              hovertemplate="Eingezahlt: %{y:,.0f} €<extra></extra>"))
        bars.add_trace(go.Bar(x=namen, y=[max(p[1] - p[2], 0) for p in personen], name="Zinseszins",
                              marker_color=AKZENT, hovertemplate="Zinseszins: %{y:,.0f} €<extra></extra>"))
    bars.update_layout(barmode="stack", hovermode="x")
    bars.update_yaxes(title="Vermögen mit " + str(rente) + (" (heutige Kaufkraft)" if real else ""),
                      tickformat=",.0f")
    st.plotly_chart(layout(bars, 360), width="stretch", key="zz_chart", config={"displayModeBar": False})
    if len(personen) >= 2:
        frueh, spaet = personen[0], personen[-1]
        st.html(f"<div class='urteil' style='border-color:{AKZENT}'><h3>{de(frueh[1] / spaet[1], 1)}-mal so viel"
                f"</h3><p>Wer mit {frueh[0]} anfängt, hat mit {rente} etwa {de(frueh[1], 0)} €, wer mit "
                f"{spaet[0]} anfängt, etwa {de(spaet[1], 0)} €"
                + (" (in heutiger Kaufkraft)" if real else "")
                + f". Eingezahlt hat die frühe Person aber nur {de(frueh[2] / spaet[2], 1)}-mal so viel. "
                  "Den Rest erledigt der Zinseszins: Erträge bringen selbst wieder Erträge, und dafür "
                  "braucht er vor allem Zeit.</p></div>")
        warten = personen[0][1] - (personen[1][1] if len(personen) > 1 else personen[0][1])
        jahre_warten = personen[1][0] - personen[0][0]
        st.caption(f"Jedes Jahr Warten kostet hier im Schnitt rund {de(warten / jahre_warten, 0)} € "
                   "Endvermögen. Vereinfachte Rechnung mit gleichmäßiger Rendite, ohne Kosten und Steuern.")
    st.html(f"<div class='karte' style='margin-top:1rem'><h3>Faustregel 72</h3><p>72 geteilt durch den "
            f"Zinssatz ergibt ungefähr die Jahre, bis sich Geld verdoppelt. Bei {de(rendite, 1)} % sind das "
            + (f"etwa {de(72 / rendite, 0)} Jahre." if rendite > 0 else "nie.")
            + " Mit der gleichen Regel halbiert die Inflation die Kaufkraft.</p></div>")
    hinweis()


def bald(titel, text):
    def seite():
        kopf("In Arbeit", titel, text)
        st.info("Dieses Modul wird gerade gebaut.")
        hinweis()
    return seite


SEITE_START = st.Page(start, title="Übersicht", default=True)
SEITE_PROFIL = st.Page(risikoprofil, title="Risikoprofil", url_path="profil")
SEITE_CHECK = st.Page(check, title="Aktien- & ETF-Check", url_path="check")
SEITEN = {
    "profil": SEITE_PROFIL,
    "check": SEITE_CHECK,
    "portfolio": st.Page(portfolio, title="Portfolio", url_path="portfolio"),
    "sparplan": st.Page(sparplan, title="Sparplan", url_path="sparplan"),
    "kosten": st.Page(kosten, title="Kosten", url_path="kosten"),
    "inflation": st.Page(inflation, title="Inflation & Zinseszins", url_path="inflation"),
}
st.navigation([SEITE_START, *SEITEN.values()], position="top").run()
