import numpy as np

from federated_coordinator.model import LinearModel


def test_fit_reduces_error() -> None:
    rng = np.random.default_rng(0)
    x = rng.normal(size=(200, 4))
    y = x @ np.array([1.0, -2.0, 0.5, 3.0]) + 5.0
    model = LinearModel(n_features=4, learning_rate=0.1)
    before = model.evaluate(x, y)["mse"]
    model.fit(x, y, epochs=200)
    after = model.evaluate(x, y)["mse"]
    assert after < before * 0.1


def test_parameter_roundtrip() -> None:
    model = LinearModel(n_features=4)
    model.weights = np.array([1.0, 2.0, 3.0, 4.0])
    model.bias = 7.0
    params = model.get_parameters()
    restored = LinearModel(n_features=4)
    restored.set_parameters(params)
    assert np.allclose(restored.weights, model.weights)
    assert restored.bias == model.bias
