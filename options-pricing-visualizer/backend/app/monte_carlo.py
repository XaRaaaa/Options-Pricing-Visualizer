"""Monte Carlo pricing routines using JAX.

Provides a simple, vectorized Monte Carlo estimator for European
call/put options. Uses antithetic variates when requested to reduce
variance and returns a price plus a standard error estimate.
"""
from typing import Dict

import jax
import jax.numpy as jnp


def monte_carlo_price(
    spot: jnp.ndarray,
    strike: jnp.ndarray,
    rate: jnp.ndarray,
    vol: jnp.ndarray,
    time: jnp.ndarray,
    dividend: jnp.ndarray,
    option_type: str = "call",
    num_paths: int = 100000,
    seed: int = 0,
    antithetic: bool = True,
) -> Dict[str, object]:
    """Estimate the European option price by Monte Carlo under GBM.

    Args:
        spot, strike, rate, vol, time, dividend: scalar JAX arrays or values.
        option_type: 'call' or 'put'.
        num_paths: Number of Monte Carlo samples (will be coerced to int).
        seed: PRNG seed.
        antithetic: Use antithetic variates to reduce variance.

    Returns:
        Dict with keys 'price' (JAX scalar), 'stderr' (JAX scalar),
        and 'num_paths' (int).
    """
    # Coerce to JAX arrays/scalars
    spot = jnp.array(spot)
    strike = jnp.array(strike)
    rate = jnp.array(rate)
    vol = jnp.array(vol)
    time = jnp.array(time)
    dividend = jnp.array(dividend)

    num_paths = int(num_paths)
    if num_paths <= 0:
        raise ValueError("num_paths must be > 0")

    key = jax.random.PRNGKey(int(seed))

    # Use closed-form GBM terminal distribution; no time-stepping required.
    sqrt_t = jnp.sqrt(jnp.maximum(time, 1e-12))
    mu = (rate - dividend - 0.5 * vol * vol) * time

    if antithetic:
        half = max(1, num_paths // 2)
        key1, key2 = jax.random.split(key)
        z_half = jax.random.normal(key1, shape=(half,))
        z = jnp.concatenate([z_half, -z_half])
        if z.shape[0] < num_paths:
            extra = jax.random.normal(key2, shape=(num_paths - z.shape[0],))
            z = jnp.concatenate([z, extra])
    else:
        key1, _ = jax.random.split(key)
        z = jax.random.normal(key1, shape=(num_paths,))

    s_t = spot * jnp.exp(mu + vol * sqrt_t * z)

    if option_type == "call":
        payoffs = jnp.maximum(s_t - strike, 0.0)
    else:
        payoffs = jnp.maximum(strike - s_t, 0.0)

    disc = jnp.exp(-rate * time)
    discounted = disc * payoffs

    price_est = jnp.mean(discounted)
    stderr = jnp.std(discounted) / jnp.sqrt(discounted.shape[0])

    return {"price": price_est, "stderr": stderr, "num_paths": int(discounted.shape[0])}
