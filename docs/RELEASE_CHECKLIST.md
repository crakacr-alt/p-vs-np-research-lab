# Release checklist

Этот список используется для каждой версии.

## Версия и документы

- [ ] номер версии обновлён в `pyproject.toml`;
- [ ] `pnp_lab.__version__` совпадает с package metadata;
- [ ] README показывает текущую версию;
- [ ] `CITATION.cff` обновлён;
- [ ] `CHANGELOG.md` содержит отдельную запись;
- [ ] есть `docs/RELEASE_<version>.md`.

## Корректность

- [ ] `python -m unittest discover -s tests -v`;
- [ ] `python -m unittest discover -s property_tests -v`;
- [ ] `pnp-lab doctor`;
- [ ] differential verification проходит;
- [ ] для изменения solver/representation есть отдельный correctness test;
- [ ] сильное научное утверждение не основано только на benchmark.

## Упаковка

- [ ] `python -m build`;
- [ ] `python -m twine check dist/*`;
- [ ] wheel ставится в чистое окружение;
- [ ] `python -m pip check` проходит.

## GitHub

- [ ] PR зелёный;
- [ ] CodeQL зелёный;
- [ ] PR слит в `main`;
- [ ] зелёный post-merge CI;
- [ ] только после этого создан tag `vX.Y.Z`.
