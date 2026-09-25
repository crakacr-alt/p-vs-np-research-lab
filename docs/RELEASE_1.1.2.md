# Release 1.1.2 — research quality

Версия 1.1.2 не меняет математический алгоритм solver-ов. Она улучшает процесс
проверки и публикации лаборатории.

Добавлено:

- CodeQL для Python;
- Dependabot для Python dependencies и GitHub Actions;
- CODEOWNERS;
- шаблон PR и отдельный issue для correctness bugs;
- универсальный release checklist;
- автоматическая сборка wheel/sdist по tag;
- проверка совпадения tag и package version.

Также CI переведён на актуальные official GitHub Actions, package job запускает
`pip check`, а README очищен от артефакта форматирования.

Научный статус не изменился: проект не является доказательством P=NP или P!=NP.
