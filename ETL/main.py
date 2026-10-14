from extract.extract_main import main as extract_main
from transfrom.transform_main import main as transform_main
from load.load_main import main as load_main

def main():
    #@@ 예외처리를 raise해서 최상단인 main에서 할 것인지 아니면
    #@@ 각 파일에서 할 것인지에 대한 전략 필요 
    checkpoint_extract = extract_main()

    if checkpoint_extract:
        checkpoint_tramsform = transform_main()

        if checkpoint_tramsform:
            load_main()



if __name__ == "__main__":
    main()