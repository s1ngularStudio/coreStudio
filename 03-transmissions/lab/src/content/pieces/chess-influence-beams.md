---
title: Chess Influence Beams
date: 2026-09-04
tags: [chess, generative, live-stream]
builtWith: [py5, python-chess]
summary: >
  A live layer on the chess move poster — every piece fires a beam at
  everything it attacks, and a beam that hits another piece bends once
  instead of stopping, like light catching an edge.
---

Part of the chess/music sync poster project. Every piece's line of sight
becomes a drawn beam; a hit on a pawn reflects the beam back one square, a
hit on anything else redirects it toward whichever of that piece's own
lines reaches farthest.
