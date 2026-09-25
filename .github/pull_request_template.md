## Что изменено

Коротко опишите изменение.

## Научная проверка

- [ ] есть correctness test;
- [ ] результат сверялся с baseline/oracle, если менялся solver;
- [ ] benchmark не выдаётся за математическое доказательство;
- [ ] обновлён CHANGELOG, если изменение заметно пользователю.

## Перед PR

- [ ] `python -m unittest discover -s tests -v`
- [ ] `python -m unittest discover -s property_tests -v`
- [ ] `pnp-lab doctor`
- [ ] `ruff check pnp_lab tests property_tests`
