## Getting Started
### Installation (Ubuntu 20.04 & CUDA 11.3 기준)

1. Clone this repository.

    ~~~
    git clone https://github.com/YueLiao/PPDM.git
    ~~~
2. Install pytorch 1.11.0

    ~~~
    pip install torch==1.11.0+cu113 torchvision==0.12.0+cu113 torchaudio==0.11.0 --extra-index-url https://download.pytorch.org/whl/cu113
    ~~~
3. Install the requirements.
    
    ~~~
    cd PPDM
    pip install -r requirements.txt
    ~~~
4. Compile deformable convolutional.

    ~~~
    cd $PPDM_ROOT/src/lib/models/networks
    rm -rf DCNv2
    git clone https://github.com/jinfagang/DCNv2_latest.git
    mv DCNv2_latest DCNv2
    cd DCNv2
    python3 setup.py build develop
    ~~~

4. Compile deformable convolutional.

    ~~~
    cd $PPDM_ROOT/src/lib/models/networks
    rm -rf DCNv2
    git clone https://github.com/jinfagang/DCNv2_latest.git
    mv DCNv2_latest DCNv2
    cd DCNv2
    python3 setup.py build develop
    ~~~

## Dataset Preperation

제론테크 annotation 포맷에서 모델 학습이 가능한 HOIA 포맷으로의 변환 필요
HOIA 포맷에 대한 자세한 정보는 HOIA포맷.docx 참고 요망
제론테크의 HOI 이미지와 annotation으로 PPDM repo 내부 Dataset 폴더를 아래와 같이 구성함

Organize them in Dataset folder as follows (before conversion):
    ~~~
    |-- Dataset/
    |   |-- <hoia>/
    |       |-- images
    |           |-- train2015
    |           |-- test2015
    |       |-- annotations
    |           |-- train
    |           |-- test
    ~~~

zeron2hoia.py에서 ROOT 변수를 hoia 폴더 path string으로 설정 후 실행 (zeron2hoia.py가 위치한 경로에서 실행)

Organize them in Dataset folder as follows (after conversion):
    ~~~
    |-- Dataset/
    |   |-- <hoia>/
    |       |-- images
    |           |-- train2015
    |           |-- test2015
    |       |-- annotations
    |           |-- train
    |           |-- test
    |           |-- train_hoia.json
    |           |-- test_hoia.json
    |           |-- corre_hoia.npy
    ~~~

## Train and Test

### Train
1. https://drive.google.com/file/d/18Q3fzzAsha_3Qid6mn4jcIFPeOGUaj1d/edit 에서 CenterNet pretrained 모델 가중치 다운로드 받은 뒤, $PPDM_ROOT/models 경로에 붙혀넣기
2. PARAMTER세팅.docx에서 Train 파트 진행 후 아래 command 입력하여 실행
command:
~~~
cd $PPDM_ROOT/src
python main.py  Hoidet --batch_size 112 --master_batch 7 --lr 4.5e-4 --gpus 2,3,4,5  --num_workers 16  --load_model ../models/ctdet_coco_dla_2x.pth --image_dir images/train2015 --dataset hoia --exp_id hoidet_hoia_final
~~~
(Pretrained 모델 설치 실패시 PARAMTER세팅.docx 참조 요망)

### Test
1. PARAMTER세팅.docx에서 Test 파트 진행 후 아래 command 입력하여 실행 (exp_id와 load_model의 중간 경로가 동일해야함)
2. command:
~~~
cd $PPDM_ROOT/src
python test_hoi.py Hoidet --exp_id hoidet_hoia_final --load_model ../exp/Hoidet/hoidet_hoia_final/model_last.pth --gpus 0 --dataset hoia --image_dir images/test2015 --test_with_eval
~~~