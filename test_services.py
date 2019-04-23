import pytest
import model
import repository
import services


class FakeRepository(repository.AbstractRepository):

    @staticmethod
    def for_batch(ref, sku, qty, eta=None):
        return FakeRepository([
            model.Batch(ref, sku, qty, eta),
        ])

    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, batch):
        self._batches.add(batch)

    def get(self, reference):
        return next(b for b in self._batches if b.reference == reference)

    def list(self):
        return list(self._batches)


class FakeSession():
    committed = False

    def commit(self):
        self.committed = True


def test_add_batch():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch('b1', 'CRUNCHY-ARMCHAIR', 100, None, repo, session)
    assert repo.get('b1') is not None
    assert session.committed


def test_returns_allocation():
    repo = FakeRepository.for_batch("batch1", "COMPLICATED-LAMP", 100, eta=None)
    result = services.allocate("o1", "COMPLICATED-LAMP", 10, repo, FakeSession())
    assert result == "batch1"


def test_error_for_invalid_sku():
    repo = FakeRepository.for_batch('b1', 'AREALSKU', 100, eta=None)
    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, repo, FakeSession())


def test_commits():
    repo = FakeRepository.for_batch("b1", "OMINOUS-MIRROR", 100, eta=None)
    session = FakeSession()
    services.allocate("o1", "OMINOUS-MIRROR", 10, repo, session)
    assert session.committed is True