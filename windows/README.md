# PC5 Launcher для Windows 11

Порт запускается как обычное приложение: окно с родным интерфейсом PC5 Launcher (из `app/web`), библиотека игр
Steam / Epic / GOG и свои `.exe`, управление геймпадом (XInput) и клавиатурой.

## Установка

Скачайте из **Actions → Windows build → Artifacts** (или из **Releases**, если сборка шла по тегу):

* `PC5Launcher-Setup-<версия>.exe` — установщик (в профиль пользователя, права администратора не нужны);
* `PC5Launcher-<версия>-windows-x64-portable.zip` — распаковать и запустить `PC5Launcher.exe`.

Нужен Microsoft Edge WebView2 Runtime — в Windows 11 он уже есть.

## Как собрать через GitHub Actions

1. Залейте репозиторий на GitHub (папка `.github/workflows/windows.yml` уже в нём).
2. Любой push в `main`/`master`, pull request или ручной запуск (**Actions → Windows build → Run workflow**) собирает приложение.
3. Релиз: `git tag v0.3.3 && git push origin v0.3.3` — установщик и zip появятся в **Releases**.

Версия берётся из файла `VERSION`.

## Локальная сборка (Windows, Python 3.12)

```powershell
python -m pip install -r windows\requirements-build.txt
powershell -ExecutionPolicy Bypass -File windows\build.ps1
```

Запуск из исходников: `python windows\run_pc5.py` (добавьте `--fullscreen` для полного экрана).

## Управление

| Геймпад | Клавиатура |
|---|---|
| Крестовина / левый стик | Стрелки |
| A / B / X / Y | Enter или Пробел / Esc / X / Y |
| LB / RB, LT / RT | Q / E, 1 / 3 |
| Start | O |
| Правый стик вверх/вниз | PageUp / PageDown |
| Back + Start (1,2 с) — на главный экран | Home |
| — | F11 — полный экран |

Геймпад реагирует только пока окно лаунчера на переднем плане.

## Что работает, а что нет (честно)

Работает: главный экран, библиотека (Steam, Epic, GOG, свои `.exe`), запуск и определение «игра идёт», время в игре,
избранное, скрытие, переименование, обложки Steam, темы, настройки интерфейса, меню питания (сон, выключение,
перезагрузка), файловый обозреватель и «Добавить в библиотеку», язык English / Deutsch.

Не портировано, потому что это Linux-механика и в Windows она не нужна или невозможна: Gamescope, Proton / FSR 4 /
OptiScaler, Flatpak-эмуляторы, установка из архивов через Proton, Bluetooth/Wi-Fi/звук через PipeWire/NetworkManager,
Control Center (оверлей поверх игры), экранная клавиатура, магазины внутри лаунчера. Эти разделы показывают пустые
списки; в Windows игры ставятся родными лаунчерами.

Данные хранятся в `%APPDATA%\PC5Launcher` (настройки, библиотека, лог `pc5launcher.log`, свои темы в `themes\`).

## Устройство

```
windows/pc5win/server.py    локальный сервер 127.0.0.1 (токен, проверка Host), отдаёт app/web и RPC
windows/pc5win/shim.js      имитирует мост WebKitGTK (window.webkit.messageHandlers.couch) через HTTP
windows/pc5win/backend.py   RPC-методы с теми же именами и формами ответов, что у Linux-ядра
windows/pc5win/sources.py   Steam / Epic / GOG
windows/pc5win/pad.py       XInput -> события «pad»
windows/pc5win/app.py       окно WebView2 (pywebview), одиночный экземпляр, --selftest для CI
```

Интерфейс в `app/web` не менялся. Лицензия — GPL-3.0, как у оригинала.
