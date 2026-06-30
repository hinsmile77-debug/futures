import time
import pyautogui
import keyboard
import pyperclip

saved_points = []
last_saved = None

print("=" * 70)
print("          Mouse Position Tool  v2.0")
print("=" * 70)
print(" F8   : (x, y) 복사")
print(" F9   : x, y 복사")
print(" F10  : pyautogui.click(x, y) 복사")
print(" F11  : 현재 좌표 저장")
print(" F12  : 저장된 좌표를 Python 코드로 복사")
print(" DEL  : 저장 좌표 모두 삭제")
print(" ESC  : 종료")
print("=" * 70)

last_xy = (-1, -1)


def wait_release(key):
    while keyboard.is_pressed(key):
        time.sleep(0.05)


while True:

    if keyboard.is_pressed("esc"):
        print("\n프로그램 종료")
        break

    x, y = pyautogui.position()

    if (x, y) != last_xy:
        print(
            f"\r현재 위치 : ({x:5d}, {y:5d})    저장:{len(saved_points):3d}",
            end="",
            flush=True,
        )
        last_xy = (x, y)

    # ----------------------------------------------------
    # F8
    # ----------------------------------------------------
    if keyboard.is_pressed("F8"):
        text = f"({x}, {y})"
        pyperclip.copy(text)
        print(f"\n복사 완료 : {text}")
        wait_release("F8")

    # ----------------------------------------------------
    # F9
    # ----------------------------------------------------
    if keyboard.is_pressed("F9"):
        text = f"{x}, {y}"
        pyperclip.copy(text)
        print(f"\n복사 완료 : {text}")
        wait_release("F9")

    # ----------------------------------------------------
    # F10
    # ----------------------------------------------------
    if keyboard.is_pressed("F10"):
        text = f"pyautogui.click({x}, {y})"
        pyperclip.copy(text)
        print(f"\n복사 완료")
        print(text)
        wait_release("F10")

    # ----------------------------------------------------
    # F11
    # ----------------------------------------------------
    if keyboard.is_pressed("F11"):

        if last_saved != (x, y):
            saved_points.append((x, y))
            last_saved = (x, y)
            print(f"\n좌표 저장 ({len(saved_points)}개) : ({x}, {y})")

        wait_release("F11")

    # ----------------------------------------------------
    # F12
    # ----------------------------------------------------
    if keyboard.is_pressed("F12"):

        if len(saved_points) == 0:
            print("\n저장된 좌표가 없습니다.")
        else:

            code = [
                "import pyautogui",
                "import time",
                "",
            ]

            for i, (sx, sy) in enumerate(saved_points, 1):
                code.append(f"# Point {i}")
                code.append(f"pyautogui.click({sx}, {sy})")
                code.append("time.sleep(0.3)")
                code.append("")

            text = "\n".join(code)

            pyperclip.copy(text)

            print(f"\nPython 코드 복사 완료 ({len(saved_points)}개 좌표)")

        wait_release("F12")

    # ----------------------------------------------------
    # DEL
    # ----------------------------------------------------
    if keyboard.is_pressed("delete"):
        saved_points.clear()
        last_saved = None
        print("\n저장 좌표 삭제 완료")
        wait_release("delete")

    time.sleep(0.01)