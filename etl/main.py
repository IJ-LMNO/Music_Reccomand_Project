from extract.auto_collector import collect
from extract.main import extract
from etl.transform.main import transform
from etl.load.main import load


def main():
    while True:
        collect()

        # Extract
        if not extract():
            print("Extract에서 오류 발생 : ETL 종료")
            return

        # Transform
        if not transform():
            print("Transform에서 오류 발생 : ETL 종료")
            return

        # Load
        try:
            load()
        except Exception as error:
            print(f"Load에서 오류 발생 : {error}")
            return

if __name__ == "__main__":
    main()