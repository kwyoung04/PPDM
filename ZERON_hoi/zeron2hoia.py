import json
import pandas as pd
import numpy as np
import glob
import tqdm
import math
from utils.get_info import get_hoiinfo, save_actionlist, create_correinfo
from utils.transform import xywh2xyxy

ROOT = '/gpfs/dave/hoi/dataset/new_data'
DATASET_TYPE = ['train', 'test']

annotations_path = ROOT + '/' + 'annotations'
eps = 1e-7

for ti, t in enumerate(DATASET_TYPE):

    dataset_path = annotations_path + '/' + t + '/'
    
    new_json = []
    
    if not ti:
        hoi_list, action_list, object_list, class_categories_dict, action_categories_dict, mask_index, actual_class_categories_dict, actual_action_categories_dict = get_hoiinfo(dataset_path)
        save_actionlist(action_list, root_path = ROOT)
        create_correinfo(action_list, object_list, mask_index, root_path = annotations_path)
        df_hoi = pd.DataFrame(hoi_list, columns = ['id', 'object', 'verb'])
        

    filepaths = glob.glob(dataset_path + '/*.json')
    
    print('\n')
    print(f'----- processing {t} dataset -----')
    print(f'number of json files: {len(filepaths)}')
    print('\n')

    for i, filepath in enumerate(tqdm.tqdm(filepaths)):
        
        add_flag = True
        
        with open(filepath, "r") as zeron_json:
            zeron_sample = json.load(zeron_json)
        
        new_sample = {}

        new_annotations = []
        for annotation in zeron_sample['annotations']:
            new_annotation = {}
            
            b1, b2, b3, b4 = annotation["bbox"]
            
            new_annotation["bbox"] = xywh2xyxy(annotation["bbox"])
            # if b3 < b1:
            #     new_annotation["bbox"] = xywh2xyxy(annotation["bbox"])
            # else:
            #     new_annotation["bbox"] = annotation["bbox"]
                
            # print('new_annotation_bbox: ', new_annotation["bbox"])
            new_annotation["category_id"] = object_list.index(class_categories_dict[annotation["category_id"]]) + 1
            new_annotations.append(new_annotation)

        new_sample["annotations"] = new_annotations

        file_name = zeron_sample['images'][0]['file_name']

        new_sample["file_name"] = file_name

        hoi_annotations = []
        for action in zeron_sample['actions']:
            
            if isinstance(action['object'], int):
                action['object'] = class_categories_dict[action['object']]
                action['name'] = action_categories_dict[action['name']]
            
            hcx, hcy = action['boxes_h']
            # print('hcx, hcy: ', hcx, hcy)
            ocx, ocy = action['boxes_o']
            # print('ocx, ocy: ', ocx, ocy)
            
            hoi_annotation = {}
            
            action_name = action['name']
            
            hoi_annotation['category_id'] = action_list.index(action_name) + 1
            
            if not hoi_annotation['category_id']:
                raise ValueError(f'{action_name} not in action list!')
            
            hoi_category_id = np.where((df_hoi['object'] == action['object']) & (df_hoi['verb'] == action['name']))[0]
            
            if len(hoi_category_id) > 1:
                raise ValueError('object-action pair duplicates exist!')
            
            # hoi_annotation['hoi_category_id'] = int(hoi_category_id[0]) + 1
            
            for ii, annotation in enumerate(zeron_sample['annotations']): #new_annotations
                if len(annotation['keypoints']) > 0:
                    hoi_annotation['subject_id'] = ii
                    # hoi_annotation['object_id'] = ii
                else:
                    hoi_annotation['object_id'] = ii
                    # hoi_annotation['subject_id'] = ii
                # bx1, by1, bx2, by2 = annotation['bbox']
                
                
                
                # if ocx <= bx2 + eps and ocx >= bx1 - eps \
                #     and ocy <= by2 + eps and ocy >= by1 - eps:
                #         hoi_annotation['object_id'] = ii
                
                # if hcx <= bx2 + eps and hcx >= bx1 - eps \
                #     and hcy <= by2 + eps and hcy >= by1 - eps:
                #         hoi_annotation['subject_id'] = ii
                
            if len(hoi_annotation.keys()) < 3:
                print('\nhoi_annotation: ' , hoi_annotation)
                add_flag = False
                print('number of hoi_annotation keys not enough!\n')
            else:
                hoi_annotations.append(hoi_annotation)

        new_sample["hoi_annotation"] = hoi_annotations

        # new_sample["img_id"] = i + 1
        
        # image = cv2.imread(dataset_path.replace('annotations','image') + file_name)
        # cv2.imshow('temp', image)
        # cv2.waitKey(0)
        # temp_id += 1
        
        if add_flag:
            new_json.append(new_sample)
        else:
            continue
    
    with open(annotations_path + '/' + t + '_' + 'hoia' + '.json', "w") as json_file:
        json.dump(new_json, json_file, indent=4)
