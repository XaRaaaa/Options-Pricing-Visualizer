"""Monte Carlo pricing routines using JAX.

This module keeps the simulation memory-light for CPU-only deployments
by evaluating paths in fixed-size JAX batches and aggregating the
statistics on the host. That avoids materializing very large path
arrays while still keeping the core payoff calculation JIT-compiled.
"""

from functools import partial
from math import sqrt

import jax
import jax.numpy as jnp

DEFAULT_BATCH_SIZE = 8192


@partial(jax.jit, static_argnames=("option_type", "antithetic", "batch_size"))
def _batch_payoff_stats(
    key: jax.Array,
    spot: float,
    strike: float,
    rate: float,
    vol: float,
    time: float,
    dividend: float,
    option_type: str,
    antithetic: bool,
    batch_size: int,
) -> tuple[jax.Array, jax.Array]:
    """Return discounted payoff sum and squared sum for one batch."""
    spot = jnp.asarray(spot, dtype=jnp.float32)
    strike = jnp.asarray(strike, dtype=jnp.float32)
    rate = jnp.asarray(rate, dtype=jnp.float32)
    vol = jnp.asarray(vol, dtype=jnp.float32)
    time = jnp.asarray(time, dtype=jnp.float32)
    dividend = jnp.asarray(dividend, dtype=jnp.float32)

    sqrt_t = jnp.sqrt(jnp.maximum(time, 1e-12))
    mu = (rate - dividend - 0.5 * vol * vol) * time
    disc = jnp.exp(-rate * time)

    if antithetic:
        half = batch_size // 2
        key1, key2 = jax.random.split(key)
        z_half = jax.random.normal(key1, shape=(half,), dtype=jnp.float32)
        z = jnp.concatenate([z_half, -z_half])
        if batch_size % 2:
            extra = jax.random.normal(key2, shape=(1,), dtype=jnp.float32)
            z = jnp.concatenate([z, extra])
    else:
        z = jax.random.normal(key, shape=(batch_size,), dtype=jnp.float32)

    terminal_spot = spot * jnp.exp(mu + vol * sqrt_t * z)
    if option_type == "call":
        payoffs = jnp.maximum(terminal_spot - strike, 0.0)
    else:
        payoffs = jnp.maximum(strike - terminal_spot, 0.0)

    discounted = disc * payoffs
    return jnp.sum(discounted), jnp.sum(discounted * discounted)


def monte_carlo_price(
    spot: float,
    strike: float,
    rate: float,
    vol: float,
    time: float,
    dividend: float,
    option_type: str = "call",
    num_paths: int = 100000,
    seed: int = 0,
    antithetic: bool = True,
) -> dict[str, object]:
    """Estimate the European option price by Monte Carlo under GBM.

    Args:
        spot, strike, rate, vol, time, dividend: scalar values.
        option_type: 'call' or 'put'.
        num_paths: Number of Monte Carlo samples.
        seed: PRNG seed.
        antithetic: Use antithetic variates to reduce variance.

    Returns:
        Dict with keys 'price' (JAX scalar), 'stderr' (JAX scalar),
        and 'num_paths' (int).
    """
    num_paths = int(num_paths)
    if num_paths <= 0:
        raise ValueError("num_paths must be > 0")

    if option_type not in {"call", "put"}:
        raise ValueError("option_type must be 'call' or 'put'")

    key = jax.random.PRNGKey(int(seed))
    remaining = num_paths
    total_sum = 0.0
    total_sum_sq = 0.0
    sampled = 0

    while remaining > 0:
        batch_size = min(DEFAULT_BATCH_SIZE, remaining)
        key, batch_key = jax.random.split(key)
        batch_sum, batch_sum_sq = _batch_payoff_stats(
            batch_key,
            spot,
            strike,
            rate,
            vol,
            time,
            dividend,
            option_type=option_type,
            antithetic=antithetic,
            batch_size=batch_size,
        )

        total_sum += float(batch_sum)
        total_sum_sq += float(batch_sum_sq)
        sampled += batch_size
        remaining -= batch_size

    mean = total_sum / sampled
    if sampled > 1:
        variance = max((total_sum_sq - sampled * mean * mean) / (sampled - 1), 0.0)
    else:
        variance = 0.0

    stderr = sqrt(variance / sampled)
    return {
        "price": jnp.asarray(mean, dtype=jnp.float32),
        "stderr": jnp.asarray(stderr, dtype=jnp.float32),
        "num_paths": sampled,
    }