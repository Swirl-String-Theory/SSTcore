# BEMv19 Route-B integration plan for links

BEMv19 parses multi-component link geometry but does not yet claim a full R--T BEM link result.

## Required operator upgrade

For a link with components \(C_1,\ldots,C_m\), replace the single boundary map by a block boundary operator:

\[
\Lambda^{\rm link}_{R/T}
=
\begin{pmatrix}
\Lambda_{11} & \Lambda_{12} & \cdots \\
\Lambda_{21} & \Lambda_{22} & \cdots \\
\vdots & \vdots & \ddots
\end{pmatrix}_{R/T}.
\]

Diagonal blocks encode self-boundary response. Off-diagonal blocks encode inter-component R--T coupling.

## Link-specific correction

A first link-aware Route-B correction should separate:

\[
\Delta F_{\rm pair}^{\rm link}
=
\Delta F_{\rm self}
+
\Delta F_{\rm cross}.
\]

The cross term should be tested against Gauss linking estimates and component separation diagnostics.

## Parsed link IDs


## Status

\[
\boxed{\text{BEMv19 status: geometry parser ready; block R--T operator still open.}}
\]