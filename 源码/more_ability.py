#原始点位数据转换模块
def old_to_new(data_path):
    with open(data_path, 'r') as file:
        points={}
        line=file.readlines()
        i=0
        point_number=1
        while i < len(line):
            line[i]=line[i].strip()
            #获取position中的x与y坐标
            if line[i] == 'position:':
                for j in range (i+1,i+3):
                    name,value=line[j].strip().split(':')
                    points[f'{name}{point_number}']=value.strip()
            #获取orientation中的z与w坐标
            elif line[i] == 'orientation:':
                for j in range (i+3,i+5):
                    name,value=line[j].strip().split(':')
                    points[f'{name}{point_number}']=value.strip()
                point_number+=1
            i+=1
    return points

#新点位数据写入模块
def write_new_data(new_data,save_path):
    point_number=1
    with open(save_path,'w',encoding='utf-8') as file:
        while point_number <len(new_data)/4+1:
            file.write('('+new_data[f'x{point_number}']+','
                        +new_data[f'y{point_number}']+','
                        +new_data[f'z{point_number}']+','
                        +new_data[f'w{point_number}']+')')
            point_number+=1

#清空指定文件内的所有内容/初始化文件
def data_init(data_path):
    with open(data_path,'w') as file:
        file.write(' ')
