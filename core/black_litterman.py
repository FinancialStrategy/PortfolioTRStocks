# core/black_litterman.py

from __future__ import annotations

import numpy as np
import pandas as pd


class BlackLittermanModel:
    """
    Simplified Black-Litterman model with confidence-weighted views.
    """

    def __init__(
        self,
        cov_matrix: pd.DataFrame,
        market_weights: np.ndarray,
        risk_aversion: float = 2.5,
        tau: float = 0.05,
    ):
        self.cov = cov_matrix.copy()
        self.market_weights = np.asarray(market_weights, dtype=float)
        self.risk_aversion = risk_aversion
        self.tau = tau

    def equilibrium_returns(self) -> pd.Series:
        pi = self.risk_aversion * self.cov.values @ self.market_weights
        return pd.Series(pi, index=self.cov.index, name="Pi")

    def build_omega(self, P: np.ndarray, confidences: np.ndarray) -> np.ndarray:
        base = np.diag(np.diag(P @ (self.tau * self.cov.values) @ P.T))
        conf = np.clip(confidences, 1e-4, 0.9999)
        scale = (1.0 - conf) / conf
        omega = np.diag(np.diag(base) * scale)
        return omega

    def posterior(self, P: np.ndarray, Q: np.ndarray, confidences: np.ndarray):
        Sigma = self.cov.values
        Pi = self.equilibrium_returns().values.reshape(-1, 1)

        P = np.asarray(P, dtype=float)
        Q = np.asarray(Q, dtype=float).reshape(-1, 1)
        confidences = np.asarray(confidences, dtype=float)

        Omega = self.build_omega(P, confidences)

        tauSigma_inv = np.linalg.inv(self.tau * Sigma)
        Omega_inv = np.linalg.inv(Omega)

        middle = np.linalg.inv(tauSigma_inv + P.T @ Omega_inv @ P)
        mu_bl = middle @ (tauSigma_inv @ Pi + P.T @ Omega_inv @ Q)
        sigma_bl = Sigma + middle

        return {
            "posterior_returns": pd.Series(mu_bl.flatten(), index=self.cov.index),
            "posterior_cov": pd.DataFrame(sigma_bl, index=self.cov.index, columns=self.cov.columns),
        }
