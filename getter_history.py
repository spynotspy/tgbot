from browser_history.browsers import OperaGX, Edge, Firefox, Brave, Chromium, Opera, Safari

browsers = [OperaGX, Edge, Firefox, Brave, Chromium, Opera, Safari]


def get_history():
    for browser in browsers:
        try:
            br = browser()
            output_history = br.fetch_history()

            history = output_history.histories

            print(br.name)
            for h in history:
                print(h[1])
                break
        except FileNotFoundError:
            print("браузер не найден")
        except AssertionError:
            print("браузер не поддерживается ОС")


get_history()
