import glob
import tqdm
import json
import numpy as np
import os

def get_hoiinfo(folder_path):
    
    filepaths = glob.glob(folder_path + '/*.json')

    actual_hoi_dict = {}
    
    print('\n')
    print('-----getting hoi list-----')
    print('\n')
    
    object_list = []
    action_list = []
    # action_list.append('no_interaction')
    no_interaction_object_list = []
    remove_list = []

    for i, filepath in enumerate(tqdm.tqdm(filepaths)):
        # print('filepath: ', filepath)
        with open(filepath, 'r') as jsonfile:
            data = json.load(jsonfile)
        
        if not i:
            # class_categories_dict = {}
            # action_categories_dict = {}
            # for x in data['Categories']:
            #     class_categories_dict[x['id']] = x['name']
            # for x in data['action_categories']:
            #     action_categories_dict[x['id']] = x['name']
            # # class_categories_dict = {x['id'] : x['name'] for x in data['Categories']}
            # # action_categories_dict = {x['id'] : x['name'] for x in data['action_categories']}
            # # U:/hoi
            filepath_temp = 'utils/zeron_category_sample.json'
            # # filepath_temp = '/gpfs/dave/HOTR/zeron/annotations/train/VID_0059706_person(person).json'
            with open(filepath_temp, 'r') as jsonfile_temp:
                data_temp = json.load(jsonfile_temp)
                
            class_categories_dict = {x['id'] : x['name'] for x in data_temp['Categories']}
            action_categories_dict = {x['id'] : x['name'] for x in data_temp['action_categories']}
            
            for x in data['Categories']:
                class_categories_dict[x['id']] = x['name']
            for x in data['action_categories']:
                action_categories_dict[x['id']] = x['name']
            
        else:
            for x in data['Categories']:
                class_categories_dict[x['id']] = x['name']
            for x in data['action_categories']:
                action_categories_dict[x['id']] = x['name']
        
        for annotation in data['annotations']:
            # if class_categories_dict[annotation['category_id']] == "doll" or class_categories_dict[annotation['category_id']] == "person":
            #     pass
            # else:
            #     print('category_id: ', annotation['category_id'])
            #     print('class categories dict: ', class_categories_dict)
            #     print('annotation object:', class_categories_dict[annotation['category_id']])
                # print('file path: ', filepath)
                
            try:
                temp_object_id = class_categories_dict[annotation['category_id']]
            except:
                class_categories_dict = {annotation['category_id'] : 'unknown'}
                remove_list.append(filepath)
                                      
                
            # print('class_categories_dict: ', class_categories_dict)
            if class_categories_dict[annotation['category_id']] not in object_list:
                object_list.append(class_categories_dict[annotation['category_id']])
                actual_hoi_dict[class_categories_dict[annotation['category_id']]] = [] #['no_interaction']
        
        for action in data['actions']:
            if isinstance(action['object'], int):
                try:
                    # print('action object: ', class_categories_dict[action['object']])
                    # print('action name: ', action_categories_dict[action['name']])
                    action['object'] = class_categories_dict[action['object']]
                    action['name'] = action_categories_dict[action['name']]
                except:
                    print(action)
                    print(data['images'])
                    remove_list.append(filepath)
                
            if action['name'] == 'no_interaction':
                no_interaction_object_list.append(action['object'])
                
            if not actual_hoi_dict.get(action['object'], None):
                actual_hoi_dict[action['object']] = [action['name']]
                # action_list.append(action['name'])
            else:
                if action['name'] in actual_hoi_dict[action['object']]:
                    continue
                else:
                    # actual_hoi_dict[action['object']] = sorted(actual_hoi_dict[action['object']] +[action['name']])
                    actual_hoi_dict[action['object']] = actual_hoi_dict[action['object']] +[action['name']]
            
            if action['name'] not in action_list:
                action_list.append(action['name'])
    
    # actual_hoi_dict = dict(sorted(actual_hoi_dict.items(), key=lambda item: item[1], reverse = True))
    
    with open('remove_list.txt', 'w') as f:
        for line in remove_list:
            f.write(f"{line}\n")
    
    print('actual_hoi_dict: ', actual_hoi_dict)
    
    cnt = 1
    action_index = 0
    hoi_list = []
    # object_list = sorted(object_list)
    # action_list = sorted(action_list)
    
    actual_class_categories_dict = {i + 1: x for i, x in enumerate(object_list)}
    actual_action_categories_dict = {i + 1: x for i, x in enumerate(action_list)}
    
    mask_true_index = [] 
    
    print('\n')
    print('object_list: ', object_list)
    print('\n')
    print('number of objects: ', len(object_list))
    print('\n')
    print('action_list: ', action_list)
    print('\n')
    print('number of actions: ', len(action_list))
    
    print('\n')
    print('class_categories_dict: ', class_categories_dict)
    print('\n')
    print('action_categories_dict: ', action_categories_dict)
    print('\n')
    print('actual_class_categories_dict: ', actual_class_categories_dict)
    print('\n')
    print('actual_action_categories_dict: ', actual_action_categories_dict)
    print('\n')
    
    for ii, (key, values) in enumerate(actual_hoi_dict.items()):
        for value in values:
            # action_list.append(str(value))
            hoi_list.append([cnt, key, value])
            if value == 'no_interaction':
                if key in no_interaction_object_list:
                    mask_true_index.append((action_list.index(value), object_list.index(key)))
            else:
                mask_true_index.append((action_list.index(value), object_list.index(key)))
            
            cnt += 1
            
    print('hoi_list: ', hoi_list)
    print('number of hois: ', len(hoi_list))

    return hoi_list, action_list, object_list, class_categories_dict, action_categories_dict, mask_true_index, actual_class_categories_dict, actual_action_categories_dict

def save_actionlist(action_list, root_path):
    actionlines = [[str(i+1).zfill(3) + '\t', x + '\n'] for i, x in enumerate(action_list)]
    actionlines.insert(0, ['---------------------------------------------------\n'])
    actionlines.insert(0, ['id\t', 'verb\n'])
    
    save_path = root_path + '/' + 'list_action.txt'
    
    try:
        os.remove(save_path)
        print('\n')
        print("% s removed successfully" % save_path)
        print('\n')
    except OSError as error:
        # print(error)
        print('\n')
        print("same path does not exist!")
        print('\n')
    
    with open(save_path, 'a') as f:
        for line in actionlines:
            f.writelines(line)
    f.close()

def create_correinfo(action_list, object_list, mask_index, root_path):
    n, m = len(action_list), len(object_list)
    mat = np.zeros((n,m))
    
    
    for (x, y) in mask_index:
        mat[x,y] = 1
    
    print('x-axis(object): ', object_list)
    print('y-axis(action): ', action_list)
    
    print('x-axis length: ', len(object_list))
    print('y-axis length: ', len(action_list))
    
    # mat = mat[:,1:]
    
    print('corre matrix: ', mat)
    
    
    np.save(root_path + '/' + 'corre_hoia.npy', mat)
    
# def get_categoryinfo(category_list):
#     return {x['id'] : x['name'] for x in category_list}
    