from extract.auto_collector import collect
from extract.main import extract as extract_main
from transform.transform_main import main as transform_main
from load.load_main import main as load_main


def main():
    while True:
        collect()

        # Extract
        if not extract_main():
            print("Extract에서 오류 발생 : ETL 종료")
            return

        # Transform
        if not transform_main():
            print("Transform에서 오류 발생 : ETL 종료")
            return

        # Load
        try:
            load_main()
        except Exception as error:
            print(f"Load에서 오류 발생 : {error}")
            return

if __name__ == "__main__":
    main()